# helpers.py - Funciones utilitarias para la aplicación

import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# ==================== MANEJO DE FECHAS Y HORAS ====================

def ahora_argentina():
    """Obtiene la fecha y hora actual de Argentina"""
    return datetime.now(pytz.timezone('America/Argentina/Buenos_Aires'))

def get_current_datetime():
    """Compatibilidad: devuelve la fecha y hora actual de Argentina"""
    return ahora_argentina()

def format_datetime(dt, format_str='%d/%m/%Y %H:%M'):
    """Formatea un datetime object a string"""
    if pd.isna(dt) or not isinstance(dt, datetime):
        return ''
    return dt.strftime(format_str)

def parse_fecha(fecha_str):
    """Intenta parsear una fecha desde string con múltiples formatos"""
    if pd.isna(fecha_str) or not fecha_str:
        return pd.NaT
    
    formatos = [
        '%d/%m/%Y %H:%M',    # 25/12/2023 14:30
        '%Y-%m-%d %H:%M:%S', # 2023-12-25 14:30:00
        '%d/%m/%Y',          # 25/12/2023
        '%Y-%m-%d',          # 2023-12-25
        '%m/%d/%Y',          # 12/25/2023 (formato US)
    ]
    
    for formato in formatos:
        try:
            return datetime.strptime(str(fecha_str).strip(), formato)
        except ValueError:
            continue
    
    return pd.NaT

def es_fecha_valida(fecha_str):
    """Verifica si un string puede ser parseado como fecha"""
    return not pd.isna(parse_fecha(fecha_str))

# ==================== FORMATEO DE DATOS ====================

def format_phone_number(phone):
    """Formatea un número de teléfono argentino"""
    if pd.isna(phone) or not phone:
        return ''
    
    # Limpiar y normalizar
    phone_str = re.sub(r'[^\d]', '', str(phone))
    
    # Remover prefijo internacional si existe
    if phone_str.startswith('54'):
        phone_str = phone_str[2:]
    if phone_str.startswith('0'):
        phone_str = phone_str[1:]
    
    # Formatear según longitud
    if len(phone_str) == 10:
        return f"+54 {phone_str[:3]} {phone_str[3:7]} {phone_str[7:]}"
    elif len(phone_str) == 8:
        return f"+54 11 {phone_str[:4]} {phone_str[4:]}"
    else:
        return f"+54 {phone_str}"

def format_dni(dni):
    """Formatea un DNI con puntos"""
    if pd.isna(dni) or not dni:
        return ''
    
    dni_str = re.sub(r'[^\d]', '', str(dni))
    if len(dni_str) > 3:
        return f"{dni_str[:-3]}.{dni_str[-3:]}"
    return dni_str

def truncate_text(text, max_length=50, ellipsis="..."):
    """Trunca texto muy largo con opción de ellipsis personalizado"""
    if pd.isna(text) or not text:
        return ''
    
    text_str = str(text).strip()
    if len(text_str) <= max_length:
        return text_str
    
    return text_str[:max_length - len(ellipsis)] + ellipsis

def format_currency(amount, symbol="$", decimals=2):
    """Formatea un monto como currency argentino"""
    try:
        amount_float = safe_float_conversion(amount)
        return f"{symbol}{amount_float:,.{decimals}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return f"{symbol}{str(amount)}"

# ==================== VALIDACIONES ====================

def is_valid_email(email):
    """Valida formato básico de email con regex"""
    if pd.isna(email) or not email:
        return False
    
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, str(email).strip()))

def is_valid_phone(phone):
    """Valida que sea un número de teléfono válido"""
    if pd.isna(phone) or not phone:
        return False
    
    phone_clean = re.sub(r'[^\d]', '', str(phone))
    return len(phone_clean) >= 8 and len(phone_clean) <= 15

# ==================== CONVERSIONES SEGURAS ====================

def safe_float_conversion(value, default=0.0):
    """Convierte seguro a float con manejo de errores"""
    try:
        if pd.isna(value) or value == '':
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int_conversion(value, default=0):
    """Convierte seguro a int con manejo de errores"""
    try:
        if pd.isna(value) or value == '':
            return default
        return int(float(value))  # Convierte primero a float por si viene con decimales
    except (ValueError, TypeError):
        return default

