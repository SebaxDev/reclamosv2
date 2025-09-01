# --------------------------------------------------
# Aplicación principal de gestión de reclamos optimizada
# Versión 2.3 - Diseño optimizado para rendimiento
# --------------------------------------------------

# -------------------------
# Standard library
# -------------------------
import io
import json
import time
import logging
from datetime import datetime

# -------------------------
# Third-party libraries
# -------------------------
import pandas as pd
import pytz
import streamlit as st
import gspread
from google.oauth2 import service_account
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from streamlit_lottie import st_lottie
from tenacity import retry, wait_exponential, stop_after_attempt

# -------------------------
# Configuración
# -------------------------
from config.settings import (
    SHEET_ID,
    WORKSHEET_RECLAMOS,
    WORKSHEET_CLIENTES,
    WORKSHEET_USUARIOS,
    COLUMNAS_RECLAMOS,
    COLUMNAS_CLIENTES,
    COLUMNAS_USUARIOS,
    WORKSHEET_NOTIFICACIONES,
    NOTIFICATION_TYPES,
    COLUMNAS_NOTIFICACIONES,
    SECTORES_DISPONIBLES,
    TIPOS_RECLAMO,
    TECNICOS_DISPONIBLES,
    MATERIALES_POR_RECLAMO,
    ROUTER_POR_SECTOR,
    DEBUG_MODE,
)

# -------------------------
# Local components
# -------------------------
from components.reclamos.nuevo import render_nuevo_reclamo
from components.reclamos.gestion import render_gestion_reclamos
from components.clientes.gestion import render_gestion_clientes
from components.reclamos.impresion import render_impresion_reclamos
from components.reclamos.planificacion import render_planificacion_grupos
from components.reclamos.cierre import render_cierre_reclamos
from components.resumen_jornada import render_resumen_jornada
from components.notifications import init_notification_manager
from components.notification_bell import render_notification_bell
from components.auth import auth_has_permission, check_authentication, render_login_form
from components.navigation import render_main_navigation
from components.metrics_dashboard import render_metrics_dashboard, metric_card
from components.ui import breadcrumb, metric_card, card, badge, loading_indicator

# -------------------------
# Utils
# -------------------------
from utils.helpers import (
    show_warning,
    show_error,
    show_success,
    show_info,
    format_phone_number,
    format_dni,
    get_current_datetime,
    format_datetime,
    truncate_text,
    is_valid_email,
    safe_float_conversion,
    safe_int_conversion,
    get_status_badge,
    format_currency,
    get_breadcrumb_icon,
)
from utils.styles import get_main_styles, get_loading_spinner, loading_indicator
from utils.data_manager import (
    safe_get_sheet_data,
    safe_normalize,
    update_sheet_data,
    batch_update_sheet,
)
from utils.api_manager import api_manager, init_api_session_state
from utils.pdf_utils import agregar_pie_pdf
from utils.date_utils import parse_fecha, es_fecha_valida, format_fecha, ahora_argentina
from utils.permissions import has_permission

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Fusion Reclamos CRM",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------
# INICIALIZACIÓN
# --------------------------

# Inicializar API manager correctamente
success, error = api_manager.initialize()
if not success:
    st.error(f"No se pudo inicializar la API de Google Sheets: {error}")
    st.stop()

# Inicializar variables de sesión de API (compatibilidad)
init_api_session_state()

# Cargar estilos Monokai (siempre modo oscuro)
st.markdown(get_main_styles(), unsafe_allow_html=True)

# --------------------------
# FUNCIONES AUXILIARES
# --------------------------

def init_google_sheets():
    """Inicializa la conexión con Google Sheets"""
    try:
        sheet_reclamos = api_manager.open_sheet(SHEET_ID, WORKSHEET_RECLAMOS)
        sheet_clientes = api_manager.open_sheet(SHEET_ID, WORKSHEET_CLIENTES)
        sheet_usuarios = api_manager.open_sheet(SHEET_ID, WORKSHEET_USUARIOS)
        
        return sheet_reclamos, sheet_clientes, sheet_usuarios
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        st.stop()

def cargar_datos():
    """Carga datos de Google Sheets"""
    try:
        sheet_reclamos, sheet_clientes, sheet_usuarios = init_google_sheets()
        
        df_reclamos = safe_get_sheet_data(sheet_reclamos, COLUMNAS_RECLAMOS)
        df_clientes = safe_get_sheet_data(sheet_clientes, COLUMNAS_CLIENTES)
        df_usuarios = safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)
        
        return df_reclamos, df_clientes, df_usuarios, sheet_reclamos, sheet_clientes
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), None, None

def render_metricas_simples(df_reclamos):
    """Renderiza métricas simplificadas de reclamos"""
    if df_reclamos.empty:
        return
    
    hoy = ahora_argentina().date()
    
    # Reclamos de hoy
    reclamos_hoy = 0
    if 'Fecha y hora' in df_reclamos.columns:
        try:
            df_reclamos['Fecha'] = pd.to_datetime(df_reclamos['Fecha y hora']).dt.date
            reclamos_hoy = len(df_reclamos[df_reclamos['Fecha'] == hoy])
        except:
            reclamos_hoy = 0
    
    # Contar por estado
    if 'Estado' in df_reclamos.columns:
        pendientes = len(df_reclamos[df_reclamos['Estado'] == 'Pendiente'])
        en_curso = len(df_reclamos[df_reclamos['Estado'] == 'En curso'])
        desconexiones = len(df_reclamos[df_reclamos['Tipo de reclamo'] == 'Desconexión'])
    else:
        pendientes = en_curso = desconexiones = 0
    
    # Mostrar métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📥 Ingresados hoy", reclamos_hoy)
    with col2:
        st.metric("⏳ Pendientes", pendientes)
    with col3:
        st.metric("🔄 En curso", en_curso)
    with col4:
        st.metric("🔌 Desconexiones", desconexiones)

