# --------------------------------------------------
# Aplicación principal de gestión de reclamos optimizada
# Versión 2.3 - Diseño optimizado para rendimiento
# --------------------------------------------------

# Standard library
import io
import json
import time
from datetime import datetime
import logging

# Third-party
import pandas as pd
import pytz
import streamlit as st
from google.oauth2 import service_account
import gspread
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from streamlit_lottie import st_lottie
from tenacity import retry, wait_exponential, stop_after_attempt

# Config
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
    DEBUG_MODE
)

# Local components
from components.admin import render_panel_administracion
from components.reclamos.nuevo import render_nuevo_reclamo
from components.reclamos.gestion import render_gestion_reclamos
from components.clientes.gestion import render_gestion_clientes
from components.reclamos.impresion import render_impresion_reclamos
from components.reclamos.planificacion import render_planificacion_grupos
from components.reclamos.cierre import render_cierre_reclamos
from components.resumen_jornada import render_resumen_jornada
from components.notifications import init_notification_manager
from components.notification_bell import render_notification_bell
from components.auth import render_login, check_authentication, render_user_info
from components.navigation import render_sidebar_navigation
from components.metrics_dashboard import render_metrics_dashboard, metric_card
from components.ui import breadcrumb, metric_card, card, badge, loading_spinner as loading_indicator
from components.ui_kit import crm_card, crm_metric, crm_badge, crm_loading, crm_alert
from utils.helpers import show_warning, show_error, show_success, show_info, format_phone_number, format_dni, get_current_datetime, format_datetime, truncate_text, is_valid_email, safe_float_conversion, safe_int_conversion, get_status_badge, format_currency, get_breadcrumb_icon

# Utils
from utils.styles import get_main_styles_v3
from utils.data_manager import safe_get_sheet_data, safe_normalize, update_sheet_data, batch_update_sheet
from utils.api_manager import api_manager, init_api_session_state
from utils.pdf_utils import agregar_pie_pdf
from utils.date_utils import parse_fecha, es_fecha_valida, format_fecha, ahora_argentina
from utils.permissions import has_permission

# Al inicio de app.py, después de los imports
def load_tailwind():
    return """
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        primary: {
                            50: '#eff6ff',
                            100: '#dbeafe',
                            200: '#bfdbfe',
                            300: '#93c5fd',
                            400: '#60a5fa',
                            500: '#3b82f6',
                            600: '#2563eb',
                            700: '#1d4ed8',
                            800: '#1e40af',
                            900: '#1e3a8a'
                        },
                        success: {
                            50: '#f0fdf4',
                            100: '#dcfce7',
                            200: '#bbf7d0',
                            300: '#86efac',
                            400: '#4ade80',
                            500: '#22c55e',
                            600: '#16a34a',
                            700: '#15803d',
                            800: '#166534',
                            900: '#14532d'
                        },
                        warning: {
                            50: '#fffbeb',
                            100: '#fef3c7',
                            200: '#fde68a',
                            300: '#fcd34d',
                            400: '#fbbf24',
                            500: '#f59e0b',
                            600: '#d97706',
                            700: '#b45309',
                            800: '#92400e',
                            900: '#78350f'
                        },
                        danger: {
                            50: '#fef2f2',
                            100: '#fee2e2',
                            200: '#fecaca',
                            300: '#fca5a5',
                            400: '#f87171',
                            500: '#ef4444',
                            600: '#dc2626',
                            700: '#b91c1c',
                            800: '#991b1b',
                            900: '#7f1d1d'
                        },
                        gray: {
                            50: '#f9fafb',
                            100: '#f3f4f6',
                            200: '#e5e7eb',
                            300: '#d1d5db',
                            400: '#9ca3af',
                            500: '#6b7280',
                            600: '#4b5563',
                            700: '#374151',
                            800: '#1f2937',
                            900: '#111827'
                        }
                    },
                    borderRadius: {
                        sm: '0.25rem',
                        md: '0.375rem',
                        lg: '0.5rem',
                        xl: '0.75rem',
                        '2xl': '1rem'
                    },
                    fontFamily: {
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                        mono: ['SF Mono', 'Monaco', 'monospace']
                    }
                }
            }
        }
    </script>
    """

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(
    page_title="Fusion Reclamos CRM",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Sistema profesional de gestión de reclamos - Fusion CRM v2.3"
    }
)

