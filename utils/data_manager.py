"""
Gestor de datos para operaciones con Google Sheets
Versión mejorada con manejo robusto de datos
"""
import pandas as pd
import streamlit as st
import logging
from utils.api_manager import api_manager

logger = logging.getLogger(__name__)

@st.cache_data(ttl=600)
def safe_get_sheet_data(_sheet, columnas=None):
    """
    Carga datos de una hoja de cálculo de forma segura, con cacheo.
    
    Args:
        _sheet: Objeto de hoja de Google Sheets
        columnas: Lista de columnas esperadas
    
    Returns:
        DataFrame con los datos o DataFrame vacío en caso de error
    """
    try:
        sheet_name = _sheet.title
        logger.info(f"Intentando obtener datos para la hoja '{sheet_name}'. Esta llamada debería estar cacheada.")
        # Obtener todos los valores de la hoja
        data, error = api_manager.safe_sheet_operation(_sheet.get_all_values)
        if error:
            logger.error(f"Error al obtener datos de la hoja '{sheet_name}': {error}")
            st.error(f"Error al obtener datos: {error}")
            return pd.DataFrame(columns=columnas or [])
        
        # Verificar si hay datos
        if len(data) <= 1:
            return pd.DataFrame(columns=columnas or [])
        
        # Crear DataFrame
        headers = data[0]
        rows = data[1:]
        df = pd.DataFrame(rows, columns=headers)
        
        # Asegurar que todas las columnas esperadas existan
        if columnas:
            for col in columnas:
                if col not in df.columns:
                    df[col] = None
            df = df[columnas]
        
        return df
    
    except Exception as e:
        st.error(f"Error crítico al cargar datos: {str(e)}")
        return pd.DataFrame(columns=columnas or [])

def update_sheet_row(sheet, data):
    """
    Agrega una nueva fila a la hoja de cálculo
    
    Args:
        sheet: Objeto de hoja de Google Sheets
        data: Lista con los valores de la fila
    
    Returns:
        Tuple (success, error_message)
    """
    try:
        result, error = api_manager.safe_sheet_operation(
            sheet.append_row, data, is_batch=False
        )
        return result is not None, error
    except Exception as e:
        return False, str(e)

def batch_update_sheet(sheet, updates):
    """
    Realiza múltiples actualizaciones en batch
    
    Args:
        sheet: Objeto de hoja de Google Sheets
        updates: Lista de actualizaciones en formato batch
    
    Returns:
        Tuple (success, error_message)
    """
    try:
        result, error = api_manager.safe_sheet_operation(
            sheet.batch_update, updates, is_batch=True
        )
        return result is not None, error
    except Exception as e:
        return False, str(e)

def clear_and_populate_sheet(sheet, data):
    """
    Limpia la hoja y la pobla con nuevos datos
    
    Args:
        sheet: Objeto de hoja de Google Sheets
        data: Lista de listas con los datos (incluyendo headers)
    
    Returns:
        Tuple (success, error_message)
    """
    try:
        # Limpiar hoja
        result, error = api_manager.safe_sheet_operation(
            sheet.clear, is_batch=True
        )
        if error:
            return False, error
        
        # Agregar datos
        if data:
            result, error = api_manager.safe_sheet_operation(
                sheet.update, data, is_batch=True
            )
            return result is not None, error
        
        return True, None
        
    except Exception as e:
        return False, str(e)

def find_row_index(sheet, search_column, search_value):
    """
    Encuentra el índice de una fila basado en un valor específico
    
    Args:
        sheet: Objeto de hoja de Google Sheets
        search_column: Índice o nombre de columna a buscar
        search_value: Valor a buscar
    
    Returns:
        Índice de la fila (1-based) o -1 si no se encuentra
    """
    try:
        data, error = api_manager.safe_sheet_operation(sheet.get_all_values)
        if error or len(data) <= 1:
            return -1
        
        headers = data[0]
        
        # Convertir nombre de columna a índice si es necesario
        if isinstance(search_column, str):
            if search_column in headers:
                col_index = headers.index(search_column)
            else:
                return -1
        else:
            col_index = search_column
        
        # Buscar el valor
        for i, row in enumerate(data[1:], start=2):  # start=2 porque la fila 1 es header
            if len(row) > col_index and row[col_index] == str(search_value):
                return i
        
        return -1
        
    except Exception as e:
        st.error(f"Error buscando fila: {str(e)}")
        return -1

def update_cell(sheet, row, col, value):
    """
    Actualiza una celda específica
    
    Args:
        sheet: Objeto de hoja de Google Sheets
        row: Número de fila (1-based)
        col: Número de columna (1-based) o nombre de columna
        value: Nuevo valor
    
    Returns:
        Tuple (success, error_message)
    """
    try:
        # Convertir nombre de columna a índice si es necesario
        if isinstance(col, str):
            data, error = api_manager.safe_sheet_operation(sheet.get_all_values)
            if error or len(data) == 0:
                return False, "No se pudo obtener headers"
            
            headers = data[0]
            if col in headers:
                col_index = headers.index(col) + 1  # +1 porque Google Sheets es 1-based
            else:
                return False, f"Columna '{col}' no encontrada"
        else:
            col_index = col
        
        # Actualizar celda
        result, error = api_manager.safe_sheet_operation(
            sheet.update_cell, row, col_index, value, is_batch=False
        )
        return result is not None, error
        
    except Exception as e:
        return False, str(e)

# Alias para compatibilidad con código existente
safe_normalize = lambda df, column: df  # Función simplificada ya que pandas maneja bien los tipos

def update_sheet_data(sheet, data, is_batch=True):
    """
    Compatibilidad: Actualiza datos en una hoja con control de rate limiting.
    Ahora se implementa usando clear_and_populate_sheet.
    """
    # data debe ser lista de listas (incluyendo headers en la primera fila)
    return clear_and_populate_sheet(sheet, data)