def render_navegacion_principal():
    """Renderiza la navegación principal en la pantalla"""
    st.markdown("---")
    
    # Opciones de navegación
    opciones = [
        {"icon": "🏠", "nombre": "Inicio", "key": "inicio"},
        {"icon": "📋", "nombre": "Reclamos cargados", "key": "reclamos"},
        {"icon": "👥", "nombre": "Gestión de clientes", "key": "clientes"},
        {"icon": "🖨️", "nombre": "Imprimir reclamos", "key": "imprimir"},
        {"icon": "🔧", "nombre": "Seguimiento técnico", "key": "seguimiento"},
        {"icon": "✅", "nombre": "Cierre de Reclamos", "key": "cierre"}
    ]
    
    # Crear botones de navegación
    cols = st.columns(len(opciones))
    for i, opcion in enumerate(opciones):
        with cols[i]:
            if st.button(
                f"{opcion['icon']} {opcion['nombre']}", 
                key=opcion['key'],
                use_container_width=True
            ):
                st.session_state.current_page = opcion['nombre']
                st.rerun()
    
    st.markdown("---")

# --------------------------
# AUTENTICACIÓN
# --------------------------

if not check_authentication():
    df_reclamos, df_clientes, df_usuarios, sheet_reclamos, sheet_clientes = cargar_datos()
    render_login_form(sheet_usuarios)
    st.stop()

# --------------------------
# CARGA DE DATOS
# --------------------------

df_reclamos, df_clientes, df_usuarios, sheet_reclamos, sheet_clientes = cargar_datos()

# Almacenar en session state
st.session_state.df_reclamos = df_reclamos
st.session_state.df_clientes = df_clientes
st.session_state.df_usuarios = df_usuarios

# --------------------------
# INTERFAZ PRINCIPAL
# --------------------------

# Header principal
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="margin: 0; background: linear-gradient(135deg, #66D9EF 0%, #F92672 30%, #A6E22E 70%, #AE81FF 100%); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.8rem;">
        Fusion Reclamos CRM
    </h1>
    <p style="color: #CFCFC2; margin-top: 0.5rem;">
        Sistema profesional de gestión de reclamos
    </p>
</div>
""", unsafe_allow_html=True)

# Información de usuario en sidebar
with st.sidebar:
    render_user_info()
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #75715E; font-size: 0.9rem;">
        Versión 2.3 • {ahora_argentina().strftime('%d/%m/%Y %H:%M')}
    </div>
    """, unsafe_allow_html=True)

# Mostrar métricas
render_metricas_simples(df_reclamos)

# Navegación principal
render_navegacion_principal()

# --------------------------
# RUTEO DE COMPONENTES
# --------------------------

# Obtener página actual
current_page = st.session_state.get('current_page', 'Inicio')

# Renderizar componente según la página seleccionada
if current_page == 'Inicio':
    render_nuevo_reclamo(
        df_reclamos=df_reclamos,
        df_clientes=df_clientes,
        sheet_reclamos=sheet_reclamos,
        sheet_clientes=sheet_clientes,
        current_user=st.session_state.auth.get('user_info', {}).get('nombre', '')
    )

elif current_page == 'Reclamos cargados':
    render_gestion_reclamos(
        df_reclamos=df_reclamos,
        df_clientes=df_clientes,
        sheet_reclamos=sheet_reclamos,
        user=st.session_state.auth.get('user_info', {})
    )

elif current_page == 'Gestión de clientes':
    render_gestion_clientes(
        df_clientes=df_clientes,
        df_reclamos=df_reclamos,
        sheet_clientes=sheet_clientes,
        user_role=st.session_state.auth.get('user_info', {}).get('rol', '')
    )

elif current_page == 'Imprimir reclamos':
    render_impresion_reclamos(
        df_clientes=df_clientes,
        df_reclamos=df_reclamos,
        user=st.session_state.auth.get('user_info', {})
    )

elif current_page == 'Seguimiento técnico':
    render_planificacion_grupos(
        df_reclamos=df_reclamos,
        sheet_reclamos=sheet_reclamos,
        user=st.session_state.auth.get('user_info', {})
    )

elif current_page == 'Cierre de Reclamos':
    render_cierre_reclamos(
        df_reclamos=df_reclamos,
        df_clientes=df_clientes,
        sheet_reclamos=sheet_reclamos,
        sheet_clientes=sheet_clientes,
        user=st.session_state.auth.get('user_info', {})
    )

# Renderizar componente seleccionado
if opcion in COMPONENTES and has_permission(COMPONENTES[opcion]["permiso"]):
    with st.container():
        st.markdown("---")
        resultado = COMPONENTES[opcion]["render"](**COMPONENTES[opcion]["params"])
        
        if resultado and resultado.get('needs_refresh'):
            st.cache_data.clear()
            time.sleep(1)
            st.rerun()

# --------------------------
# RESUMEN DE JORNADA OPTIMIZADO
# --------------------------
with st.container():
    render_resumen_jornada(df_reclamos)
    st.markdown('</div>', unsafe_allow_html=True)