# ✅ INICIALIZAR MODO OSCURO MUY AL PRINCIPIO
if 'modo_oscuro' not in st.session_state:
    st.session_state.modo_oscuro = False

# Aplicar los estilos mejorados (SIEMPRE, incluso antes del login)
st.markdown(load_tailwind(), unsafe_allow_html=True)
st.markdown(get_main_styles_v3(dark_mode=st.session_state.modo_oscuro), unsafe_allow_html=True)

# Añadir clases de Tailwind al body
st.markdown(f"""
<script>
// Aplicar clase dark si está en modo oscuro
if (document.body.classList.contains('stApp')) {{
    document.body.classList.add('bg-gray-50');
    if ({'true' if st.session_state.modo_oscuro else 'false'}) {{
        document.body.classList.add('dark');
        document.body.classList.remove('bg-gray-50');
        document.body.style.backgroundColor = 'var(--bg-primary)';
    }}
}}
</script>
""", unsafe_allow_html=True)

# --- PRIMERO VERIFICAR AUTENTICACIÓN ANTES DE CARGAR DATOS ---
if not check_authentication():
    # Solo mostrar login sin cargar nada más
    render_login(sheet_usuarios)
    st.stop()

# --- SOLO SI ESTÁ AUTENTICADO CONTINUAR CON LA CARGA DE DATOS ---
loading_placeholder = st.empty()
loading_placeholder.markdown(loading_indicator(), unsafe_allow_html=True)

try:
    # ✅ ACTUALIZAR: Recibir la hoja de logs
    sheet_reclamos, sheet_clientes, sheet_usuarios, sheet_notifications, sheet_logs = init_google_sheets()
    if not all([sheet_reclamos, sheet_clientes, sheet_usuarios, sheet_notifications]):
        st.stop()
finally:
    loading_placeholder.empty()

# ✅ Datos del usuario actual
user_info = st.session_state.auth.get('user_info', {})
user_role = user_info.get('rol', '')

# ✅ ACTUALIZAR: Pasar la hoja de logs al precache
precache_all_data(sheet_reclamos, sheet_clientes, sheet_usuarios, sheet_notifications, sheet_logs)

# --------------------------
# FUNCIONES AUXILIARES OPTIMIZADAS
# --------------------------

def generar_id_unico():
    """Genera un ID único para reclamos"""
    import uuid
    return str(uuid.uuid4())[:8].upper()

def is_system_dark_mode():
    """Intenta detectar si el sistema está en modo oscuro"""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx is None:
            return False
        return st.session_state.get('modo_oscuro', False)
    except:
        return False

# --- 🔹 Funciones nuevas para persistencia de modo oscuro ---
MODO_OSCURO_KEY = "modo_oscuro"

def _coerce_bool(val):
    if isinstance(val, bool):
        return val
    if pd.isna(val):
        return False
    return str(val).strip().lower() in ("true", "verdadero", "si", "sí", "1", "yes", "y")

def init_modo_oscuro():
    """Inicializa st.session_state[MODO_OSCURO_KEY] desde df_usuarios si existe."""
    if MODO_OSCURO_KEY in st.session_state:
        return
    modo = is_system_dark_mode()
    df = st.session_state.get("df_usuarios")
    user_email = st.session_state.auth.get("user_info", {}).get("email")
    if df is not None and not df.empty and user_email:
        if "modo_oscuro" in df.columns:
            row = df[df["Email"] == user_email] if "Email" in df.columns else None
            if row is not None and not row.empty:
                modo = _coerce_bool(row.iloc[0].get("modo_oscuro", modo))
    st.session_state[MODO_OSCURO_KEY] = modo

