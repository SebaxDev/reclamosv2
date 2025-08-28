# components/reclamos/nuevo.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.date_utils import ahora_argentina, format_fecha, parse_fecha
from utils.api_manager import api_manager
from utils.data_manager import batch_update_sheet
from config.settings import (
    SECTORES_DISPONIBLES,
    TIPOS_RECLAMO,
    DEBUG_MODE
)

# --- FUNCIONES HELPER NUEVAS ---
def _normalizar_datos(df_clientes, df_reclamos, nro_cliente):
    """Normaliza datos solo cuando es necesario"""
    if not nro_cliente:
        return df_clientes, df_reclamos
    
    df_clientes_normalizado = df_clientes.copy()
    df_reclamos_normalizado = df_reclamos.copy()
    
    df_clientes_normalizado["Nº Cliente"] = df_clientes_normalizado["Nº Cliente"].astype(str).str.strip()
    df_reclamos_normalizado["Nº Cliente"] = df_reclamos_normalizado["Nº Cliente"].astype(str).str.strip()
    
    return df_clientes_normalizado, df_reclamos_normalizado

def _validar_y_normalizar_sector(sector_input):
    """Valida y normaliza el sector ingresado"""
    try:
        sector_limpio = str(sector_input).strip()
        sector_num = int(sector_limpio)
        
        if 1 <= sector_num <= 17:
            return str(sector_num), None
        else:
            return None, f"⚠️ El sector debe estar entre 1 y 17. Se ingresó: {sector_num}"
            
    except ValueError:
        return None, f"⚠️ El sector debe ser un número válido. Se ingresó: {sector_input}"

def _verificar_reclamos_activos(nro_cliente, df_reclamos):
    """Verifica reclamos activos de forma eficiente"""
    if nro_cliente not in df_reclamos["Nº Cliente"].values:
        return pd.DataFrame()
    
    reclamos_cliente = df_reclamos[df_reclamos["Nº Cliente"] == nro_cliente]
    
    # Convertir estados a minúsculas para comparación case-insensitive
    estados_activos = ["pendiente", "en curso", "desconexión"]
    reclamos_activos = reclamos_cliente[
        reclamos_cliente["Estado"].str.strip().str.lower().isin(estados_activos) |
        (reclamos_cliente["Tipo de reclamo"].str.strip().str.lower() == "Desconexion a Pedido")
    ]
    
    return reclamos_activos

def generar_id_unico():
    """Genera un ID único para reclamos"""
    import uuid
    return str(uuid.uuid4())[:8].upper()

