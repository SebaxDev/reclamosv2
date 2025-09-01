"""
Módulo para gestión segura de datos con Google Sheets
Versión 3.2 - Con manejo robusto de errores y compatibilidad con API
"""
import streamlit as st
import time
from typing import List, Dict, Union, Optional

class ApiManager:
    """Gestor de operaciones seguras con Google Sheets API"""
    
    def __init__(self):
        self.total_calls = 0
        self.error_count = 0
        self.last_call_time = 0
        self.min_call_interval = 0.1  # 100ms entre llamadas para evitar rate limiting

    def initialize(self):
        """Inicializa el manager y establece conexión"""
        try:
            from google.oauth2 import service_account
            import gspread
            
            # Configuración desde secrets de Streamlit
            creds = service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
            self.client = gspread.authorize(creds)
            return True, None
        except Exception as e:
            return False, f"Error inicializando API: {str(e)}"

    def open_sheet(self, sheet_id: str, worksheet_name: str):
        """
        Abre una hoja de cálculo específica
        
        Args:
            sheet_id: ID de la hoja de Google Sheets
            worksheet_name: Nombre de la worksheet
        
        Returns:
            Worksheet object o None si hay error
        """
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            return spreadsheet.worksheet(worksheet_name)
        except Exception as e:
            st.error(f"Error abriendo hoja {worksheet_name}: {str(e)}")
            return None

    def safe_sheet_operation(self, func, *args, **kwargs) -> Tuple[Any, Optional[str]]:
        """
        Ejecuta una operación segura sobre la API con control de rate limiting
        
        Args:
            func: Función de gspread a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos clave (is_batch para operaciones batch)
        
        Returns:
            Tuple (resultado, mensaje_error)
        """
        try:
            # Control de rate limiting
            current_time = time.time()
            time_since_last_call = current_time - self.last_call_time
            
            if time_since_last_call < self.min_call_interval:
                time.sleep(self.min_call_interval - time_since_last_call)
            
            # Ejecutar operación
            self.total_calls += 1
            self.last_call_time = time.time()
            
            result = func(*args, **kwargs)
            return result, None
            
        except Exception as e:
            self.error_count += 1
            error_msg = f"Error en operación API: {str(e)}"
            
            # Log detallado para debugging
            if st.secrets.get("DEBUG_MODE", False):
                st.error(f"DEBUG: {error_msg}")
                st.error(f"Función: {func.__name__}")
                st.error(f"Args: {args}")
            
            return None, error_msg

    def get_stats(self) -> Dict[str, Any]:
        """Devuelve estadísticas de uso de la API"""
        return {
            "total_calls": self.total_calls,
            "error_count": self.error_count,
            "last_call_time": self.last_call_time,
            "success_rate": f"{((self.total_calls - self.error_count) / self.total_calls * 100):.1f}%" if self.total_calls > 0 else "N/A"
        }

    def reset_stats(self):
        """Reinicia las estadísticas del manager"""
        self.total_calls = 0
        self.error_count = 0
        self.last_call_time = 0

# Instancia global única del API Manager
api_manager = ApiManager()

# Funciones de utilidad para operaciones comunes
def batch_update_sheet(worksheet, updates: List[Dict]) -> Tuple[bool, Optional[str]]:
    """
    Realiza actualizaciones por lotes en una hoja de cálculo
    
    Args:
        worksheet: Objeto worksheet de gspread
        updates: Lista de diccionarios con formato batchUpdate
        
    Returns:
        Tuple (éxito, mensaje_error)
    """
    if not updates:
        return True, None
    
    try:
        result, error = api_manager.safe_sheet_operation(worksheet.batch_update, updates)
        return result is not None, error
    except Exception as e:
        return False, f"Error en batch_update: {str(e)}"

def append_row(worksheet, row_data: List[Any]) -> Tuple[bool, Optional[str]]:
    """
    Agrega una fila a la hoja de cálculo
    
    Args:
        worksheet: Objeto worksheet de gspread
        row_data: Lista con los valores de la fila
        
    Returns:
        Tuple (éxito, mensaje_error)
    """
    try:
        result, error = api_manager.safe_sheet_operation(worksheet.append_row, row_data)
        return result is not None, error
    except Exception as e:
        return False, f"Error append_row: {str(e)}"

def get_all_values(worksheet) -> Tuple[List[List[Any]], Optional[str]]:
    """
    Obtiene todos los valores de una hoja
    
    Args:
        worksheet: Objeto worksheet de gspread
        
    Returns:
        Tuple (valores, mensaje_error)
    """
    try:
        values, error = api_manager.safe_sheet_operation(worksheet.get_all_values)
        return values or [], error
    except Exception as e:
        return [], f"Error get_all_values: {str(e)}"

def update_cell(worksheet, row: int, col: int, value: Any) -> Tuple[bool, Optional[str]]:
    """
    Actualiza una celda específica
    
    Args:
        worksheet: Objeto worksheet de gspread
        row: Número de fila (1-based)
        col: Número de columna (1-based)
        value: Valor a establecer
        
    Returns:
        Tuple (éxito, mensaje_error)
    """
    try:
        result, error = api_manager.safe_sheet_operation(worksheet.update_cell, row, col, value)
        return result is not None, error
    except Exception as e:
        return False, f"Error update_cell: {str(e)}"

# Inicialización automática
def initialize_api():
    """Inicializa la API al importar el módulo"""
    success, error = api_manager.initialize()
    if not success and st.secrets.get("DEBUG_MODE", False):
        st.warning(f"API no inicializada: {error}")
    return success

# Inicializar al importar
initialize_api()