def persist_modo_oscuro(new_value: bool):
    """Guarda la preferencia en sheet_usuarios."""
    df = st.session_state.get("df_usuarios")
    user_email = st.session_state.auth.get("user_info", {}).get("email")
    if df is None or not user_email:
        return False
    if "Email" in df.columns:
        row_index = df.index[df["Email"] == user_email]
        if not row_index.empty:
            idx = int(row_index[0])
            col_idx = df.columns.get_loc("modo_oscuro") if "modo_oscuro" in df.columns else None
            if col_idx is None:
                return False
            try:
                def _op(ws):
                    ws.update_cell(idx + 2, col_idx + 1, "TRUE" if new_value else "FALSE")
                api_manager.safe_sheet_operation(sheet_usuarios, _op)
                return True
            except Exception as e:
                logging.exception("Error persistiendo modo oscuro")
    return False

def _on_toggle_modo_oscuro():
    val = st.session_state.get(MODO_OSCURO_KEY, False)
    if persist_modo_oscuro(val):
        st.toast("Preferencia guardada ✅") if hasattr(st, "toast") else st.success("Preferencia guardada")
    else:
        st.info("Preferencia guardada solo en esta sesión")

# ------------------------------------------------------------

def is_mobile():
    """Detecta si la aplicación se está ejecutando en un dispositivo móvil"""
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return False
        user_agent = ctx.request.headers.get("User-Agent", "").lower()
        mobile_keywords = ['mobi', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']
        return any(keyword in user_agent for keyword in mobile_keywords)
    except:
        return False

def migrar_uuids_existentes(sheet_reclamos, sheet_clientes):
    """Genera UUIDs para registros existentes que no los tengan"""
    try:
        if not sheet_reclamos or not sheet_clientes:
            st.error("No se pudo conectar a las hojas de cálculo")
            return False

        updates_reclamos = []
        updates_clientes = []
        
        # Para Reclamos
        if 'ID Reclamo' not in st.session_state.df_reclamos.columns:
            st.error("La columna 'ID Reclamo' no existe en los datos de reclamos")
            return False
            
        reclamos_sin_uuid = st.session_state.df_reclamos[
            st.session_state.df_reclamos['ID Reclamo'].isna() | 
            (st.session_state.df_reclamos['ID Reclamo'] == '')
        ]
        
        if not reclamos_sin_uuid.empty:
            with st.status("Generando UUIDs para reclamos...", expanded=True) as status:
                st.write(f"📋 {len(reclamos_sin_uuid)} reclamos sin UUID encontrados")
                
                for _, row in reclamos_sin_uuid.iterrows():
                    nuevo_uuid = generar_id_unico()
                    updates_reclamos.append({
                        "range": f"P{row.name + 2}",  # Usando row.name para precisión
                        "values": [[nuevo_uuid]]
                    })
                
                batch_size = 50
                total_batches = (len(updates_reclamos) // batch_size) + 1
                
                for i in range(0, len(updates_reclamos), batch_size):
                    batch = updates_reclamos[i:i + batch_size]
                    progress = min((i + batch_size) / len(updates_reclamos), 1.0)
                    status.update(label=f"Actualizando reclamos... {progress:.0%}", state="running")
                    
                    success, error = api_manager.safe_sheet_operation(
                        batch_update_sheet,
                        sheet_reclamos,
                        batch,
                        is_batch=True
                    )
                    if not success:
                        st.error(f"Error al actualizar lote de reclamos: {error}")
                        return False
                
                status.update(label="✅ UUIDs para reclamos completados", state="complete", expanded=False)

        # Para Clientes
        if 'ID Cliente' not in st.session_state.df_clientes.columns:
            st.error("La columna 'ID Cliente' no existe en los datos de clientes")
            return False
            
        clientes_sin_uuid = st.session_state.df_clientes[
            st.session_state.df_clientes['ID Cliente'].isna() | 
            (st.session_state.df_clientes['ID Cliente'] == '')
        ]
        
        if not clientes_sin_uuid.empty:
            with st.status("Generando UUIDs para clientes...", expanded=True) as status:
                st.write(f"👥 {len(clientes_sin_uuid)} clientes sin UUID encontrados")
                
                for _, row in clientes_sin_uuid.iterrows():
                    nuevo_uuid = generar_id_unico()
                    updates_clientes.append({
                        "range": f"G{row.name + 2}",  # Usando row.name para precisión
                        "values": [[nuevo_uuid]]
                    })
                
                batch_size = 50
                total_batches = (len(updates_clientes) // batch_size) + 1
                
                for i in range(0, len(updates_clientes), batch_size):
                    batch = updates_clientes[i:i + batch_size]
                    progress = min((i + batch_size) / len(updates_clientes), 1.0)
                    status.update(label=f"Actualizando clientes... {progress:.0%}", state="running")
                    
                    success, error = api_manager.safe_sheet_operation(
                        batch_update_sheet,
                        sheet_clientes,
                        batch,
                        is_batch=True
                    )
                    if not success:
                        st.error(f"Error al actualizar lote de clientes: {error}")
                        return False
                
                status.update(label="✅ UUIDs para clientes completados", state="complete", expanded=False)

        if not updates_reclamos and not updates_clientes:
            st.info("ℹ️ Todos los registros ya tienen UUIDs asignados")
            return False

        # Actualizar los DataFrames en caché
        st.session_state.df_reclamos = safe_get_sheet_data(sheet_reclamos, COLUMNAS_RECLAMOS)
        st.session_state.df_clientes = safe_get_sheet_data(sheet_clientes, COLUMNAS_CLIENTES)
        
        return True

    except Exception as e:
        st.error(f"❌ Error en la migración de UUIDs: {str(e)}")
        if DEBUG_MODE:
            st.exception(e)
        return False

# --------------------------
# CONEXIÓN CON GOOGLE SHEETS
# --------------------------
@st.cache_resource(ttl=3600)
def init_google_sheets():
    """Conexión optimizada a Google Sheets con retry automático"""
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def _connect():
        creds = service_account.Credentials.from_service_account_info(
            {**st.secrets["gcp_service_account"], "private_key": st.secrets["gcp_service_account"]["private_key"].replace("\\n", "\n")},
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        sheet_notifications = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_NOTIFICACIONES)
        init_notification_manager(sheet_notifications)
        
        # ✅ CONEXIÓN A LA HOJA DE LOGS
        try:
            sheet_logs = client.open_by_key(SHEET_ID).worksheet("Logs")
        except Exception:
            # Si la hoja no existe, crear una nueva
            try:
                spreadsheet = client.open_by_key(SHEET_ID)
                sheet_logs = spreadsheet.add_worksheet(title="Logs", rows=1000, cols=10)
                # Agregar encabezados
                sheet_logs.append_row(["timestamp", "usuario", "nivel", "modulo", "accion", "detalles", "ip_address"])
            except Exception as e:
                st.error(f"Error al crear hoja de Logs: {str(e)}")
                sheet_logs = None
        
        return (
            client.open_by_key(SHEET_ID).worksheet(WORKSHEET_RECLAMOS),
            client.open_by_key(SHEET_ID).worksheet(WORKSHEET_CLIENTES),
            client.open_by_key(SHEET_ID).worksheet(WORKSHEET_USUARIOS),
            sheet_notifications,
            sheet_logs  # ✅ NUEVO: Retornar la hoja de logs
        )
    try:
        return _connect()
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        st.stop()

def precache_all_data(sheet_reclamos, sheet_clientes, sheet_usuarios, sheet_notifications, sheet_logs):
    _ = safe_get_sheet_data(sheet_reclamos, COLUMNAS_RECLAMOS)
    _ = safe_get_sheet_data(sheet_clientes, COLUMNAS_CLIENTES)
    _ = safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)
    _ = safe_get_sheet_data(sheet_notifications, COLUMNAS_NOTIFICACIONES)
    # ✅ Precargar datos de logs si existe la hoja
    if sheet_logs:
        try:
            _ = safe_get_sheet_data(sheet_logs, ["timestamp", "usuario", "nivel", "modulo", "accion", "detalles", "ip_address"])
        except Exception as e:
            st.warning(f"Advertencia al cargar logs: {str(e)}")

loading_placeholder = st.empty()
loading_placeholder.markdown(loading_indicator(), unsafe_allow_html=True)
try:
    # ✅ ACTUALIZAR: Recibir la hoja de logs
    sheet_reclamos, sheet_clientes, sheet_usuarios, sheet_notifications, sheet_logs = init_google_sheets()
    if not all([sheet_reclamos, sheet_clientes, sheet_usuarios, sheet_notifications]):
        st.stop()
finally:
    loading_placeholder.empty()

if not check_authentication():
    render_login(sheet_usuarios)
    st.stop()
    
# ✅ Datos del usuario actual
user_info = st.session_state.auth.get('user_info', {})
user_role = user_info.get('rol', '')

# ✅ ACTUALIZAR: Pasar la hoja de logs al precache
precache_all_data(sheet_reclamos, sheet_clientes, sheet_usuarios, sheet_notifications, sheet_logs)

# ✅ GUARDAR LA HOJA DE LOGS EN SESSION_STATE
st.session_state.sheet_logs = sheet_logs

df_reclamos, df_clientes, df_usuarios = safe_get_sheet_data(sheet_reclamos, COLUMNAS_RECLAMOS), safe_get_sheet_data(sheet_clientes, COLUMNAS_CLIENTES), safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)
st.session_state.df_reclamos = df_reclamos
st.session_state.df_clientes = df_clientes
st.session_state.df_usuarios = df_usuarios

# --------------------------
# CONFIGURACIÓN DE PÁGINA
# --------------------------
# Navegación optimizada
if is_mobile():
    opcion = st.selectbox(
        "Menú principal",
        options=["Inicio", "Reclamos cargados", "Cierre de Reclamos"],
        index=0,
        key="mobile_nav"
    )
else:
    opcion = st.session_state.get('current_page', 'Inicio')

# --------------------------
# SIDEBAR MODERNO
# --------------------------
with st.sidebar:
    # Header del sidebar moderno
    st.markdown("""
    <div class="text-center py-4 border-b border-gray-200 dark:border-gray-700 mb-4">
        <h2 class="text-2xl font-bold text-primary-600">📋 Fusion CRM</h2>
        <p class="text-gray-500 dark:text-gray-400 text-sm mt-1">
            Panel de Control
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información de usuario (ya mejorada en auth.py)
    render_user_info()

    # Selector de modo oscuro moderno
    st.markdown("""
    <div class="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg mb-4">
        <span class="text-xl">🌙</span>
        <div class="flex-1">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Modo oscuro</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">Cambiar entre tema claro y oscuro</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Checkbox de modo oscuro
    st.checkbox("", value=st.session_state.modo_oscuro,
                key=MODO_OSCURO_KEY, on_change=_on_toggle_modo_oscuro,
                label_visibility="collapsed")
    
    # Notificaciones
    if st.session_state.auth.get("logged_in", False):
        render_notification_bell()
    
    st.markdown("---")
    
    # Navegación profesional
    render_sidebar_navigation()
    
    # Herramientas de administrador (solo visible para admins)
    if user_role == 'admin':
        st.markdown("---")
        st.markdown("**🔧 Herramientas Admin**")
        if st.button("🆔 Generar UUIDs para registros", 
                    help="Genera IDs únicos para registros existentes que no los tengan",
                    disabled=st.session_state.get('uuid_migration_in_progress', False),
                    use_container_width=True):
            st.session_state.uuid_migration_in_progress = True
            with st.spinner("Migrando UUIDs..."):
                if migrar_uuids_existentes(sheet_reclamos, sheet_clientes):
                    st.rerun()
            st.session_state.uuid_migration_in_progress = False
    
    # En el sidebar, mejora el footer:
    st.markdown(
        f"""
        <div style="margin-top: 2rem; padding: 1rem; background: var(--bg-surface); border-radius: var(--radius-lg); border: 1px solid var(--border-color);">
            <div style="text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                <p style="margin:0; font-size: 0.9rem; color: var(--text-secondary);"><strong>Versión:</strong> 2.3.0</p>
                <p style="margin:0; font-size: 0.8rem; color: var(--text-muted);">Última actualización</p>
                <p style="margin:0; font-size: 0.9rem; color: var(--primary-color); font-weight: 600;">
                    {ahora_argentina().strftime('%d/%m/%Y %H:%M')}
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <hr style="border:1px solid var(--border-light); margin:1rem 0;" />
        <div style="text-align:center; font-size:0.8rem; color: var(--text-muted);">
            Desarrollado con 💜<br>por  
            <a href="https://instagram.com/mellamansebax" target="_blank" 
               style="color: var(--primary-color); text-decoration:none; font-weight:600;">
               Sebastián Andrés
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# --------------------------
# INICIALIZACIÓN
# --------------------------

class AppState:
    def __init__(self):
        self._init_state()
        
    def _init_state(self):
        """Inicializa todos los estados necesarios"""
        defaults = {
            'app_initialized': False,
            'df_reclamos': pd.DataFrame(),
            'df_clientes': pd.DataFrame(),
            'last_update': None,
            'modo_oscuro': is_system_dark_mode(),
            'uuid_migration_in_progress': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

app_state = AppState()

# --------------------------
# CARGA DE DATOS OPTIMIZADA
# --------------------------

@st.cache_data(ttl=30, show_spinner=False)
def cargar_datos():
    """Carga datos de Google Sheets con manejo robusto de nombres y fechas."""
    try:
        loading_placeholder = st.empty()
        loading_placeholder.markdown(get_loading_spinner(), unsafe_allow_html=True)

        df_reclamos = safe_get_sheet_data(sheet_reclamos, COLUMNAS_RECLAMOS)
        df_clientes = safe_get_sheet_data(sheet_clientes, COLUMNAS_CLIENTES)
        df_usuarios = safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)

        if df_reclamos.empty:
            show_warning("La hoja de reclamos está vacía o no se pudo cargar")
        if df_clientes.empty:
            show_warning("La hoja de clientes está vacía o no se pudo cargar")
        if df_reclamos.empty or df_clientes.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # --- Normalizar nombres de columnas (quitar espacios)
        df_reclamos.columns = [str(c).strip() for c in df_reclamos.columns]
        df_clientes.columns = [str(c).strip() for c in df_clientes.columns]
        df_usuarios.columns = [str(c).strip() for c in df_usuarios.columns]

        # --- Detectar variantes y renombrar ---
        import re
        def _canon(colname):
            return re.sub(r'[^a-z0-9]', '', str(colname).lower())

        # Mapeo a "Fecha_formateada"
        for col in list(df_reclamos.columns):
            if _canon(col) in ("fechaformateada","fechadecierre","fechacierre","fecha_cierre","fechacierrehora"):
                if col != "Fecha_formateada":
                    df_reclamos.rename(columns={col: "Fecha_formateada"}, inplace=True)
                break

        # Mapeo a "Fecha y hora"
        for col in list(df_reclamos.columns):
            if _canon(col) in ("fechayhora","fechahora","fechaingreso","fechaingresohora","fecha_hora"):
                if col != "Fecha y hora":
                    df_reclamos.rename(columns={col: "Fecha y hora"}, inplace=True)
                break

        # Normalizaciones simples
        for col in ["Nº Cliente", "N° de Precinto"]:
            if col in df_clientes.columns:
                df_clientes[col] = df_clientes[col].astype(str).str.strip()
            if col in df_reclamos.columns:
                df_reclamos[col] = df_reclamos[col].astype(str).str.strip()

        # Parseo seguro: Fecha y hora (ingreso)
        if "Fecha y hora" in df_reclamos.columns:
            df_reclamos["Fecha y hora"] = df_reclamos["Fecha y hora"].apply(
                lambda x: parse_fecha(x) if not pd.isna(x) else pd.NaT
            )

        # Parseo robusto: Fecha_formateada (cierre)
        import numpy as np
        if "Fecha_formateada" in df_reclamos.columns:
            raw = df_reclamos["Fecha_formateada"].copy()
            # Limpieza inicial
            df_reclamos["Fecha_formateada"] = (
                raw.astype(str)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
                .replace({"": np.nan, "nan": np.nan, "NaN": np.nan})
            )
            # Intentar parseo con pandas
            df_reclamos["Fecha_formateada"] = pd.to_datetime(
                df_reclamos["Fecha_formateada"],
                errors="coerce",
                dayfirst=True,
                infer_datetime_format=True
            )
        else:
            df_reclamos["Fecha_formateada"] = pd.NaT

        return df_reclamos, df_clientes, df_usuarios

    except Exception as e:
        show_error(f"Error al cargar datos: {str(e)}")
        if DEBUG_MODE:
            st.exception(e)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    finally:
        loading_placeholder.empty()

df_reclamos, df_clientes, df_usuarios = cargar_datos()
st.session_state.df_reclamos = df_reclamos
st.session_state.df_clientes = df_clientes
st.session_state.df_usuarios = df_usuarios

# --------------------------
# INTERFAZ PRINCIPAL OPTIMIZADA
# --------------------------

st.markdown("""
<div class="text-center py-10 bg-gradient-to-r from-blue-50 to-indigo-100 dark:from-gray-800 dark:to-gray-900 rounded-2xl mb-8 border border-gray-200 dark:border-gray-700 shadow-lg">
    <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
        Fusion Reclamos CRM
    </h1>
    <div class="inline-block bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-medium">
        Sistema profesional en gestión de Reclamos
    </div>
</div>
""", unsafe_allow_html=True)

# Dashboard de métricas
render_metrics_dashboard(df_reclamos, is_mobile=is_mobile())

# BREADCRUMB DE NAVEGACIÓN moderno
st.markdown(f"""
<div class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
    <div class="flex items-center space-x-3">
        <span class="text-xl text-gray-500">📋</span>
        <span class="text-gray-500">Navegación:</span>
        <span class="flex items-center space-x-2 bg-blue-50 dark:bg-blue-900/20 px-3 py-2 rounded-lg border border-blue-200 dark:border-blue-700">
            <span class="text-xl text-blue-600">{get_breadcrumb_icon(opcion)}</span>
            <span class="font-semibold text-blue-600">{opcion}</span>
        </span>
    </div>
    <span class="text-sm text-gray-400">
        {ahora_argentina().strftime('%d/%m/%Y %H:%M')}
    </span>
</div>
""", unsafe_allow_html=True)

# --------------------------
# RUTEO DE COMPONENTES
# --------------------------

COMPONENTES = {
    "Inicio": {
        "render": render_nuevo_reclamo,
        "permiso": "inicio",
        "params": {
            "df_reclamos": df_reclamos,
            "df_clientes": df_clientes,
            "sheet_reclamos": sheet_reclamos,
            "sheet_clientes": sheet_clientes,
            "current_user": user_info.get('nombre', '')
        }
    },
    "Reclamos cargados": {
        "render": render_gestion_reclamos,
        "permiso": "reclamos_cargados",
        "params": {
            "df_reclamos": df_reclamos,
            "df_clientes": df_clientes,
            "sheet_reclamos": sheet_reclamos,
            "user": user_info
        }
    },
    "Gestión de clientes": {
        "render": render_gestion_clientes,
        "permiso": "gestion_clientes",
        "params": {
            "df_clientes": df_clientes,
            "df_reclamos": df_reclamos,
            "sheet_clientes": sheet_clientes,
            "user_role": user_info.get('rol', '')
        }
    },
    "Imprimir reclamos": {
        "render": render_impresion_reclamos,
        "permiso": "imprimir_reclamos",
        "params": {
            "df_clientes": df_clientes,
            "df_reclamos": df_reclamos,
            "user": user_info
        }
    },
    "Seguimiento técnico": {
        "render": render_planificacion_grupos,
        "permiso": "seguimiento_tecnico",
        "params": {
            "df_reclamos": df_reclamos,
            "sheet_reclamos": sheet_reclamos,
            "user": user_info
        }
    },
    "Cierre de Reclamos": {
        "render": render_cierre_reclamos,
        "permiso": "cierre_reclamos",
        "params": {
            "df_reclamos": df_reclamos,
            "df_clientes": df_clientes,
            "sheet_reclamos": sheet_reclamos,
            "sheet_clientes": sheet_clientes,
            "user": user_info
        }
    },
    "Administración": {
        "render": render_panel_administracion,
        "permiso": "admin",  # Solo admins pueden acceder
        "params": {
            "df_usuarios": df_usuarios,
            "sheet_usuarios": sheet_usuarios,
            "user_info": user_info
        }
    }
}

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