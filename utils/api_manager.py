"""
Módulo para gestión segura de datos con Google Sheets
Versión final fusionada
"""
import streamlit as st
import time
import logging
from typing import Any, List, Dict, Union, Optional, Tuple
from tenacity import retry, wait_exponential, stop_after_attempt, RetryError

logger = logging.getLogger(__name__)

class ApiManager:
    """Gestor de operaciones seguras con Google Sheets API"""

    def __init__(self):
        self.total_calls = 0
        self.error_count = 0
        self.last_call_time = 0
        self.min_call_interval = 0.1  # 100ms entre llamadas
        self.client = None

    def initialize(self) -> Tuple[bool, Optional[str]]:
        """Inicializa el manager y establece conexión"""
        try:
            from google.oauth2 import service_account
            import gspread

            # Debug: verificar qué claves están disponibles en secrets
            available_keys = list(st.secrets.keys()) if st.secrets else []
            
            # Intentar diferentes configuraciones de secrets
            creds_info = None
            
            # Opción 1: Buscar sección gcp_service_account
            if "gcp_service_account" in st.secrets:
                creds_info = dict(st.secrets["gcp_service_account"])
                
            # Opción 2: Usar secrets directamente si tiene las claves necesarias
            elif all(key in st.secrets for key in ["type", "project_id", "private_key", "client_email"]):
                creds_info = dict(st.secrets)
                
            # Opción 3: Buscar otras posibles secciones
            elif "google_service_account" in st.secrets:
                creds_info = dict(st.secrets["google_service_account"])
                
            if not creds_info:
                error_msg = f"No se encontraron credenciales válidas. Claves disponibles: {available_keys}"
                return False, error_msg
            
            # Verificar campos obligatorios
            required_fields = ["type", "project_id", "private_key", "client_email"]
            missing_fields = [field for field in required_fields if field not in creds_info]
            
            if missing_fields:
                return False, f"Campos obligatorios faltantes: {missing_fields}"
            
            # Crear credenciales
            creds = service_account.Credentials.from_service_account_info(
                creds_info,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            
            self.client = gspread.authorize(creds)
            logger.info("Cliente de Google Sheets autorizado y API Manager inicializado correctamente.")
            return True, None
            
        except Exception as e:
            self.client = None
            logger.critical(f"Fallo catastrófico al inicializar la API de Google Sheets: {e}", exc_info=True)
            return False, f"Error inicializando API: {str(e)}"

    def open_sheet(self, sheet_id: str, worksheet_name: str):
        """Abre una hoja de cálculo específica"""
        if not self.client:
            st.error("API Manager no inicializado: client = None")
            return None
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            return spreadsheet.worksheet(worksheet_name)
        except Exception as e:
            st.error(f"Error abriendo hoja {worksheet_name}: {str(e)}")
            return None

    @retry(
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        before_sleep=lambda retry_state: logger.warning(
            f"Reintentando operación de GSheets: {retry_state.fn.__name__}, intento {retry_state.attempt_number}..."
        )
    )
    def safe_sheet_operation(self, func, *args, **kwargs) -> Tuple[Any, Optional[str]]:
        """
        Ejecuta operación segura sobre la API con control de rate limiting y reintentos.
        """
        try:
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time

            if time_since_last_call < self.min_call_interval:
                time.sleep(self.min_call_interval - time_since_last_call)

            self.total_calls += 1
            self.last_call_time = time.time()

            result = func(*args, **kwargs)
            return result, None
        except RetryError as e:
            logger.error(f"La operación de GSheets falló después de varios reintentos: {e}")
            self.error_count += 1
            return None, f"Error en operación API después de reintentos: {str(e)}"
        except Exception as e:
            logger.error(f"Error inesperado en operación de GSheets: {e}", exc_info=True)
            self.error_count += 1
            return None, f"Error en operación API: {str(e)}"

    def get_stats(self) -> Dict[str, Any]:
        """Devuelve estadísticas de uso de la API"""
        return {
            "total_calls": self.total_calls,
            "error_count": self.error_count,
            "last_call_time": self.last_call_time,
            "success_rate": f"{((self.total_calls - self.error_count) / self.total_calls * 100):.1f}%" 
                            if self.total_calls > 0 else "N/A"
        }

    def reset_stats(self):
        """Reinicia estadísticas"""
        self.total_calls = 0
        self.error_count = 0
        self.last_call_time = 0

# Instancia global
api_manager = ApiManager()

# Funciones de utilidad
def batch_update_sheet(worksheet, updates: List[Dict]) -> Tuple[bool, Optional[str]]:
    if not updates:
        return True, None
    try:
        result, error = api_manager.safe_sheet_operation(worksheet.batch_update, updates)
        return result is not None, error
    except Exception as e:
        return False, f"Error en batch_update: {str(e)}"

def append_row(worksheet, row_data: List[Any]) -> Tuple[bool, Optional[str]]:
    try:
        result, error = api_manager.safe_sheet_operation(worksheet.append_row, row_data)
        return result is not None, error
    except Exception as e:
        return False, f"Error append_row: {str(e)}"

def get_all_values(worksheet) -> Tuple[List[List[Any]], Optional[str]]:
    try:
        values, error = api_manager.safe_sheet_operation(worksheet.get_all_values)
        return values or [], error
    except Exception as e:
        return [], f"Error get_all_values: {str(e)}"

def update_cell(worksheet, row: int, col: int, value: Any) -> Tuple[bool, Optional[str]]:
    try:
        result, error = api_manager.safe_sheet_operation(worksheet.update_cell, row, col, value)
        return result is not None, error
    except Exception as e:
        return False, f"Error update_cell: {str(e)}"

def initialize_api() -> bool:
    """Inicializa la API automáticamente al importar"""
    success, error = api_manager.initialize()
    if not success and st.secrets.get("DEBUG_MODE", False):
        st.warning(f"API no inicializada: {error}")
    return success