# --- FUNCIÓN PRINCIPAL OPTIMIZADA ---
def render_nuevo_reclamo(df_reclamos, df_clientes, sheet_reclamos, sheet_clientes, current_user=None):
    """
    Muestra la sección para cargar nuevos reclamos con diseño CRM moderno
    """
    # Header moderno
    st.markdown("""
    <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <span class="mr-3">📝</span> Cargar nuevo reclamo
        </h2>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
            Complete el formulario para registrar un nuevo reclamo técnico
        </p>
    </div>
    """, unsafe_allow_html=True)

    estado = {
        'nro_cliente': '',
        'cliente_existente': None,
        'formulario_bloqueado': False,
        'reclamo_guardado': False,
        'cliente_nuevo': False
    }

    # Campo de número de cliente con diseño mejorado
    st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🔢 N° de Cliente</label>', unsafe_allow_html=True)
    estado['nro_cliente'] = st.text_input(
        "", 
        placeholder="Ingresa el número de cliente",
        label_visibility="collapsed",
        key="nro_cliente_input"
    ).strip()

    if estado['nro_cliente']:
        # Normalizar datos solo cuando sea necesario
        df_clientes_norm, df_reclamos_norm = _normalizar_datos(
            df_clientes, df_reclamos, estado['nro_cliente']
        )
        
        # Buscar cliente
        match = df_clientes_norm[df_clientes_norm["Nº Cliente"] == estado['nro_cliente']]
        
        if not match.empty:
            estado['cliente_existente'] = match.iloc[0].to_dict()
            st.markdown("""
            <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <div class="flex items-center">
                    <span class="text-green-600 text-lg mr-2">✅</span>
                    <span class="text-green-800 font-medium">Cliente reconocido, datos auto-cargados.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            estado['cliente_nuevo'] = True
            st.markdown("""
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div class="flex items-center">
                    <span class="text-blue-600 text-lg mr-2">ℹ️</span>
                    <span class="text-blue-800">Este cliente no existe en la base y se cargará como cliente nuevo.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Verificar reclamos activos
        reclamos_activos = _verificar_reclamos_activos(estado['nro_cliente'], df_reclamos_norm)
        
        if not reclamos_activos.empty:
            estado['formulario_bloqueado'] = True
            st.markdown("""
            <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <div class="flex items-center">
                    <span class="text-red-600 text-lg mr-2">⚠️</span>
                    <span class="text-red-800 font-medium">Este cliente ya tiene un reclamo sin resolver o una desconexión activa.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mostrar reclamos activos
            for _, reclamo in reclamos_activos.iterrows():
                with st.expander(f"🔍 Reclamo activo - {format_fecha(reclamo['Fecha y hora'], '%d/%m/%Y %H:%M')}", expanded=False):
                    st.markdown(f"""
                    <div class="bg-gray-50 rounded-lg p-4">
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <p class="text-sm text-gray-600">👤 Cliente</p>
                                <p class="font-medium">{reclamo.get('Nombre', 'N/A')}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">📌 Tipo</p>
                                <p class="font-medium">{reclamo.get('Tipo de reclamo', 'N/A')}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">📝 Detalles</p>
                                <p class="font-medium">{reclamo.get('Detalles', 'N/A')[:200]}...</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">⚙️ Estado</p>
                                <p class="font-medium">{reclamo.get('Estado', 'Sin estado')}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    if estado['reclamo_guardado']:
        st.markdown("""
        <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <div class="flex items-center">
                <span class="text-green-600 text-lg mr-2">✅</span>
                <span class="text-green-800 font-medium">Reclamo registrado correctamente.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif not estado['formulario_bloqueado']:
        estado = _mostrar_formulario_reclamo(estado, df_clientes, sheet_reclamos, sheet_clientes, current_user)

    return estado

# --- FUNCIÓN DE FORMULARIO MEJORADA ---
def _mostrar_formulario_reclamo(estado, df_clientes, sheet_reclamos, sheet_clientes, current_user):
    """Muestra y procesa el formulario de nuevo reclamo con diseño moderno"""
    
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">📋 Información del Reclamo</h3>
    """, unsafe_allow_html=True)
    
    with st.form("reclamo_formulario", clear_on_submit=False):
        col1, col2 = st.columns(2)

        # Datos del cliente (existe o nuevo)
        if estado['cliente_existente']:
            cliente_data = estado['cliente_existente']
            
            with col1:
                st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">👤 Nombre del Cliente</label>', unsafe_allow_html=True)
                nombre = st.text_input(
                    "",
                    value=cliente_data.get("Nombre", ""),
                    label_visibility="collapsed",
                    key="nombre_cliente"
                )
                
                st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📍 Dirección</label>', unsafe_allow_html=True)
                direccion = st.text_input(
                    "",
                    value=cliente_data.get("Dirección", ""),
                    label_visibility="collapsed",
                    key="direccion_cliente"
                )

            with col2:
                st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📞 Teléfono</label>', unsafe_allow_html=True)
                telefono = st.text_input(
                    "",
                    value=cliente_data.get("Teléfono", ""),
                    label_visibility="collapsed",
                    key="telefono_cliente"
                )
                
                # Sector con validación mejorada
                st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🔢 Sector (1-17)</label>', unsafe_allow_html=True)
                sector_existente = cliente_data.get("Sector", "1")
                sector_normalizado, error_sector = _validar_y_normalizar_sector(sector_existente)
                
                if error_sector:
                    st.warning(error_sector)
                    sector = st.text_input("", value="1", label_visibility="collapsed", key="sector_cliente")
                else:
                    sector = st.text_input("", value=sector_normalizado, label_visibility="collapsed", key="sector_cliente")

        else:
            with col1:
                st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">👤 Nombre del Cliente</label>', unsafe_allow_html=True)
                nombre = st.text_input("", placeholder="Nombre completo", label_visibility="collapsed", key="nombre_nuevo")
                
                st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📍 Dirección</label>', unsafe_allow_html=True)
                direccion = st.text_input("", placeholder="Dirección completa", label_visibility="collapsed", key="direccion_nuevo")
            
            with col2:
                st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📞 Teléfono</label>', unsafe_allow_html=True)
                telefono = st.text_input("", placeholder="Número de contacto", label_visibility="collapsed", key="telefono_nuevo")
                
                st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🔢 Sector (1-17)</label>', unsafe_allow_html=True)
                sector = st.text_input("", placeholder="Ej: 5", label_visibility="collapsed", key="sector_nuevo")

        # Campos del reclamo
        st.markdown("""
        <div class="mt-6">
            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-4">📋 Detalles del Reclamo</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📌 Tipo de Reclamo</label>', unsafe_allow_html=True)
        tipo_reclamo = st.selectbox("", TIPOS_RECLAMO, label_visibility="collapsed", key="tipo_reclamo")
        
        st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📝 Detalles del Reclamo</label>', unsafe_allow_html=True)
        detalles = st.text_area("", placeholder="Describe el problema...", height=100, label_visibility="collapsed", key="detalles_reclamo")

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🔒 N° de Precinto (opcional)</label>', unsafe_allow_html=True)
            precinto = st.text_input(
                "",
                value=estado['cliente_existente'].get("N° de Precinto", "") if estado['cliente_existente'] else "",
                placeholder="Número de precinto",
                label_visibility="collapsed",
                key="precinto_cliente"
            )
        
        with col4:
            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">👤 Atendido por</label>', unsafe_allow_html=True)
            atendido_por = st.text_input(
                "", 
                placeholder="Nombre de quien atiende", 
                value=current_user or "",
                label_visibility="collapsed",
                key="atendido_por"
            )

        # Botón de envío con diseño moderno
        enviado = st.form_submit_button(
            "💾 Guardar Reclamo", 
            use_container_width=True,
            type="primary"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if enviado:
        estado = _procesar_envio_formulario(
            estado, nombre, direccion, telefono, sector, 
            tipo_reclamo, detalles, precinto, atendido_por,
            df_clientes, sheet_reclamos, sheet_clientes
        )
    
    return estado

# --- FUNCIÓN DE PROCESAMIENTO OPTIMIZADA ---
def _procesar_envio_formulario(estado, nombre, direccion, telefono, sector, tipo_reclamo, 
                              detalles, precinto, atendido_por, df_clientes, sheet_reclamos, sheet_clientes):
    """Procesa el envío del formulario de manera optimizada"""
    
    # Validar campos obligatorios
    campos_obligatorios = {
        "Nombre": nombre.strip(),
        "Dirección": direccion.strip(),
        "Sector": str(sector).strip(),
        "Tipo de reclamo": tipo_reclamo.strip(),
        "Atendido por": atendido_por.strip()
    }
    
    campos_vacios = [campo for campo, valor in campos_obligatorios.items() if not valor]
    
    if campos_vacios:
        st.markdown(f"""
        <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <div class="flex items-center">
                <span class="text-red-600 text-lg mr-2">❌</span>
                <span class="text-red-800">Campos obligatorios vacíos: {', '.join(campos_vacios)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return estado

    # Validar y normalizar sector
    sector_normalizado, error_sector = _validar_y_normalizar_sector(sector)
    if error_sector:
        st.error(error_sector)
        return estado

    # Mostrar loading state
    with st.spinner("💾 Guardando reclamo..."):
        try:
            # Preparar datos del reclamo
            fecha_hora = ahora_argentina()
            
            # ✅ CORRECCIÓN: Desconexiones a Pedido se guardan con estado "Desconexión"
            if tipo_reclamo.lower() == "Desconexion a Pedido":
                estado_reclamo = "Desconexión"
            else:
                estado_reclamo = "Pendiente"
                
            id_reclamo = generar_id_unico()

            fila_reclamo = [
                format_fecha(fecha_hora),
                estado['nro_cliente'],
                sector_normalizado,
                nombre.upper(),
                direccion.upper(),
                telefono.strip(),
                tipo_reclamo,
                detalles.upper(),
                estado_reclamo,  # ✅ Estado corregido aquí
                "",  # Técnico (vacío inicialmente)
                precinto.strip(),
                atendido_por.upper(),
                "", "", "",  # Campos adicionales
                id_reclamo
            ]

            # Guardar reclamo
            success, error = api_manager.safe_sheet_operation(
                sheet_reclamos.append_row,
                fila_reclamo
            )

            if success:
                estado.update({
                    'reclamo_guardado': True,
                    'formulario_bloqueado': True
                })
                
                st.markdown(f"""
                <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                    <div class="flex items-center">
                        <span class="text-green-600 text-lg mr-2">✅</span>
                        <div>
                            <span class="text-green-800 font-medium">Reclamo guardado correctamente</span>
                            <p class="text-green-700 text-sm">ID: {id_reclamo} - Estado: {estado_reclamo}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gestionar cliente (nuevo o actualización)
                _gestionar_cliente(
                    estado['nro_cliente'], sector_normalizado, nombre, 
                    direccion, telefono, precinto, df_clientes, sheet_clientes
                )
                
                # Notificación
                if 'notification_manager' in st.session_state:
                    st.session_state.notification_manager.add(
                        notification_type="nuevo_reclamo",
                        message=f"📝 Nuevo reclamo {id_reclamo} - {tipo_reclamo}",
                        user_target="all",
                        claim_id=id_reclamo
                    )
                
                st.cache_data.clear()

                # 🔄 Forzar recarga para limpiar el formulario y mostrar reclamo activo
                st.rerun()
                
            else:
                st.markdown(f"""
                <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                    <div class="flex items-center">
                        <span class="text-red-600 text-lg mr-2">❌</span>
                        <span class="text-red-800">Error al guardar: {error}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f"""
            <div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <div class="flex items-center">
                    <span class="text-red-600 text-lg mr-2">❌</span>
                    <span class="text-red-800">Error inesperado: {str(e)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if DEBUG_MODE:
                st.exception(e)
    
    return estado

def _gestionar_cliente(nro_cliente, sector, nombre, direccion, telefono, precinto, df_clientes, sheet_clientes):
    """Gestiona la creación o actualización del cliente"""
    cliente_existente = df_clientes[df_clientes["Nº Cliente"] == nro_cliente]
    
    if cliente_existente.empty:
        # Crear nuevo cliente
        fila_cliente = [nro_cliente, sector, nombre.upper(), direccion.upper(), telefono.strip(), precinto.strip()]
        success, _ = api_manager.safe_sheet_operation(sheet_clientes.append_row, fila_cliente)
        if success:
            st.markdown("""
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <div class="flex items-center">
                    <span class="text-blue-600 text-lg mr-2">ℹ️</span>
                    <span class="text-blue-800">Nuevo cliente registrado en la base de datos</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Actualizar cliente existente
        updates = []
        idx = cliente_existente.index[0] + 2
        
        campos_actualizar = {
            "B": ("Sector", sector),
            "C": ("Nombre", nombre.upper()),
            "D": ("Dirección", direccion.upper()),
            "E": ("Teléfono", telefono.strip()),
            "F": ("N° de Precinto", precinto.strip())
        }
        
        for col, (campo, nuevo_valor) in campos_actualizar.items():
            valor_actual = str(cliente_existente.iloc[0][campo]).strip() if campo in cliente_existente.columns else ""
            if valor_actual != nuevo_valor:
                updates.append({"range": f"{col}{idx}", "values": [[nuevo_valor]]})
        
        if updates:
            success, _ = api_manager.safe_sheet_operation(
                batch_update_sheet, sheet_clientes, updates, is_batch=True
            )
            if success:
                st.markdown("""
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                    <div class="flex items-center">
                        <span class="text-blue-600 text-lg mr-2">🔄</span>
                        <span class="text-blue-800">Datos del cliente actualizados</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)