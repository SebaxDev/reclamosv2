"""
Aplicación principal de gestión de reclamos optimizada
Versión 2.0 - Con manejo robusto de API y session_state
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import time
from google.oauth2 import service_account
import gspread
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# Imports de componentes
from components.auth import has_permission, check_authentication, render_login, render_user_info
from components.navigation import render_navigation, render_user_info
from components.metrics_dashboard import render_metrics_dashboard
from utils.styles import get_main_styles
from utils.data_manager import safe_get_sheet_data, safe_normalize, update_sheet_data, batch_update_sheet
from utils.api_manager import api_manager, init_api_session_state  # Import modificado
from utils.pdf_utils import agregar_pie_pdf
from config.settings import *
from components.user_widget import show_user_widget

# --------------------------------------------------
# INICIALIZACIÓN GARANTIZADA
# --------------------------------------------------
if 'app_initialized' not in st.session_state:
    init_api_session_state()  # Inicializa API
    st.session_state.app_initialized = True  # Marcar app como inicializada
    st.session_state.df_reclamos = pd.DataFrame()  # Dataframes iniciales
    st.session_state.df_clientes = pd.DataFrame()
# --------------------------
# INICIALIZACIONES
# --------------------------

# Configuración de página
st.set_page_config(
    page_title="Fusion Reclamos App",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Función para detectar el modo oscuro del sistema
def is_system_dark_mode():
    import platform
    if platform.system() == "Windows":
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
            return value == 0  # 0 = oscuro, 1 = claro
        except:
            return False
    elif platform.system() == "Darwin":
        import subprocess
        try:
            result = subprocess.run(['defaults', 'read', '-g', 'AppleInterfaceStyle'], capture_output=True, text=True)
            return "Dark" in result.stdout
        except:
            return False
    else:
        return False  # Linux u otros

# Inicializar modo oscuro si no está en sesión
if "modo_oscuro" not in st.session_state:
    sistema_oscuro = is_system_dark_mode()
    st.session_state.modo_oscuro = sistema_oscuro

# Sidebar con toggle para cambiar modo
with st.sidebar:
    nuevo_modo = st.toggle(
        "🌙 Modo oscuro",
        value=st.session_state.modo_oscuro,
        key="dark_mode_toggle"
    )
    if nuevo_modo != st.session_state.modo_oscuro:
        st.session_state.modo_oscuro = nuevo_modo
        st.rerun()
    show_user_widget()

# Aplicar estilos personalizados según modo
st.markdown(get_main_styles(dark_mode=st.session_state.modo_oscuro), unsafe_allow_html=True)

# --------------------------
# CONEXIÓN CON GOOGLE SHEETS
# --------------------------

@st.cache_resource
def init_google_sheets():
    """Inicializa la conexión con Google Sheets con manejo de errores mejorado"""
    try:
        # Cargar credenciales de forma segura
        if 'gcp_service_account' not in st.secrets:
            raise ValueError("No se encontraron credenciales en st.secrets")
            
        info = dict(st.secrets["gcp_service_account"])
        info["private_key"] = info["private_key"].replace("\\n", "\n")
        
        credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"]
        )
        
        client = gspread.authorize(credentials)
        
        # Validar existencia de las hojas
        try:
            sheet_reclamos = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_RECLAMOS)
            sheet_clientes = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_CLIENTES)
            sheet_usuarios = client.open_by_key(SHEET_ID).worksheet(WORKSHEET_USUARIOS)
            return sheet_reclamos, sheet_clientes, sheet_usuarios
        except gspread.WorksheetNotFound as e:
            raise ValueError(f"Hoja no encontrada: {str(e)}")
            
    except Exception as e:
        st.error(f"🔴 Error crítico al conectar con Google Sheets: {str(e)}")
        st.stop()
        return None, None, None

# Inicializar conexión con Google Sheets
with st.spinner("Conectando con Google Sheets..."):
    sheet_reclamos, sheet_clientes, sheet_usuarios = init_google_sheets()
    if not all([sheet_reclamos, sheet_clientes, sheet_usuarios]):
        st.stop()

# Verificar autenticación
if not check_authentication():
    render_login(sheet_usuarios)
    st.stop()

# Obtener información del usuario actual
user_info = st.session_state.auth.get('user_info', {})
user_role = user_info.get('rol', '')
# --------------------------
# CARGA DE DATOS
# --------------------------

@st.cache_data(ttl=30, show_spinner="Cargando datos...")
def cargar_datos():
    """Carga datos de Google Sheets con manejo de errores"""
    try:
        # Cargar datos de las hojas (esto ya lo tienes)
        df_reclamos = safe_get_sheet_data(sheet_reclamos, COLUMNAS_RECLAMOS)
        df_clientes = safe_get_sheet_data(sheet_clientes, COLUMNAS_CLIENTES)
        df_usuarios = safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)
        
        if df_reclamos.empty or df_clientes.empty:
            st.warning("⚠️ Algunas hojas están vacías")
        
        # Normalizar columnas clave (esto ya lo tienes)
        for col in ["Nº Cliente", "N° de Precinto"]:
            df_clientes = safe_normalize(df_clientes, col)
            df_reclamos = safe_normalize(df_reclamos, col)
            
        # Normalización robusta de fechas
        argentina = pytz.timezone("America/Argentina/Buenos_Aires")
        
        def parse_fecha(fecha_str):
            if pd.isna(fecha_str):
                return pd.NaT
                
            formatos = [
                '%d/%m/%Y %H:%M:%S',  # Formato objetivo
                '%d-%m-%Y %H:%M:%S',
                '%m/%d/%Y %H:%M:%S',   # Formato americano
                '%Y-%m-%d %H:%M:%S'    # Formato ISO
            ]
            
            for fmt in formatos:
                try:
                    dt = datetime.strptime(str(fecha_str).strip(), fmt)
                    return argentina.localize(dt)
                except ValueError:
                    continue
            return pd.NaT
        
        df_reclamos['Fecha y hora'] = df_reclamos['Fecha y hora'].apply(parse_fecha)
        
        # Verificación de fechas inválidas
        if df_reclamos['Fecha y hora'].isna().any():
            num_fechas_invalidas = df_reclamos['Fecha y hora'].isna().sum()
            st.warning(f"⚠️ Advertencia: {num_fechas_invalidas} reclamos tienen fechas inválidas o faltantes")
            
            # Opcional: Mostrar filas problemáticas en modo debug
            if DEBUG_MODE:
                st.write("Filas con fechas inválidas:", df_reclamos[df_reclamos['Fecha y hora'].isna()])
        
        # Crear columna adicional con fecha formateada como string
        df_reclamos['Fecha_formateada'] = df_reclamos['Fecha y hora'].apply(
            lambda x: x.strftime('%d/%m/%Y %H:%M:%S') if pd.notna(x) else 'Fecha no disponible'
        )
        # === FIN DE LA NUEVA SECCIÓN ===
            
        return df_reclamos, df_clientes, df_usuarios
        
    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Cargar datos y guardar en session_state
df_reclamos, df_clientes, df_usuarios = cargar_datos()
st.session_state.df_reclamos = df_reclamos
st.session_state.df_clientes = df_clientes

# --------------------------
# INTERFAZ PRINCIPAL
# --------------------------
st.markdown("---")
# Header
st.title("📋 Fusion Reclamos App")

# Dashboard de métricas
render_metrics_dashboard(df_reclamos)
st.divider()

# Navegación
opcion = render_navigation()

# --------------------------
# SECCIÓN 1: INICIO - NUEVO RECLAMO
# --------------------------

if opcion == "Inicio" and has_permission('inicio'):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📝 Cargar nuevo reclamo")

    nro_cliente = st.text_input("🔢 N° de Cliente", placeholder="Ingresa el número de cliente").strip()
    cliente_existente = None
    formulario_bloqueado = False
    reclamo_guardado = False
    cliente_nuevo = False

    if "Nº Cliente" in df_clientes.columns and nro_cliente:
        df_clientes["Nº Cliente"] = df_clientes["Nº Cliente"].astype(str).str.strip()
        df_reclamos["Nº Cliente"] = df_reclamos["Nº Cliente"].astype(str).str.strip()

        match = df_clientes[df_clientes["Nº Cliente"] == nro_cliente]

        # Convertir fechas a datetime y manejar posibles errores
        try:
            df_reclamos["Fecha y hora"] = pd.to_datetime(
                df_reclamos["Fecha y hora"], 
                dayfirst=True,  # Para formato dd/mm/yyyy
                errors='coerce'  # Convierte errores a NaT
            )
        except Exception as e:
            st.error(f"Error al procesar fechas: {str(e)}")
            df_reclamos["Fecha y hora"] = pd.NaT

        reclamos_activos = df_reclamos[
            (df_reclamos["Nº Cliente"] == nro_cliente) &
            (
                df_reclamos["Estado"].isin(["Pendiente", "En curso"]) |
                (
                    df_reclamos["Tipo de reclamo"].str.strip().str.lower() == "desconexion a pedido"
                )
            )
        ]

        if not match.empty:
            cliente_existente = match.iloc[0].to_dict()
            st.success("✅ Cliente reconocido, datos auto-cargados.")
        else:
            st.info("ℹ️ Cliente no encontrado. Se cargará como Cliente Nuevo.")

        if not reclamos_activos.empty:
            st.error("⚠️ Este cliente ya tiene un reclamo sin resolver o una desconexión activa. No se puede cargar uno nuevo.")
            formulario_bloqueado = True

            reclamo_vigente = reclamos_activos.sort_values("Fecha y hora", ascending=False).iloc[0]

            with st.expander("🔍 Ver detalles del reclamo activo"):
                # Formatear fecha para mostrar
                fecha_formateada = reclamo_vigente['Fecha y hora'].strftime('%d/%m/%Y %H:%M:%S') if pd.notna(reclamo_vigente['Fecha y hora']) else 'Fecha no disponible'
                st.markdown(f"**📅 Fecha del reclamo:** {fecha_formateada}")
                st.markdown(f"**👤 Cliente:** {reclamo_vigente['Nombre']}")
                st.markdown(f"**📌 Tipo de reclamo:** {reclamo_vigente['Tipo de reclamo']}")
                st.markdown(f"**📝 Detalles:** {reclamo_vigente['Detalles'][:250]}{'...' if len(reclamo_vigente['Detalles']) > 250 else ''}")
                st.markdown(f"**⚙️ Estado:** {reclamo_vigente['Estado'] or 'Sin estado'}")
                st.markdown(f"**👷 Técnico asignado:** {reclamo_vigente.get('Técnico', 'No asignado') or 'No asignado'}")
                st.markdown(f"**🙍‍♂️ Atendido por:** {reclamo_vigente.get('Atendido por', 'N/A')}")

    if not formulario_bloqueado:
        with st.form("reclamo_formulario", clear_on_submit=True):
            col1, col2 = st.columns(2)

            if cliente_existente:
                with col1:
                    nombre = st.text_input("👤 Nombre del Cliente", value=cliente_existente.get("Nombre", ""))
                    direccion = st.text_input("📍 Dirección", value=cliente_existente.get("Dirección", ""))
                with col2:
                    telefono = st.text_input("📞 Teléfono", value=cliente_existente.get("Teléfono", ""))
                    sector = st.text_input("🏩 Sector / Zona", value=cliente_existente.get("Sector", ""))
            else:
                with col1:
                    nombre = st.text_input("👤 Nombre del Cliente", placeholder="Nombre completo")
                    direccion = st.text_input("📍 Dirección", placeholder="Dirección completa")
                with col2:
                    telefono = st.text_input("📞 Teléfono", placeholder="Número de contacto")
                    sector = st.text_input("🏩 Sector / Zona", placeholder="Coloque número de sector")

            tipo_reclamo = st.selectbox("📌 Tipo de Reclamo", TIPOS_RECLAMO)
            detalles = st.text_area("📝 Detalles del Reclamo", placeholder="Describe el problema o solicitud...", height=100)

            col3, col4 = st.columns(2)
            with col3:
                precinto = st.text_input("🔒 N° de Precinto (opcional)",
                                       value=cliente_existente.get("N° de Precinto", "").strip() if cliente_existente else "",
                                       placeholder="Número de precinto")
            with col4:
                atendido_por = st.text_input("👤 Atendido por", placeholder="Nombre de quien atiende", value=st.session_state.get("current_user", ""))

            enviado = st.form_submit_button("✅ Guardar Reclamo", use_container_width=True)

        if enviado:
            if not nro_cliente:
                st.error("⚠️ Debes ingresar un número de cliente.")
            elif not all([nombre.strip(), direccion.strip(), sector.strip(), tipo_reclamo.strip(), atendido_por.strip()]):
                st.error("⚠️ Todos los campos obligatorios deben estar completos.")
            else:
                with st.spinner("Guardando reclamo..."):
                    try:
                        argentina = pytz.timezone("America/Argentina/Buenos_Aires")
                        # Crear objeto datetime con zona horaria
                        fecha_hora_obj = datetime.now(argentina)
                        # Formatear para Google Sheets (como string)
                        fecha_hora_str = fecha_hora_obj.strftime("%d/%m/%Y %H:%M:%S")
                        # También guardar timestamp para posible uso futuro
                        timestamp = fecha_hora_obj.timestamp()

                        estado_reclamo = "" if tipo_reclamo.strip().lower() == "desconexion a pedido" else "Pendiente"

                        fila_reclamo = [
                            fecha_hora_str,  # String formateado para Google Sheets
                            nro_cliente, 
                            sector, 
                            nombre.upper(),
                            direccion.upper(), 
                            telefono, 
                            tipo_reclamo,
                            detalles.upper(), 
                            estado_reclamo, 
                            "", 
                            precinto, 
                            atendido_por.upper()
                        ]

                        success, error = api_manager.safe_sheet_operation(
                            sheet_reclamos.append_row,
                            fila_reclamo
                        )

                        if success:
                            reclamo_guardado = True
                            st.success(f"✅ Reclamo cargado para el cliente {nro_cliente} - {tipo_reclamo.upper()}")

                            if tipo_reclamo.strip().lower() == "desconexion a pedido":
                                st.warning("📄 Este reclamo es una Desconexión a Pedido. **Y NO CUENTA como reclamo activo.**")

                            if nro_cliente not in df_clientes["Nº Cliente"].values:
                                fila_cliente = [nro_cliente, sector, nombre.upper(), direccion.upper(), telefono, precinto]
                                success_cliente, _ = api_manager.safe_sheet_operation(
                                    sheet_clientes.append_row,
                                    fila_cliente
                                )
                                if success_cliente:
                                    cliente_nuevo = True

                            # Limpiar caché y recargar datos
                            st.cache_data.clear()
                            time.sleep(4) 
                            st.rerun()
                        else:
                            st.error(f"❌ Error al guardar: {error}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# SECCIÓN 2: RECLAMOS CARGADOS
# ----------------------------

elif opcion == "Reclamos cargados" and has_permission('reclamos_cargados'):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📊 Gestión de reclamos cargados")

    try:
        # Copia del dataframe original
        df = df_reclamos.copy()

        # Normalización de columnas clave
        df_clientes["Nº Cliente"] = df_clientes["Nº Cliente"].astype(str).str.strip()
        df["Nº Cliente"] = df["Nº Cliente"].astype(str).str.strip()

        # Merge con datos del cliente
        df = pd.merge(df, df_clientes[["Nº Cliente", "N° de Precinto", "Teléfono"]], 
                      on="Nº Cliente", how="left", suffixes=("", "_cliente"))

        # Procesamiento robusto de fechas
        df["Fecha y hora"] = pd.to_datetime(
            df["Fecha y hora"], 
            dayfirst=True,  # Para formato dd/mm/yyyy
            errors='coerce'  # Convierte errores a NaT
        )
        
        # Verificar si hay fechas inválidas
        if df["Fecha y hora"].isna().any():
            num_fechas_invalidas = df["Fecha y hora"].isna().sum()
            st.warning(f"⚠️ Advertencia: {num_fechas_invalidas} reclamos tienen fechas inválidas o faltantes")

        df = df.sort_values("Fecha y hora", ascending=False)

        # Función para formatear fechas para visualización
        def format_fecha(fecha):
            if pd.isna(fecha):
                return "Fecha no disponible"
            try:
                return fecha.strftime('%d/%m/%Y %H:%M:%S')
            except:
                return "Fecha inválida"

        # === (RECLAMOS POR TIPO) ===
        df_activos = df[df["Estado"].isin(["Pendiente", "En curso"])]

        if not df_activos.empty:
            conteo_por_tipo = df_activos["Tipo de reclamo"].value_counts().sort_index()

            st.markdown("#### 📊 Distribución de reclamos activos por tipo")
            st.markdown('<div style="margin-top: -10px; margin-bottom: 10px;">', unsafe_allow_html=True)

            tipos = list(conteo_por_tipo.index)
            cantidad = list(conteo_por_tipo.values)
            cols_per_row = 4
            for i in range(0, len(tipos), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(tipos):
                        tipo = tipos[i + j]
                        cant = cantidad[i + j]
                        color_cantidad = "#dc3545" if cant > 10 else "#0d6efd"
                        font_size = "1.4rem" if cant > 10 else "1.2rem"
                        with col:
                            st.markdown(f"""
                                <div style="text-align: center; padding: 5px; border-radius: 8px; background-color: #f8f9fa;">
                                    <h5 style='margin: 0; font-size: 0.70rem; color: #6c757d;'>{tipo}</h5>
                                    <h4 style='margin: 2px 0 0 0; color: {color_cantidad}; font-size: {font_size};'>{cant}</h4>
                                </div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # === FILTROS ===
        st.markdown("#### 🔍 Filtros de búsqueda")
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_estado = st.selectbox("Estado", ["Todos"] + sorted(df["Estado"].dropna().unique()))
        with col2:
            filtro_sector = st.selectbox("Sector", ["Todos"] + sorted(df["Sector"].dropna().unique()))
        with col3:
            filtro_tipo = st.selectbox("Tipo de reclamo", ["Todos"] + sorted(df["Tipo de reclamo"].dropna().unique()))

        df_filtrado = df.copy()
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Estado"] == filtro_estado]
        if filtro_sector != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Sector"] == filtro_sector]
        if filtro_tipo != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Tipo de reclamo"] == filtro_tipo]

        st.markdown(f"**Mostrando {len(df_filtrado)} reclamos**")

        # Mostrar dataframe con fechas formateadas
        columnas_visibles = ["Fecha y hora", "Nº Cliente", "Nombre", "Sector", "Tipo de reclamo", "Teléfono", "Estado"]
        df_mostrar = df_filtrado[columnas_visibles].copy()
        df_mostrar["Fecha y hora"] = df_mostrar["Fecha y hora"].apply(format_fecha)
        
        st.dataframe(df_mostrar, use_container_width=True, hide_index=True)

        # === FORMULARIO DE EDICIÓN MANUAL ===
        st.markdown("---")
        st.markdown("### ✏️ Editar un reclamo puntual")

        df_filtrado["label_selector"] = df_filtrado["Nº Cliente"] + " - " + df_filtrado["Nombre"]
        selector = st.selectbox(
            "Seleccioná un reclamo por Nº de Cliente y Nombre",
            [""] + df_filtrado["label_selector"].tolist()
        )

        if selector:
            nro_cliente = selector.split(" - ")[0]
            reclamo_actual = df[df["Nº Cliente"] == nro_cliente].iloc[0]
            
            # Mostrar estado actual
            estado_actual = reclamo_actual.get("Estado", "")
            st.markdown(f"**Estado actual:** {estado_actual}")
            
            # Mostrar fecha formateada
            fecha_formateada = format_fecha(reclamo_actual.get("Fecha y hora"))
            st.markdown(f"**Fecha del reclamo:** {fecha_formateada}")
            
            nueva_direccion = st.text_input("Dirección", value=reclamo_actual.get("Dirección", ""))
            nuevo_telefono = st.text_input("Teléfono", value=reclamo_actual.get("Teléfono", ""))
            nuevo_tipo = st.selectbox("Tipo de reclamo", sorted(df["Tipo de reclamo"].unique()), 
                                      index=sorted(df["Tipo de reclamo"].unique()).index(reclamo_actual["Tipo de reclamo"]))
            nuevos_detalles = st.text_area("Detalles del reclamo", value=reclamo_actual.get("Detalles", ""), height=100)
            nuevo_precinto = st.text_input("N° de Precinto", value=reclamo_actual.get("N° de Precinto", ""))
            
            # Nuevo campo para cambiar estado
            nuevo_estado = st.selectbox(
                "Estado del reclamo",
                ["Pendiente", "En curso", "Resuelto"],
                index=["Pendiente", "En curso", "Resuelto"].index(estado_actual) if estado_actual in ["Pendiente", "En curso", "Resuelto"] else 0
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 Guardar cambios", key="guardar_reclamo_individual", use_container_width=True):
                    with st.spinner("Guardando cambios..."):
                        try:
                            idx_original = df[df["Nº Cliente"] == nro_cliente].index[0]
                            
                            updates = {
                                "Dirección": nueva_direccion,
                                "Teléfono": nuevo_telefono,
                                "Tipo de reclamo": nuevo_tipo,
                                "Detalles": nuevos_detalles,
                                "N° de Precinto": nuevo_precinto,
                                "Estado": nuevo_estado
                            }
                            
                            # Si vuelve a pendiente, limpiar técnico
                            if nuevo_estado == "Pendiente":
                                updates["Técnico"] = ""
                            
                            # Actualizar el dataframe local
                            for col, val in updates.items():
                                df.loc[idx_original, col] = val
                            
                            # Preparar datos para actualizar en Google Sheets
                            df = df.astype(str)
                            data_to_update = [df.columns.tolist()] + df.values.tolist()
                            
                            success, error = api_manager.safe_sheet_operation(
                                sheet_reclamos.update,
                                data_to_update,
                                is_batch=True
                            )
                            
                            if success:
                                st.success("✅ Reclamo actualizado correctamente.")
                                st.cache_data.clear()
                                time.sleep(4)  
                                st.rerun()
                            else:
                                st.error(f"❌ Error al guardar: {error}")
                        except Exception as e:
                            st.error(f"❌ Error al procesar: {str(e)}")
            
            with col2:
                if st.button("🔄 Cambiar solo estado", key="cambiar_estado", use_container_width=True):
                    with st.spinner("Actualizando estado..."):
                        try:
                            idx_original = df[df["Nº Cliente"] == nro_cliente].index[0]
                            
                            # Actualizar solo el estado
                            df.loc[idx_original, "Estado"] = nuevo_estado
                            
                            # Si vuelve a pendiente, limpiar técnico
                            if nuevo_estado == "Pendiente":
                                df.loc[idx_original, "Técnico"] = ""
                            
                            # Actualizar en Google Sheets
                            df = df.astype(str)
                            data_to_update = [df.columns.tolist()] + df.values.tolist()
                            
                            success, error = api_manager.safe_sheet_operation(
                                sheet_reclamos.update,
                                data_to_update,
                                is_batch=True
                            )
                            
                            if success:
                                st.success(f"✅ Estado cambiado a {nuevo_estado}.")
                                st.cache_data.clear()
                                time.sleep(4)
                                st.rerun()
                            else:
                                st.error(f"❌ Error al cambiar estado: {error}")
                        except Exception as e:
                            st.error(f"❌ Error al procesar: {str(e)}")

        # === DESCONEXIONES A PEDIDO ===
        st.markdown("---")
        st.markdown("### 🔌 Gestión de Desconexiones a Pedido")

        desconexiones = df[
            (df["Tipo de reclamo"].str.strip().str.lower() == "desconexion a pedido") &
            ((df["Estado"].isna()) | (df["Estado"] == ""))
        ].copy()

        cantidad = len(desconexiones)
        st.info(f"📄 Hay {cantidad} desconexiones a pedido sin estado cargadas.")

        if cantidad > 0:
            if st.button("📄 Generar PDF de desconexiones pendientes"):
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                width, height = A4
                y = height - 40

                c.setFont("Helvetica-Bold", 16)
                c.drawString(40, y, f"DESCONEXIONES A PEDIDO - {datetime.now().strftime('%d/%m/%Y')}")
                y -= 30

                for i, reclamo in desconexiones.iterrows():
                    c.setFont("Helvetica-Bold", 14)
                    c.drawString(40, y, f"{reclamo['Nº Cliente']} - {reclamo['Nombre']}")
                    y -= 15
                    c.setFont("Helvetica", 12)
                    
                    # Formatear fecha para PDF
                    fecha_pdf = format_fecha(reclamo.get("Fecha y hora"))
                    
                    lineas = [
                        f"Fecha: {fecha_pdf}",
                        f"Dirección: {reclamo['Dirección']} - Tel: {reclamo['Teléfono']}",
                        f"Sector: {reclamo['Sector']} - Precinto: {reclamo.get('N° de Precinto', 'N/A')}",
                        f"Detalles: {reclamo['Detalles'][:100]}..." if reclamo['Detalles'] and len(reclamo['Detalles']) > 100 else f"Detalles: {reclamo['Detalles']}"
                    ]
                    for linea in lineas:
                        c.drawString(40, y, linea)
                        y -= 12
                    y -= 8
                    c.line(40, y, width - 40, y)
                    y -= 15
                    if y < 100:
                        agregar_pie_pdf(c, width, height)
                        c.showPage()
                        y = height - 40

                agregar_pie_pdf(c, width, height)
                c.save()
                buffer.seek(0)
                st.download_button("📥 Descargar PDF de desconexiones", buffer, file_name="desconexiones_pedido.pdf", mime="application/pdf")

            st.markdown("#### ✅ Marcar como resueltas")
            for i, row in desconexiones.iterrows():
                col1, col2 = st.columns([5, 1])
                fecha_formateada = format_fecha(row.get("Fecha y hora"))
                col1.markdown(f"**{row['Nº Cliente']} - {row['Nombre']} - {fecha_formateada} - Sector {row['Sector']}**")
                if col2.button("Resuelto", key=f"resuelto_{i}"):
                    try:
                        fila = i + 2
                        success, error = api_manager.safe_sheet_operation(
                            sheet_reclamos.update,
                            f"I{fila}",
                            [["Resuelto"]]
                        )
                        if success:
                            st.success(f"☑️ Reclamo {row['Nº Cliente']} marcado como resuelto.")
                            st.cache_data.clear()
                            time.sleep(4)
                            st.rerun()
                        else:
                            st.error(f"❌ Error al actualizar: {error}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {str(e)}")

    except Exception as e:
        st.error(f"⚠️ Error en la gestión de reclamos: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# SECCIÓN 3: GESTION DE CLIENTES
# --------------------------

elif opcion == "Gestión de clientes" and has_permission('gestion_clientes'):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🗂️ Gestión de clientes")
    
    # Pestañas para separar las funcionalidades
    tab_historial, tab_edicion = st.tabs(["📜 Historial de cliente", "🛠️ Editar/Crear cliente"])
    
    with tab_historial:
        st.subheader("📜 Historial de reclamos por cliente")
        
        historial_cliente = st.text_input("🔍 Ingresá N° de Cliente para ver su historial", 
                                        placeholder="Número de cliente", 
                                        key="input_historial").strip()

        if historial_cliente:
            # Normalización de datos
            df_reclamos["Nº Cliente"] = df_reclamos["Nº Cliente"].astype(str).str.strip()
            historial = df_reclamos[df_reclamos["Nº Cliente"] == historial_cliente]

            if not historial.empty:
                # Procesamiento robusto de fechas en el historial
                try:
                    historial["Fecha y hora"] = pd.to_datetime(
                        historial["Fecha y hora"], 
                        dayfirst=True,  # Para formato dd/mm/yyyy
                        errors='coerce'  # Convierte errores a NaT
                    )
                    historial = historial.sort_values("Fecha y hora", ascending=False)
                    
                    # Función para formatear fechas
                    def format_fecha(fecha):
                        if pd.isna(fecha):
                            return "Fecha no disponible"
                        try:
                            return fecha.strftime('%d/%m/%Y %H:%M:%S')
                        except:
                            return "Fecha inválida"
                    
                    # Aplicar formato a la columna de fecha para visualización
                    historial_display = historial.copy()
                    historial_display["Fecha y hora"] = historial_display["Fecha y hora"].apply(format_fecha)
                except Exception as e:
                    st.error(f"⚠️ Error al procesar fechas del historial: {str(e)}")
                    historial_display = historial.copy()

                st.success(f"🔎 Se encontraron {len(historial)} reclamos para el cliente {historial_cliente}.")
                
                # Mostrar información del cliente
                cliente_info = df_clientes[df_clientes["Nº Cliente"] == historial_cliente]
                if not cliente_info.empty:
                    cliente = cliente_info.iloc[0]
                    with st.expander("📋 Información del Cliente", expanded=True):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**👤 Nombre:** {cliente['Nombre']}")
                        with col2:
                            st.markdown(f"**📍 Dirección:** {cliente['Dirección']}")
                        with col3:
                            st.markdown(f"**📞 Teléfono:** {cliente['Teléfono']}")
                
                # Mostrar historial en tabla con fechas formateadas
                st.dataframe(
                    historial_display[["Fecha y hora", "Tipo de reclamo", "Estado", "Técnico", "N° de Precinto", "Detalles"]],
                    use_container_width=True,
                    height=400
                )
                
                # Opción para exportar a CSV (manteniendo los datos originales)
                csv = historial.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar historial a CSV",
                    data=csv,
                    file_name=f"historial_cliente_{historial_cliente}.csv",
                    mime="text/csv"
                )
            else:
                st.info("❕ Este cliente no tiene reclamos registrados.")
    
    with tab_edicion:
        if user_role == 'admin':
            st.subheader("🛠️ Editar datos de un cliente")
            
            cliente_editar = st.text_input("🔎 Ingresá N° de Cliente a editar", 
                                        placeholder="Número de cliente",
                                        key="input_editar_cliente").strip()

            if cliente_editar:
                df_clientes["Nº Cliente"] = df_clientes["Nº Cliente"].astype(str).str.strip()
                cliente_row = df_clientes[df_clientes["Nº Cliente"] == cliente_editar]

                if not cliente_row.empty:
                    cliente_actual = cliente_row.iloc[0]
                    
                    with st.form("editar_cliente_form"):
                        col1, col2 = st.columns(2)
                        with col1:
                            nuevo_sector = st.text_input("🏙️ Sector", value=cliente_actual.get("Sector", ""))
                            nuevo_nombre = st.text_input("👤 Nombre", value=cliente_actual.get("Nombre", ""))
                        with col2:
                            nueva_direccion = st.text_input("📍 Dirección", value=cliente_actual.get("Dirección", ""))
                            nuevo_telefono = st.text_input("📞 Teléfono", value=cliente_actual.get("Teléfono", ""))
                        
                        nuevo_precinto = st.text_input("🔒 N° de Precinto", 
                                                    value=cliente_actual.get("N° de Precinto", ""),
                                                    help="Número de precinto del medidor")

                        actualizar = st.form_submit_button("💾 Actualizar datos del cliente", use_container_width=True)

                    if actualizar:
                        with st.spinner("Actualizando cliente..."):
                            try:
                                index = cliente_row.index[0] + 2  # +2 porque la hoja empieza en fila 2
                                
                                updates = [
                                    {"range": f"B{index}", "values": [[nuevo_sector.upper()]]},
                                    {"range": f"C{index}", "values": [[nuevo_nombre.upper()]]},
                                    {"range": f"D{index}", "values": [[nueva_direccion.upper()]]},
                                    {"range": f"E{index}", "values": [[nuevo_telefono]]},
                                    {"range": f"F{index}", "values": [[nuevo_precinto]]}
                                ]
                                
                                success, error = api_manager.safe_sheet_operation(
                                    batch_update_sheet,
                                    sheet_clientes,
                                    updates,
                                    is_batch=True
                                )
                                
                                if success:
                                    st.success("✅ Cliente actualizado correctamente.")
                                    st.cache_data.clear()
                                    time.sleep(3)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error al actualizar: {error}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error inesperado: {str(e)}")
                else:
                    st.warning("⚠️ Cliente no encontrado.")

            # Formulario para nuevo cliente
            st.markdown("---")
            st.subheader("🆕 Cargar nuevo cliente")

            with st.form("form_nuevo_cliente", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_nro = st.text_input("🔢 N° de Cliente (nuevo)", placeholder="Número único").strip()
                    nuevo_sector = st.text_input("🏙️ Sector", placeholder="Zona o sector")
                with col2:
                    nuevo_nombre = st.text_input("👤 Nombre", placeholder="Nombre completo")
                    nueva_direccion = st.text_input("📍 Dirección", placeholder="Dirección completa")
                
                nuevo_telefono = st.text_input("📞 Teléfono", placeholder="Número de contacto")
                nuevo_precinto = st.text_input("🔒 N° de Precinto (opcional)", placeholder="Número de precinto")

                guardar_cliente = st.form_submit_button("💾 Guardar nuevo cliente", use_container_width=True)

                if guardar_cliente:
                    if not nuevo_nro or not nuevo_nombre:
                        st.error("⚠️ Debés ingresar al menos el N° de cliente y el nombre.")
                    elif nuevo_nro in df_clientes["Nº Cliente"].values:
                        st.warning("⚠️ Este cliente ya existe.")
                    else:
                        with st.spinner("Guardando nuevo cliente..."):
                            try:
                                nueva_fila = [
                                    nuevo_nro, nuevo_sector.upper(), nuevo_nombre.upper(),
                                    nueva_direccion.upper(), nuevo_telefono, nuevo_precinto
                                ]
                                
                                success, error = api_manager.safe_sheet_operation(
                                    sheet_clientes.append_row,
                                    nueva_fila
                                )
                                
                                if success:
                                    st.success("✅ Nuevo cliente agregado correctamente.")
                                    st.cache_data.clear()
                                    time.sleep(3)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error al guardar: {error}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error inesperado: {str(e)}")
        else:
            st.warning("🔒 Solo los administradores pueden editar información de clientes")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# SECCIÓN 4: IMPRIMIR RECLAMOS
# --------------------------

elif opcion == "Imprimir reclamos" and has_permission('imprimir_reclamos'):
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🖨️ Seleccionar reclamos para imprimir (formato técnico compacto)")

    try:
        # Preparar datos con manejo robusto de fechas
        df_pdf = df_reclamos.copy()
        
        # Convertir fechas y manejar posibles errores
        df_pdf["Fecha y hora"] = pd.to_datetime(
            df_pdf["Fecha y hora"],
            dayfirst=True,  # Para formato dd/mm/yyyy
            errors='coerce'  # Convierte errores a NaT
        )
        
        # Merge con datos del cliente
        df_merged = pd.merge(
            df_pdf, 
            df_clientes[["Nº Cliente", "N° de Precinto"]], 
            on="Nº Cliente", 
            how="left", 
            suffixes=("", "_cliente")
        )

        # Función para formatear fechas
        def format_fecha(fecha):
            if pd.isna(fecha):
                return "Fecha no disponible"
            try:
                return fecha.strftime('%d/%m/%Y %H:%M:%S')
            except:
                return "Fecha inválida"

        # Mostrar reclamos pendientes con fechas formateadas
        with st.expander("🕒 Reclamos pendientes de resolución", expanded=True):
            df_pendientes = df_merged[df_merged["Estado"] == "Pendiente"]
            if not df_pendientes.empty:
                # Crear copia para mostrar con fechas formateadas
                df_pendientes_display = df_pendientes.copy()
                df_pendientes_display["Fecha y hora"] = df_pendientes_display["Fecha y hora"].apply(format_fecha)
                
                st.dataframe(
                    df_pendientes_display[["Fecha y hora", "Nº Cliente", "Nombre", "Dirección", "Sector", "Tipo de reclamo"]], 
                    use_container_width=True
                )
            else:
                st.success("✅ No hay reclamos pendientes actualmente.")

        solo_pendientes = st.checkbox("🧾 Mostrar solo reclamos pendientes para imprimir", value=True)

        # --- IMPRIMIR POR TIPO DE RECLAMO ---
        st.markdown("### 🧾 Imprimir reclamos por tipo")
        
        tipos_disponibles = sorted(df_merged["Tipo de reclamo"].unique())
        tipos_seleccionados = st.multiselect(
            "Seleccioná tipos de reclamo a imprimir", 
            tipos_disponibles,
            default=tipos_disponibles[0] if tipos_disponibles else None
        )

        if tipos_seleccionados:
            reclamos_filtrados = df_merged[
                (df_merged["Estado"] == "Pendiente") & 
                (df_merged["Tipo de reclamo"].isin(tipos_seleccionados))
            ]

            if not reclamos_filtrados.empty:
                st.success(f"Se encontraron {len(reclamos_filtrados)} reclamos pendientes de los tipos seleccionados.")

                if st.button("📄 Generar PDF de reclamos por tipo", key="pdf_tipo"):
                    with st.spinner("Generando PDF..."):
                        buffer = io.BytesIO()
                        c = canvas.Canvas(buffer, pagesize=A4)
                        width, height = A4
                        y = height - 40
                        
                        # Encabezado
                        c.setFont("Helvetica-Bold", 18)
                        c.drawString(40, y, f"RECLAMOS PENDIENTES - {datetime.now().strftime('%d/%m/%Y')}")
                        y -= 30
                        
                        for i, (_, reclamo) in enumerate(reclamos_filtrados.iterrows()):
                            c.setFont("Helvetica-Bold", 16)
                            c.drawString(40, y, f"#{reclamo['Nº Cliente']} - {reclamo['Nombre']}")
                            y -= 15
                            c.setFont("Helvetica", 13)
                            
                            # Formatear fecha para PDF
                            fecha_pdf = format_fecha(reclamo['Fecha y hora'])
                            
                            lineas = [
                                f"Fecha: {fecha_pdf}",
                                f"Dirección: {reclamo['Dirección']} - Tel: {reclamo['Teléfono']}",
                                f"Sector: {reclamo['Sector']} - Precinto: {reclamo.get('N° de Precinto', 'N/A')}",
                                f"Tipo: {reclamo['Tipo de reclamo']}",
                                f"Detalles: {reclamo['Detalles'][:100]}..." if len(reclamo['Detalles']) > 100 else f"Detalles: {reclamo['Detalles']}",
                            ]
                            
                            for linea in lineas:
                                c.drawString(40, y, linea)
                                y -= 12
                            
                            y -= 8
                            c.line(40, y, width-40, y)
                            y -= 15
                            
                            if y < 100 and i < len(reclamos_filtrados) - 1:
                                agregar_pie_pdf(c, width, height)
                                c.showPage()
                                y = height - 40
                                c.setFont("Helvetica-Bold", 18)
                                c.drawString(40, y, f"RECLAMOS PENDIENTES (cont.) - {datetime.now().strftime('%d/%m/%Y')}")
                                y -= 30

                        agregar_pie_pdf(c, width, height)
                        c.save()
                        buffer.seek(0)
                        
                        st.download_button(
                            label="📥 Descargar PDF filtrado por tipo",
                            data=buffer,
                            file_name=f"reclamos_{'_'.join(tipos_seleccionados)}.pdf",
                            mime="application/pdf"
                        )
            else:
                st.info("No hay reclamos pendientes para los tipos seleccionados.")

        # --- SELECCIÓN MANUAL ---
        st.markdown("### 📋 Selección manual de reclamos")
        
        if solo_pendientes:
            df_merged = df_merged[df_merged["Estado"] == "Pendiente"]

        selected = st.multiselect(
            "Seleccioná los reclamos a imprimir:", 
            df_merged.index,
            format_func=lambda x: f"{df_merged.at[x, 'Nº Cliente']} - {df_merged.at[x, 'Nombre']}",
            key="multiselect_reclamos"
        )

        if st.button("📄 Generar PDF con seleccionados", key="pdf_manual") and selected:
            with st.spinner("Generando PDF..."):
                buffer = io.BytesIO()
                c = canvas.Canvas(buffer, pagesize=A4)
                width, height = A4
                y = height - 40
                
                # Encabezado
                c.setFont("Helvetica-Bold", 18)
                c.drawString(40, y, f"RECLAMOS SELECCIONADOS - {datetime.now().strftime('%d/%m/%Y')}")
                y -= 30

                for i, idx in enumerate(selected):
                    reclamo = df_merged.loc[idx]
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(40, y, f"#{reclamo['Nº Cliente']} - {reclamo['Nombre']}")
                    y -= 15
                    c.setFont("Helvetica", 13)
                    
                    # Formatear fecha para PDF
                    fecha_pdf = format_fecha(reclamo['Fecha y hora'])
                    
                    lineas = [
                        f"Fecha: {fecha_pdf}",
                        f"Dirección: {reclamo['Dirección']} - Tel: {reclamo['Teléfono']}",
                        f"Sector: {reclamo['Sector']} - Precinto: {reclamo.get('N° de Precinto', 'N/A')}",
                        f"Tipo: {reclamo['Tipo de reclamo']}",
                        f"Detalles: {reclamo['Detalles'][:100]}..." if len(reclamo['Detalles']) > 100 else f"Detalles: {reclamo['Detalles']}",
                    ]
                    
                    for linea in lineas:
                        c.drawString(40, y, linea)
                        y -= 12
                    
                    y -= 8
                    c.line(40, y, width-40, y)
                    y -= 15
                    
                    if y < 100 and i < len(selected) - 1:
                        agregar_pie_pdf(c, width, height)
                        c.showPage()
                        y = height - 40
                        c.setFont("Helvetica-Bold", 18)
                        c.drawString(40, y, f"RECLAMOS SELECCIONADOS (cont.) - {datetime.now().strftime('%d/%m/%Y')}")
                        y -= 30

                agregar_pie_pdf(c, width, height)
                c.save()
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Descargar PDF seleccionados",
                    data=buffer,
                    file_name="reclamos_seleccionados.pdf",
                    mime="application/pdf"
                )

        elif not selected:
            st.info("Seleccioná al menos un reclamo para generar el PDF.")

        # --- EXPORTAR TODOS LOS ACTIVOS ---
        st.markdown("### 📦 Exportar todos los reclamos 'Pendiente' y 'En curso'")

        todos_filtrados = df_merged[df_merged["Estado"].isin(["Pendiente", "En curso"])].copy()

        if not todos_filtrados.empty:
            if st.button("📄 Generar PDF de todos los reclamos activos", key="pdf_todos"):
                with st.spinner("Generando PDF completo..."):
                    buffer = io.BytesIO()
                    c = canvas.Canvas(buffer, pagesize=A4)
                    width, height = A4
                    y = height - 40

                    c.setFont("Helvetica-Bold", 18)
                    c.drawString(40, y, f"TODOS LOS RECLAMOS ACTIVOS - {datetime.now().strftime('%d/%m/%Y')}")
                    y -= 30

                    for i, (_, reclamo) in enumerate(todos_filtrados.iterrows()):
                        c.setFont("Helvetica-Bold", 16)
                        c.drawString(40, y, f"#{reclamo['Nº Cliente']} - {reclamo['Nombre']}")
                        y -= 15
                        c.setFont("Helvetica", 13)
                        
                        # Formatear fecha para PDF
                        fecha_pdf = format_fecha(reclamo['Fecha y hora'])
                        
                        lineas = [
                            f"Fecha: {fecha_pdf}",
                            f"Dirección: {reclamo['Dirección']} - Tel: {reclamo['Teléfono']}",
                            f"Sector: {reclamo['Sector']} - Precinto: {reclamo.get('N° de Precinto', 'N/A')}",
                            f"Tipo: {reclamo['Tipo de reclamo']}",
                            f"Detalles: {reclamo['Detalles'][:100]}..." if len(reclamo['Detalles']) > 100 else f"Detalles: {reclamo['Detalles']}",
                        ]
                        for linea in lineas:
                            c.drawString(40, y, linea)
                            y -= 12

                        y -= 10
                        c.line(40, y, width-40, y)
                        y -= 15

                        if y < 100:
                            agregar_pie_pdf(c, width, height)
                            c.showPage()
                            y = height - 40
                            c.setFont("Helvetica-Bold", 18)
                            c.drawString(40, y, f"RECLAMOS ACTIVOS (cont.) - {datetime.now().strftime('%d/%m/%Y')}")
                            y -= 30

                    agregar_pie_pdf(c, width, height)
                    c.save()
                    buffer.seek(0)

                    st.download_button(
                        label="📥 Descargar TODOS los reclamos activos en PDF",
                        data=buffer,
                        file_name="reclamos_activos_completo.pdf",
                        mime="application/pdf"
                    )
        else:
            st.info("🎉 No hay reclamos activos actualmente.")

    except Exception as e:
        st.error(f"❌ Error al generar PDF: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# SECCIÓN 5: PLANIFICACIÓN DE GRUPOS DE TRABAJO
# --------------------------

elif opcion == "Seguimiento técnico" and user_role == 'admin':
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🧭 Asignación de reclamos a grupos de trabajo")

    # Inicialización de variables de sesión
    if "asignaciones_grupos" not in st.session_state:
        st.session_state.asignaciones_grupos = {
            "Grupo A": [],
            "Grupo B": [],
            "Grupo C": [],
            "Grupo D": []
        }

    if "tecnicos_grupos" not in st.session_state:
        st.session_state.tecnicos_grupos = {
            "Grupo A": [],
            "Grupo B": [],
            "Grupo C": [],
            "Grupo D": []
        }

    # Configuración de grupos
    grupos_activos = st.slider("🛠️ Cantidad de grupos de trabajo activos", 1, 4, 2)

    # Asignación de técnicos
    st.markdown("### 👥 Asignar técnicos a cada grupo")
    for grupo in list(st.session_state.tecnicos_grupos.keys())[:grupos_activos]:
        st.session_state.tecnicos_grupos[grupo] = st.multiselect(
            f"{grupo} - Técnicos asignados",
            TECNICOS_DISPONIBLES,
            default=st.session_state.tecnicos_grupos[grupo],
            key=f"tecnicos_{grupo}"
        )

    st.markdown("---")
    st.markdown("### 📋 Reclamos pendientes para asignar")

    # Preparación de datos de reclamos
    df_pendientes = df_reclamos[df_reclamos["Estado"] == "Pendiente"].copy()
    df_pendientes["id"] = df_pendientes["Nº Cliente"].astype(str).str.strip()
    
    # Manejo mejorado de fechas
    df_pendientes["Fecha y hora"] = pd.to_datetime(
        df_pendientes["Fecha y hora"],
        dayfirst=True,
        format='mixed',
        errors='coerce'
    )
    
    # Función auxiliar para formatear fechas
    def format_fecha(fecha):
        if pd.isna(fecha):
            return "Sin fecha"
        try:
            return fecha.strftime('%d/%m/%Y')
        except:
            return "Fecha inválida"

    # Ordenamiento de reclamos
    orden = st.selectbox("📊 Ordenar reclamos por:", ["Fecha más reciente", "Sector", "Tipo de reclamo"])
    if orden == "Fecha más reciente":
        df_pendientes = df_pendientes.sort_values("Fecha y hora", ascending=False)
    elif orden == "Sector":
        df_pendientes = df_pendientes.sort_values("Sector")
    elif orden == "Tipo de reclamo":
        df_pendientes = df_pendientes.sort_values("Tipo de reclamo")

    # Filtrado de reclamos disponibles
    asignados = [r for reclamos in st.session_state.asignaciones_grupos.values() for r in reclamos]
    df_disponibles = df_pendientes[~df_pendientes["id"].isin(asignados)]

    # Visualización de reclamos disponibles
    for idx, row in df_disponibles.iterrows():
        with st.container():
            col1, *cols_grupo = st.columns([4] + [1]*grupos_activos)
            fecha_formateada = format_fecha(row["Fecha y hora"])
            resumen = f"📍 Sector {row['Sector']} - {row['Tipo de reclamo'].capitalize()} - {fecha_formateada}"
            col1.markdown(f"**{resumen}**")

            for i, grupo in enumerate(["Grupo A", "Grupo B", "Grupo C", "Grupo D"][:grupos_activos]):
                tecnicos = st.session_state.tecnicos_grupos[grupo]
                tecnicos_str = ", ".join(tecnicos[:2]) + ("..." if len(tecnicos) > 2 else "") if tecnicos else "Sin técnicos"
                boton_label = f"➕ {grupo[-1]} ({tecnicos_str})"
                boton_color = "primary" if tecnicos else "secondary"
                if cols_grupo[i].button(boton_label, key=f"asignar_{grupo}_{row['id']}", type=boton_color):
                    if row["id"] not in asignados:
                        st.session_state.asignaciones_grupos[grupo].append(row["id"])
                        st.rerun()

            with col1.expander("ℹ️ Ver detalles"):
                st.markdown(f"**🧾 Nº Cliente:** {row['Nº Cliente']}")
                st.markdown(f"**👤 Nombre:** {row['Nombre']}")
                st.markdown(f"**📍 Dirección:** {row['Dirección']}")
                st.markdown(f"**📞 Teléfono:** {row['Teléfono']}")
                if row.get("Detalles"):
                    st.markdown(f"**📝 Detalles:** {row['Detalles'][:250]}{'...' if len(row['Detalles']) > 250 else ''}")
                
                # Mostrar fecha completa en los detalles
                fecha_completa = format_fecha(row["Fecha y hora"]) if pd.isna(row["Fecha y hora"]) else row["Fecha y hora"].strftime('%d/%m/%Y %H:%M:%S')
                st.markdown(f"**📅 Fecha completa:** {fecha_completa}")

            st.divider()

    st.markdown("---")
    st.markdown("### 🧺 Reclamos asignados por grupo")

    # Visualización de reclamos asignados con manejo de errores
    for grupo in ["Grupo A", "Grupo B", "Grupo C", "Grupo D"][:grupos_activos]:
        reclamos_ids = st.session_state.asignaciones_grupos[grupo]
        tecnicos = st.session_state.tecnicos_grupos[grupo]
        st.markdown(f"#### 🛠️ {grupo} - Técnicos: {', '.join(tecnicos) if tecnicos else 'Sin asignar'} ({len(reclamos_ids)} reclamos)")

        if reclamos_ids:
            for reclamo_id in reclamos_ids:
                # Verificar si el reclamo todavía existe en df_pendientes
                reclamo_data = df_pendientes[df_pendientes["id"] == reclamo_id]
                
                col1, col2 = st.columns([5, 1])
                if not reclamo_data.empty:
                    row = reclamo_data.iloc[0]
                    fecha_formateada = format_fecha(row["Fecha y hora"])
                    resumen = f"📍 Sector {row['Sector']} - {row['Tipo de reclamo'].capitalize()} - {fecha_formateada}"
                    col1.markdown(f"**{resumen}**")
                else:
                    # Si el reclamo ya no está en pendientes, mostramos solo el ID
                    col1.markdown(f"**Reclamo ID: {reclamo_id} (ya no está pendiente)**")
                
                if col2.button("❌ Quitar", key=f"quitar_{grupo}_{reclamo_id}"):
                    st.session_state.asignaciones_grupos[grupo].remove(reclamo_id)
                    st.rerun()
                
                st.divider()
        else:
            st.info("Este grupo no tiene reclamos asignados.")

    st.markdown("---")

    # Botón para guardar asignaciones con manejo mejorado
    if st.button("💾 Guardar asignaciones en Google Sheets", use_container_width=True):
        actualizaciones = []
        reclamos_a_actualizar = []
        
        # Recolectar información para actualizar
        for grupo, reclamos in st.session_state.asignaciones_grupos.items():
            tecnicos = st.session_state.tecnicos_grupos[grupo]
            for reclamo_id in reclamos:
                idx = df_reclamos[df_reclamos["Nº Cliente"].astype(str).str.strip() == reclamo_id].index
                if not idx.empty:
                    row_idx = idx[0] + 2
                    actualizaciones.append({
                        "range": f"I{row_idx}", 
                        "values": [["En curso"]]
                    })
                    actualizaciones.append({
                        "range": f"J{row_idx}", 
                        "values": [[", ".join(tecnicos).upper()]]
                    })
                    reclamos_a_actualizar.append(reclamo_id)

        if actualizaciones:
            with st.spinner("Actualizando en Sheets..."):
                success, error = api_manager.safe_sheet_operation(
                    batch_update_sheet,
                    sheet_reclamos,
                    actualizaciones,
                    is_batch=True
                )
                if success:
                    st.success("✅ Reclamos actualizados como 'En curso'")
                    # Limpiar solo los reclamos que fueron actualizados
                    for grupo in st.session_state.asignaciones_grupos:
                        st.session_state.asignaciones_grupos[grupo] = [
                            r for r in st.session_state.asignaciones_grupos[grupo] 
                            if r not in reclamos_a_actualizar
                        ]
                    # Limpiar caché y rerun
                    st.cache_data.clear()
                    time.sleep(3)
                    st.rerun()
                else:
                    st.error(f"❌ Error: {error}")
        else:
            st.warning("⚠️ No hay asignaciones para guardar.")

    # Generación de PDF (se mantiene igual)
    if st.button("📄 Generar PDF de asignaciones por grupo", use_container_width=True):
        with st.spinner("Generando PDF..."):
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 40

            for grupo in ["Grupo A", "Grupo B", "Grupo C", "Grupo D"][:grupos_activos]:
                reclamos_ids = st.session_state.asignaciones_grupos[grupo]
                tecnicos = st.session_state.tecnicos_grupos[grupo]

                if not reclamos_ids:
                    continue

                # SALTO DE PÁGINA por grupo
                agregar_pie_pdf(c, width, height)
                c.showPage()
                y = height - 40

                c.setFont("Helvetica-Bold", 16)
                c.drawString(40, y, f"{grupo} - Técnicos: {', '.join(tecnicos)}")
                y -= 25

                for reclamo_id in reclamos_ids:
                    reclamo_data = df_pendientes[df_pendientes["id"] == reclamo_id]
                    if not reclamo_data.empty:
                        reclamo = reclamo_data.iloc[0]
                        c.setFont("Helvetica-Bold", 14)
                        c.drawString(40, y, f"{reclamo['Nº Cliente']} - {reclamo['Nombre']}")
                        y -= 15
                        c.setFont("Helvetica", 11)
                        
                        # Formatear fecha para PDF
                        fecha_pdf = format_fecha(reclamo["Fecha y hora"]) if pd.isna(reclamo["Fecha y hora"]) else reclamo["Fecha y hora"].strftime('%d/%m/%Y %H:%M')
                        
                        lineas = [
                            f"Fecha: {fecha_pdf}",
                            f"Dirección: {reclamo['Dirección']} - Tel: {reclamo['Teléfono']}",
                            f"Sector: {reclamo['Sector']} - Precinto: {reclamo.get('N° de Precinto', 'N/A')}",
                            f"Tipo: {reclamo['Tipo de reclamo']}",
                            f"Detalles: {reclamo['Detalles'][:100]}..." if len(reclamo['Detalles']) > 100 else f"Detalles: {reclamo['Detalles']}",
                        ]
                        for linea in lineas:
                            c.drawString(40, y, linea)
                            y -= 12

                        y -= 8
                        c.line(40, y, width - 40, y)
                        y -= 15

                        if y < 100:
                            agregar_pie_pdf(c, width, height)
                            c.showPage()
                            y = height - 40
                            c.setFont("Helvetica-Bold", 16)
                            c.drawString(40, y, f"{grupo} (cont.)")
                            y -= 25

                y -= 20

            agregar_pie_pdf(c, width, height)
            c.save()
            buffer.seek(0)

            st.download_button(
                label="📥 Descargar PDF de asignaciones",
                data=buffer,
                file_name="asignaciones_grupos.pdf",
                mime="application/pdf"
            )

    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# SECCIÓN 6: CIERRE DE RECLAMOS
# --------------------------
elif opcion == "Cierre de Reclamos" and user_role == 'admin':
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("✅ Cierre de reclamos en curso")

    def format_fecha(fecha, formato='%d/%m/%Y %H:%M:%S'):
        if pd.isna(fecha) or fecha is None:
            return "Fecha no disponible"
        try:
            if isinstance(fecha, str):
                fecha = pd.to_datetime(fecha, dayfirst=True, format='mixed')
            return fecha.strftime(formato)
        except:
            return "Fecha inválida"

    df_reclamos["Nº Cliente"] = df_reclamos["Nº Cliente"].astype(str).str.strip()
    df_reclamos["Técnico"] = df_reclamos["Técnico"].astype(str).fillna("")
    df_reclamos["Fecha y hora"] = pd.to_datetime(df_reclamos["Fecha y hora"], dayfirst=True, format='mixed', errors='coerce')

    # 👉 NUEVO: Buscar y reasignar técnico por cliente
    with st.expander("🔄 Reasignar técnico por Nº de cliente"):
        cliente_busqueda = st.text_input("🔢 Ingresá el N° de Cliente para buscar", key="buscar_cliente_tecnico").strip()
        if cliente_busqueda:
            reclamos_filtrados = df_reclamos[
                (df_reclamos["Nº Cliente"] == cliente_busqueda) &
                (df_reclamos["Estado"].isin(["Pendiente", "En curso"]))
            ]

            if not reclamos_filtrados.empty:
                reclamo = reclamos_filtrados.iloc[0]
                st.markdown(f"📌 **Reclamo encontrado:** {reclamo['Tipo de reclamo']} - Estado: {reclamo['Estado']}")
                st.markdown(f"👷 Técnico actual: `{reclamo['Técnico'] or 'No asignado'}`")

                tecnicos_actuales_raw = [t.strip().lower() for t in reclamo["Técnico"].split(",") if t.strip()]
                tecnicos_actuales = [
                    tecnico for tecnico in TECNICOS_DISPONIBLES
                    if tecnico.lower() in tecnicos_actuales_raw
                ]
                nuevo_tecnico_multiselect = st.multiselect(
                    "👷 Nuevo técnico asignado",
                    options=TECNICOS_DISPONIBLES,
                    default=tecnicos_actuales,
                    key="nuevo_tecnico_input"
                )

                if st.button("💾 Guardar nuevo técnico", key="guardar_tecnico"):
                    try:
                        fila_index = reclamo.name + 2
                        nuevo_tecnico = ", ".join(nuevo_tecnico_multiselect).upper()

                        updates = [{"range": f"J{fila_index}", "values": [[nuevo_tecnico]]}]

                        if reclamo['Estado'] == "Pendiente":
                            updates.append({"range": f"I{fila_index}", "values": [["En curso"]]})

                        success, error = api_manager.safe_sheet_operation(
                            batch_update_sheet,
                            sheet_reclamos,
                            updates,
                            is_batch=True
                        )

                        if success:
                            st.success("✅ Técnico actualizado correctamente.")
                            st.cache_data.clear()
                            time.sleep(3)
                            st.rerun()
                        else:
                            st.error(f"❌ Error al actualizar: {error}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {str(e)}")
            else:
                st.warning("⚠️ No se encontró un reclamo pendiente o en curso para ese cliente.")

    # 🔽 Parte clásica: ver y resolver reclamos en curso
    en_curso = df_reclamos[df_reclamos["Estado"] == "En curso"].copy()

    if en_curso.empty:
        st.info("📭 No hay reclamos en curso en este momento.")
    else:
        tecnicos_unicos = sorted(set(
            tecnico.strip().upper() 
            for t in en_curso["Técnico"] 
            for tecnico in t.split(",") 
            if tecnico.strip()
        ))

        tecnicos_seleccionados = st.multiselect("👷 Filtrar por técnico asignado", tecnicos_unicos, key="filtro_tecnicos")

        if tecnicos_seleccionados:
            en_curso = en_curso[
                en_curso["Técnico"].apply(lambda t: any(tecnico.strip().upper() in t.upper() for tecnico in tecnicos_seleccionados))
            ]

        st.write("### 📋 Reclamos en curso:")
        df_mostrar = en_curso[["Fecha y hora", "Nº Cliente", "Nombre", "Tipo de reclamo", "Técnico"]].copy()
        df_mostrar["Fecha y hora"] = df_mostrar["Fecha y hora"].apply(format_fecha)

        st.dataframe(df_mostrar, use_container_width=True, height=400)

        st.markdown("### ✏️ Acciones por reclamo:")

        for i, row in en_curso.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.markdown(f"**#{row['Nº Cliente']} - {row['Nombre']}**")
                    st.markdown(f"📅 {format_fecha(row['Fecha y hora'])}")
                    st.markdown(f"📌 {row['Tipo de reclamo']}")
                    st.markdown(f"👷 {row['Técnico']}")

                    cliente_id = str(row["Nº Cliente"]).strip()
                    cliente_info = df_clientes[df_clientes["Nº Cliente"] == cliente_id]
                    precinto_actual = cliente_info["N° de Precinto"].values[0] if not cliente_info.empty else ""

                    nuevo_precinto = st.text_input("🔒 Precinto", value=precinto_actual, key=f"precinto_{i}")

                with col2:
                    if st.button("✅ Resuelto", key=f"resolver_{i}", use_container_width=True):
                        with st.spinner("Cerrando reclamo..."):
                            try:
                                updates = [{"range": f"I{i + 2}", "values": [["Resuelto"]]}]

                                if len(COLUMNAS_RECLAMOS) > 12:
                                    argentina = pytz.timezone("America/Argentina/Buenos_Aires")
                                    fecha_resolucion = datetime.now(argentina).strftime("%d/%m/%Y %H:%M:%S")
                                    updates.append({"range": f"M{i + 2}", "values": [[fecha_resolucion]]})

                                if nuevo_precinto.strip() and nuevo_precinto != precinto_actual:
                                    updates.append({"range": f"F{i + 2}", "values": [[nuevo_precinto.strip()]]})

                                success, error = api_manager.safe_sheet_operation(
                                    batch_update_sheet,
                                    sheet_reclamos,
                                    updates,
                                    is_batch=True
                                )

                                if success:
                                    if nuevo_precinto.strip() and nuevo_precinto != precinto_actual and not cliente_info.empty:
                                        index_cliente_en_clientes = cliente_info.index[0] + 2
                                        success_precinto, error_precinto = api_manager.safe_sheet_operation(
                                            sheet_clientes.update,
                                            f"F{index_cliente_en_clientes}",
                                            [[nuevo_precinto.strip()]]
                                        )
                                        if not success_precinto:
                                            st.warning(f"⚠️ Precinto guardado en reclamo pero no en hoja de clientes: {error_precinto}")
                                    st.success(f"🟢 Reclamo de {row['Nombre']} cerrado correctamente.")
                                    st.cache_data.clear()
                                    time.sleep(3)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error al actualizar: {error}")
                            except Exception as e:
                                st.error(f"❌ Error inesperado: {str(e)}")

                with col3:
                    if st.button("↩️ Pendiente", key=f"volver_{i}", use_container_width=True):
                        with st.spinner("Cambiando estado..."):
                            try:
                                updates = [
                                    {"range": f"I{i + 2}", "values": [["Pendiente"]]},
                                    {"range": f"J{i + 2}", "values": [[""]]}
                                ]
                                success, error = api_manager.safe_sheet_operation(
                                    batch_update_sheet,
                                    sheet_reclamos,
                                    updates,
                                    is_batch=True
                                )
                                if success:
                                    st.success(f"🔄 Reclamo de {row['Nombre']} vuelto a PENDIENTE.")
                                    st.cache_data.clear()
                                    time.sleep(3)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Error al actualizar: {error}")
                            except Exception as e:
                                st.error(f"❌ Error inesperado: {str(e)}")

                st.divider()

    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------
# NUEVO FOOTER - RESUMEN DE LA JORNADA
# --------------------------
st.markdown("---")
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.markdown("### 📋 Resumen de la jornada")

# Función auxiliar para formatear fechas
def format_fecha(fecha, formato='%d/%m/%Y %H:%M:%S'):
    """Formatea una fecha para visualización consistente"""
    if pd.isna(fecha) or fecha is None:
        return "Fecha no disponible"
    try:
        if isinstance(fecha, str):
            fecha = pd.to_datetime(fecha, dayfirst=True, format='mixed')
        return fecha.strftime(formato)
    except:
        return "Fecha inválida"

# Procesamiento mejorado de fechas
df_reclamos["Fecha y hora"] = pd.to_datetime(
    df_reclamos["Fecha y hora"],
    dayfirst=True,
    format='mixed',
    errors='coerce'
)

# Obtener fecha actual con zona horaria
argentina = pytz.timezone("America/Argentina/Buenos_Aires")
hoy = datetime.now(argentina).date()

# Filtrar reclamos de hoy (comparando solo la parte de fecha)
df_hoy = df_reclamos[
    df_reclamos["Fecha y hora"].dt.tz_localize(None).dt.date == hoy
].copy()

# Reclamos en curso
df_en_curso = df_reclamos[df_reclamos["Estado"] == "En curso"].copy()

# Mostrar métricas
col1, col2 = st.columns(2)
col1.metric("📌 Reclamos cargados hoy", len(df_hoy))
col2.metric("⚙️ Reclamos en curso", len(df_en_curso))

# Técnicos por reclamo
st.markdown("### 👷 Reclamos en curso por técnicos")

if not df_en_curso.empty and "Técnico" in df_en_curso.columns:
    # Normalizar nombres y filtrar no vacíos
    df_en_curso["Técnico"] = df_en_curso["Técnico"].fillna("").astype(str)
    df_en_curso = df_en_curso[df_en_curso["Técnico"].str.strip() != ""]

    # Crear un set inmutable de técnicos asignados por reclamo (para detectar duplicados)
    df_en_curso["tecnicos_set"] = df_en_curso["Técnico"].apply(
        lambda x: tuple(sorted([t.strip().upper() for t in x.split(",") if t.strip()]))
    )

    # Agrupar por ese conjunto de técnicos
    conteo_grupos = df_en_curso.groupby("tecnicos_set").size().reset_index(name="Cantidad")

    # Mostrar estadísticas
    if not conteo_grupos.empty:
        st.markdown("#### Distribución de trabajo:")
        for fila in conteo_grupos.itertuples():
            tecnicos = ", ".join(fila.tecnicos_set)
            st.markdown(f"- 👥 **{tecnicos}**: {fila.Cantidad} reclamos")
        
        # Mostrar reclamos más antiguos pendientes
        reclamos_antiguos = df_en_curso.sort_values("Fecha y hora").head(3)
        if not reclamos_antiguos.empty:
            st.markdown("#### ⏳ Reclamos más antiguos aún en curso:")
            for _, row in reclamos_antiguos.iterrows():
                fecha_formateada = format_fecha(row["Fecha y hora"])
                st.markdown(
                    f"- **{row['Nombre']}** ({row['Nº Cliente']}) - " 
                    f"Desde: {fecha_formateada} - "
                    f"Técnicos: {row['Técnico']}"
                )
    else:
        st.info("No hay técnicos asignados actualmente a reclamos en curso.")
else:
    st.info("No hay reclamos en curso en este momento.")

# Mostrar fecha y hora actual del sistema
st.markdown(f"*Última actualización: {datetime.now(argentina).strftime('%d/%m/%Y %H:%M:%S')}*")

st.markdown('</div>', unsafe_allow_html=True)