def safe_str_conversion(value, default=""):
    """Convierte seguro a string con manejo de errores"""
    try:
        if pd.isna(value):
            return default
        return str(value).strip()
    except (ValueError, TypeError):
        return default

# ==================== MANEJO DE ESTADOS Y BADGES ====================

def get_status_badge(status):
    """Devuelve un badge colorizado según el estado del reclamo"""
    status = safe_str_conversion(status).title()
    
    status_config = {
        'Pendiente': {'color': 'warning', 'icon': '⏳'},
        'En Proceso': {'color': 'info', 'icon': '🔄'},
        'En Curso': {'color': 'info', 'icon': '🔧'},
        'Resuelto': {'color': 'success', 'icon': '✅'},
        'Cerrado': {'color': 'success', 'icon': '🔒'},
        'Cancelado': {'color': 'danger', 'icon': '❌'},
        'Derivado': {'color': 'primary', 'icon': '📤'}
    }
    
    config = status_config.get(status, {'color': 'secondary', 'icon': '📋'})
    return status, config['color'], config['icon']

# ==================== UI Y NOTIFICACIONES ====================

def show_message(message, type="info", icon=None):
    """Muestra mensajes de forma consistente"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    emoji = icon or icons.get(type, "📝")
    formatted_message = f"{emoji} {message}"
    
    if type == "success":
        st.success(formatted_message)
    elif type == "error":
        st.error(formatted_message)
    elif type == "warning":
        st.warning(formatted_message)
    else:
        st.info(formatted_message)

# Alias para compatibilidad
show_success = lambda msg: show_message(msg, "success")
show_error = lambda msg: show_message(msg, "error") 
show_warning = lambda msg: show_message(msg, "warning")
show_info = lambda msg: show_message(msg, "info")

# ==================== NAVEGACIÓN Y UI ====================

def get_breadcrumb_icon(page_name):
    """Devuelve el icono correspondiente para el breadcrumb"""
    icons = {
        "Inicio": "🏠",
        "Reclamos cargados": "📊",
        "Gestión de clientes": "👥",
        "Imprimir reclamos": "🖨️",
        "Seguimiento técnico": "🔧",
        "Cierre de Reclamos": "✅",
        "Dashboard": "📈",
        "Configuración": "⚙️"
    }
    return icons.get(page_name, "📋")

def get_page_icon(page_name):
    """Devuelve icono para botones de navegación"""
    icons = {
        "Inicio": "🏠",
        "Reclamos cargados": "📋",
        "Gestión de clientes": "👥", 
        "Imprimir reclamos": "🖨️",
        "Seguimiento técnico": "🔧",
        "Cierre de Reclamos": "✅"
    }
    return icons.get(page_name, "📦")

# ==================== MANEJO DE DATOS ====================

def normalize_text(text):
    """Normaliza texto para búsquedas y comparaciones"""
    if pd.isna(text) or not text:
        return ''
    
    text_str = str(text).strip().lower()
    # Remover acentos y caracteres especiales
    replacements = [
        ('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'),
        ('ñ', 'n'), ('-', ' '), ('_', ' ')
    ]
    
    for old, new in replacements:
        text_str = text_str.replace(old, new)
    
    return text_str

def safe_compare_strings(str1, str2, case_sensitive=False):
    """Compara strings de forma segura"""
    if pd.isna(str1) or pd.isna(str2):
        return False
    
    s1 = str(str1) if case_sensitive else normalize_text(str1)
    s2 = str(str2) if case_sensitive else normalize_text(str2)
    
    return s1 == s2

# ==================== VALIDACIONES DE NEGOCIO ====================

def validar_sector(sector):
    """Valida que el sector sea válido"""
    from config.settings import SECTORES_DISPONIBLES
    return str(sector) in SECTORES_DISPONIBLES

def validar_tecnico(tecnico):
    """Valida que el técnico sea válido"""
    from config.settings import TECNICOS_DISPONIBLES
    return safe_str_conversion(tecnico) in TECNICOS_DISPONIBLES

def validar_tipo_reclamo(tipo):
    """Valida que el tipo de reclamo sea válido"""
    from config.settings import TIPOS_RECLAMO
    return safe_str_conversion(tipo) in TIPOS_RECLAMO