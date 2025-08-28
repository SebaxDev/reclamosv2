# components/clientes/gestion.py
import streamlit as st
import pandas as pd
import uuid
from utils.date_utils import ahora_argentina, format_fecha, parse_fecha
from utils.api_manager import api_manager, batch_update_sheet
from config.settings import SECTORES_DISPONIBLES

# --- FUNCIONES HELPER NUEVAS ---
def _validar_telefono(telefono):
    """Valida el formato del teléfono"""
    if not telefono.strip():
        return True, ""  # Vacío es válido (opcional)
    
    telefono_limpio = telefono.strip().replace(" ", "").replace("-", "")
    if telefono_limpio.isdigit():
        return True, ""
    else:
        return False, "⚠️ El teléfono debe contener solo números, espacios o guiones."

def _valores_diferentes(valor1, valor2):
    """Compara valores de forma segura considerando strings y None"""
    str1 = str(valor1).strip() if valor1 is not None else ""
    str2 = str(valor2).strip() if valor2 is not None else ""
    return str1 != str2

def _obtener_indice_sector(sector_actual, sectores_disponibles):
    """Obtiene el índice seguro para el selectbox de sector"""
    if not sector_actual:
        return 0
        
    try:
        sector_str = str(sector_actual).strip()
        return sectores_disponibles.index(sector_str)
    except (ValueError, AttributeError):
        return 0

# --- FUNCIÓN PRINCIPAL CON DISEÑO MEJORADO ---
def render_gestion_clientes(df_clientes, df_reclamos, sheet_clientes, user_role):
    """
    Muestra la sección de gestión de clientes con diseño CRM profesional
    
    Args:
        df_clientes (pd.DataFrame): DataFrame con los clientes
        df_reclamos (pd.DataFrame): DataFrame con los reclamos
        sheet_clientes: Objeto de conexión a la hoja de clientes
        user_role (str): Rol del usuario actual
    
    Returns:
        dict: Diccionario con estado de cambios y necesidad de recarga
    """
    # Header profesional
    st.markdown("""
    <div class="mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
            <span class="mr-3">👥</span> Gestión de Clientes
        </h2>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
            Administra la información de clientes y sus datos de contacto
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Normalización de datos
    df_clientes["Nº Cliente"] = df_clientes["Nº Cliente"].astype(str).str.strip()

    cambios = False

    if user_role == 'admin':
        cambios = _mostrar_edicion_cliente(df_clientes, df_reclamos, sheet_clientes) or cambios
        st.markdown("---")
        cambios = _mostrar_nuevo_cliente(df_clientes, sheet_clientes) or cambios
    else:
        st.markdown("""
        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg mb-4">
            <div class="flex items-start">
                <span class="text-yellow-600 text-lg mr-3">🔒</span>
                <div>
                    <h4 class="text-yellow-800 font-semibold">Acceso restringido</h4>
                    <p class="text-yellow-700 text-sm">Solo los administradores pueden editar información de clientes</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    return {
        "cambios": cambios,
        "needs_refresh": cambios
    }

# --- FUNCIÓN DE EDICIÓN CON DISEÑO MEJORADO ---
def _mostrar_edicion_cliente(df_clientes, df_reclamos, sheet_clientes):
    """Muestra el formulario para editar un cliente existente con diseño profesional"""
    cambios = False

    # Filtrar solo clientes con número válido
    clientes_validos = df_clientes[
        df_clientes["Nº Cliente"].astype(str).str.strip() != ""
    ]
    
    if clientes_validos.empty:
        st.markdown("""
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
            <div class="flex items-start">
                <span class="text-blue-600 text-lg mr-3">📝</span>
                <p class="text-blue-700">No hay clientes registrados para editar</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return cambios

    clientes_lista = clientes_validos["Nº Cliente"].astype(str).tolist()
    
    # Selector moderno
    st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🔍 Seleccionar cliente</label>', unsafe_allow_html=True)
    cliente_seleccionado = st.selectbox(
        "", 
        clientes_lista,
        help="Elegí el cliente que querés editar",
        label_visibility="collapsed"
    )

    if not cliente_seleccionado:
        return cambios

    # Búsqueda robusta del cliente
    cliente_actual = df_clientes[
        df_clientes["Nº Cliente"].astype(str).str.strip() == str(cliente_seleccionado).strip()
    ]
    
    if cliente_actual.empty:
        st.markdown(f"""
        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
            <div class="flex items-start">
                <span class="text-red-600 text-lg mr-3">❌</span>
                <p class="text-red-700">No se encontró el cliente {cliente_seleccionado}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return cambios

    cliente_actual = cliente_actual.iloc[0]
    
    # Header del cliente
    st.markdown(f"""
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900 rounded-xl p-4 mb-6 border border-blue-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
            <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                    📋 Editando: Cliente {cliente_seleccionado}
                </h3>
                <p class="text-gray-600 dark:text-gray-400">{cliente_actual.get('Nombre', '')}</p>
            </div>
            <span class="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                👤 Cliente activo
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    _mostrar_reclamos_cliente(cliente_seleccionado, df_reclamos)

    # Formulario de edición con diseño moderno
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">✏️ Editar información del cliente</h4>
    """, unsafe_allow_html=True)
    
    with st.form("form_editar_cliente"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🏢 Sector</label>', unsafe_allow_html=True)
            indice_sector = _obtener_indice_sector(
                cliente_actual.get("Sector"), 
                SECTORES_DISPONIBLES
            )
            
            nuevo_sector = st.selectbox(
                "",
                SECTORES_DISPONIBLES,
                index=indice_sector,
                label_visibility="collapsed"
            )

            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">👤 Nombre *</label>', unsafe_allow_html=True)
            nuevo_nombre = st.text_input(
                "",
                value=cliente_actual.get("Nombre", ""),
                help="Campo obligatorio",
                label_visibility="collapsed"
            )

            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📍 Dirección *</label>', unsafe_allow_html=True)
            nueva_direccion = st.text_input(
                "",
                value=cliente_actual.get("Dirección", ""),
                help="Campo obligatorio",
                label_visibility="collapsed"
            )

        with col2:
            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📞 Teléfono</label>', unsafe_allow_html=True)
            nuevo_telefono = st.text_input(
                "",
                value=cliente_actual.get("Teléfono", ""),
                help="Opcional - solo números, espacios o guiones",
                label_visibility="collapsed"
            )

            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🔒 Nº de Precinto</label>', unsafe_allow_html=True)
            nuevo_precinto = st.text_input(
                "",
                value=cliente_actual.get("N° de Precinto", ""),
                help="Opcional",
                label_visibility="collapsed"
            )

        # Botón de envío moderno
        submitted = st.form_submit_button(
            "💾 Guardar cambios",
            use_container_width=True,
            type="primary"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        # Validaciones
        if not nuevo_nombre.strip():
            st.markdown("""
            <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-4">
                <div class="flex items-start">
                    <span class="text-red-600 text-lg mr-3">❌</span>
                    <p class="text-red-700">El nombre del cliente es obligatorio</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return cambios
            
        if not nueva_direccion.strip():
            st.markdown("""
            <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-4">
                <div class="flex items-start">
                    <span class="text-red-600 text-lg mr-3">❌</span>
                    <p class="text-red-700">La dirección del cliente es obligatoria</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return cambios

        # Validación de teléfono
        telefono_valido, mensaje_error = _validar_telefono(nuevo_telefono)
        if not telefono_valido:
            st.markdown(f"""
            <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg mb-4">
                <div class="flex items-start">
                    <span class="text-yellow-600 text-lg mr-3">⚠️</span>
                    <p class="text-yellow-700">{mensaje_error}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Verificar consistencia con reclamos
        _verificar_cambios_desde_reclamos(
            cliente_seleccionado, 
            df_reclamos, 
            nueva_direccion.strip(), 
            nuevo_telefono.strip(), 
            nuevo_precinto.strip()
        )

        # Verificar cambios
        hubo_cambios = any([
            _valores_diferentes(nuevo_sector, cliente_actual.get("Sector")),
            _valores_diferentes(nuevo_nombre, cliente_actual.get("Nombre")),
            _valores_diferentes(nueva_direccion, cliente_actual.get("Dirección")),
            _valores_diferentes(nuevo_telefono, cliente_actual.get("Teléfono")),
            _valores_diferentes(nuevo_precinto, cliente_actual.get("N° de Precinto"))
        ])

        if not hubo_cambios:
            st.markdown("""
            <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
                <div class="flex items-start">
                    <span class="text-blue-600 text-lg mr-3">ℹ️</span>
                    <p class="text-blue-700">No se detectaron cambios en los datos del cliente</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return cambios

        # Mostrar preview de cambios
        st.markdown("""
        <div class="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-4 border border-gray-200 dark:border-gray-700">
            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">📋 Resumen de cambios</h4>
        """, unsafe_allow_html=True)
        
        cambios_data = {
            "Campo": ["Sector", "Nombre", "Dirección", "Teléfono", "Precinto"],
            "Valor anterior": [
                cliente_actual.get("Sector", ""),
                cliente_actual.get("Nombre", ""), 
                cliente_actual.get("Dirección", ""),
                cliente_actual.get("Teléfono", "") or "No tiene",
                cliente_actual.get("N° de Precinto", "") or "No tiene"
            ],
            "Valor nuevo": [
                nuevo_sector,
                nuevo_nombre.strip(),
                nueva_direccion.strip(),
                nuevo_telefono.strip() or "No tiene",
                nuevo_precinto.strip() or "No tiene"
            ]
        }
        
        df_cambios = pd.DataFrame(cambios_data)
        df_cambios = df_cambios[df_cambios["Valor anterior"] != df_cambios["Valor nuevo"]]
        
        if not df_cambios.empty:
            st.dataframe(df_cambios, use_container_width=True, hide_index=True)
            
            # Confirmación final con diseño moderno
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("✅ Confirmar cambios", 
                           key=f"confirmar_{cliente_seleccionado}",
                           use_container_width=True,
                           type="primary"):
                    cambios = _actualizar_cliente(
                        df_clientes[df_clientes["Nº Cliente"].astype(str) == str(cliente_seleccionado)],
                        sheet_clientes,
                        nuevo_sector,
                        nuevo_nombre.strip(),
                        nueva_direccion.strip(),
                        nuevo_telefono.strip(),
                        nuevo_precinto.strip()
                    )
            with col2:
                if st.button("❌ Cancelar", 
                           use_container_width=True,
                           type="secondary"):
                    st.rerun()
        else:
            st.markdown("""
            <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-lg">
                <div class="flex items-start">
                    <span class="text-blue-600 text-lg mr-3">ℹ️</span>
                    <p class="text-blue-700">No se detectaron cambios</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return cambios

    return cambios

def _mostrar_reclamos_cliente(nro_cliente, df_reclamos):
    """Muestra los últimos reclamos del cliente con diseño moderno"""
    df_reclamos_cliente = df_reclamos[
        df_reclamos["Nº Cliente"] == nro_cliente
    ].copy()
    
    df_reclamos_cliente["Fecha y hora"] = df_reclamos_cliente["Fecha y hora"].apply(
        parse_fecha
    )
    
    df_reclamos_cliente = df_reclamos_cliente.sort_values(
        "Fecha y hora", 
        ascending=False
    ).head(3)
    
    with st.expander("📄 Historial de reclamos recientes", expanded=False):
        if df_reclamos_cliente.empty:
            st.markdown("""
            <div class="text-center py-4 text-gray-500">
                <span class="text-lg">📭</span>
                <p class="mt-2">No hay reclamos registrados</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for _, recl in df_reclamos_cliente.iterrows():
                estado_color = {
                    "Pendiente": "text-yellow-600 bg-yellow-100",
                    "En curso": "text-blue-600 bg-blue-100", 
                    "Resuelto": "text-green-600 bg-green-100",
                    "Desconexión": "text-red-600 bg-red-100"
                }.get(recl.get('Estado', ''), 'text-gray-600 bg-gray-100')
                
                st.markdown(f"""
                <div class="bg-white dark:bg-gray-800 p-3 rounded-lg border border-gray-200 dark:border-gray-700 mb-2">
                    <div class="flex items-center justify-between">
                        <div class="flex-1">
                            <div class="flex items-center space-x-2 mb-1">
                                <span class="text-sm font-medium text-gray-900 dark:text-white">{recl['Tipo de reclamo']}</span>
                                <span class="text-xs px-2 py-1 rounded-full {estado_color}">{recl.get('Estado', 'N/A')}</span>
                            </div>
                            <div class="text-xs text-gray-500 dark:text-gray-400">
                                📅 {format_fecha(recl['Fecha y hora'], '%d/%m/%Y')} | 
                                👷 {recl.get('Técnico', 'Sin asignar')}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def _verificar_cambios_desde_reclamos(nro_cliente, df_reclamos, nueva_direccion, nuevo_telefono, nuevo_precinto):
    """Verifica diferencias entre datos actuales y reclamos recientes con sugerencias"""
    df_reclamos_cliente = df_reclamos[
        df_reclamos["Nº Cliente"] == nro_cliente
    ].copy()
    
    if df_reclamos_cliente.empty:
        return False
    
    cambios_detectados = []
    sugerencias = []
    
    campos = ["Dirección", "Teléfono", "N° de Precinto"]
    nuevos_valores = [nueva_direccion.strip(), nuevo_telefono.strip(), nuevo_precinto.strip()]
    
    for campo, nuevo_valor in zip(campos, nuevos_valores):
        if not nuevo_valor:
            continue
            
        valores_historicos = df_reclamos_cliente.head(5)[campo].dropna().astype(str).str.strip().unique()
        
        if len(valores_historicos) > 0 and nuevo_valor not in valores_historicos:
            cambios_detectados.append(campo)
            valor_comun = df_reclamos_cliente[campo].mode()
            if not valor_comun.empty:
                sugerencias.append(f"**{campo}**: Históricamente suele ser '{valor_comun.iloc[0]}'")
    
    if cambios_detectados:
        st.markdown("""
        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg mb-4">
            <div class="flex items-start">
                <span class="text-yellow-600 text-lg mr-3">⚠️</span>
                <div>
                    <h4 class="text-yellow-800 font-semibold mb-2">Posible inconsistencia detectada</h4>
                    <p class="text-yellow-700 text-sm mb-2">
                        Los campos {campos_detectados} difieren de los registrados en reclamos recientes.
                    </p>
        """.replace("{campos_detectados}", ", ".join(cambios_detectados)), unsafe_allow_html=True)
        
        if sugerencias:
            with st.expander("💡 Sugerencias basadas en histórico", expanded=False):
                for sugerencia in sugerencias:
                    st.markdown(sugerencia)
        
        st.markdown("""
                    <p class="text-yellow-700 text-sm font-medium">
                        Verificá que los datos sean correctos antes de guardar.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    return bool(cambios_detectados)

def _actualizar_cliente(cliente_row, sheet_clientes, nuevo_sector, nuevo_nombre, 
                       nueva_direccion, nuevo_telefono, nuevo_precinto):
    """Actualiza los datos del cliente en la hoja de cálculo"""
    
    if cliente_row.empty:
        st.markdown("""
        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
            <div class="flex items-start">
                <span class="text-red-600 text-lg mr-3">❌</span>
                <p class="text-red-700">Error: No se pudo encontrar el cliente para actualizar</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return False
        
    if len(cliente_row) > 1:
        st.markdown("""
        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg">
            <div class="flex items-start">
                <span class="text-yellow-600 text-lg mr-3">⚠️</span>
                <p class="text-yellow-700">Advertencia: Se encontraron múltiples clientes con el mismo número</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    cliente_actual = cliente_row.iloc[0]
    
    with st.spinner("🔄 Actualizando cliente..."):
        try:
            index = int(cliente_row.index[0]) + 2

            updates = [
                {"range": f"B{index}", "values": [[str(nuevo_sector)]]},
                {"range": f"C{index}", "values": [[str(nuevo_nombre).upper()]]},
                {"range": f"D{index}", "values": [[str(nueva_direccion).upper()]]},
                {"range": f"E{index}", "values": [[str(nuevo_telefono)]]},
                {"range": f"F{index}", "values": [[str(nuevo_precinto)]]},
                {"range": f"H{index}", "values": [[format_fecha(ahora_argentina())]]}
            ]

            success, error = api_manager.safe_sheet_operation(
                batch_update_sheet,
                sheet_clientes,
                updates,
                is_batch=True
            )

            if success:
                st.markdown("""
                <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg">
                    <div class="flex items-start">
                        <span class="text-green-600 text-lg mr-3">✅</span>
                        <p class="text-green-700 font-medium">Cliente actualizado correctamente</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if 'notification_manager' in st.session_state:
                    num_cliente = str(cliente_actual['Nº Cliente'])
                    nombre_cliente = str(nuevo_nombre).upper()
                    mensaje = f"✏️ Se actualizaron los datos del cliente N° {num_cliente} - {nombre_cliente}"
                    st.session_state.notification_manager.add(
                        notification_type="cliente_actualizado",
                        message=mensaje,
                        user_target="all"
                    )
                return True
            else:
                st.markdown(f"""
                <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                    <div class="flex items-start">
                        <span class="text-red-600 text-lg mr-3">❌</span>
                        <p class="text-red-700">Error al actualizar: {error}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                return False

        except ValueError:
            st.markdown("""
            <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                <div class="flex items-start">
                    <span class="text-red-600 text-lg mr-3">❌</span>
                    <p class="text-red-700">Error: Índice del cliente no es válido</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return False
        except Exception as e:
            st.markdown(f"""
            <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                <div class="flex items-start">
                    <span class="text-red-600 text-lg mr-3">❌</span>
                    <p class="text-red-700">Error inesperado: {str(e)}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return False

def _mostrar_nuevo_cliente(df_clientes, sheet_clientes):
    """Muestra el formulario para crear nuevo cliente con diseño moderno"""
    st.markdown("""
    <div class="mb-6">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white flex items-center">
            <span class="mr-2">🆕</span> Registrar nuevo cliente
        </h3>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
            Completa los datos para agregar un nuevo cliente al sistema
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    cambios = False

    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
    """, unsafe_allow_html=True)
    
    with st.form("form_nuevo_cliente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🔢 N° de Cliente *</label>', unsafe_allow_html=True)
            nuevo_nro = st.text_input(
                "", 
                placeholder="Número único de cliente",
                label_visibility="collapsed"
            ).strip()
            
            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🏢 Sector *</label>', unsafe_allow_html=True)
            nuevo_sector = st.selectbox(
                "",
                options=SECTORES_DISPONIBLES,
                index=0,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">👤 Nombre *</label>', unsafe_allow_html=True)
            nuevo_nombre = st.text_input(
                "", 
                placeholder="Nombre completo del cliente",
                label_visibility="collapsed"
            )
            
            st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📍 Dirección *</label>', unsafe_allow_html=True)
            nueva_direccion = st.text_input(
                "", 
                placeholder="Dirección completa",
                label_visibility="collapsed"
            )

        st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">📞 Teléfono</label>', unsafe_allow_html=True)
        nuevo_telefono = st.text_input(
            "", 
            placeholder="Número de contacto (opcional)",
            label_visibility="collapsed"
        )
        
        st.markdown('<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🔒 N° de Precinto</label>', unsafe_allow_html=True)
        nuevo_precinto = st.text_input(
            "", 
            placeholder="Número de precinto (opcional)",
            label_visibility="collapsed"
        )

        # Botón moderno
        guardar_cliente = st.form_submit_button(
            "💾 Guardar nuevo cliente", 
            use_container_width=True,
            type="primary"
        )

    st.markdown("</div>", unsafe_allow_html=True)

    if guardar_cliente:
        cambios = _guardar_nuevo_cliente(
            df_clientes, sheet_clientes,
            nuevo_nro, nuevo_sector, nuevo_nombre,
            nueva_direccion, nuevo_telefono, nuevo_precinto
        )

    return cambios

def _guardar_nuevo_cliente(df_clientes, sheet_clientes, nuevo_nro, nuevo_sector, 
                          nuevo_nombre, nueva_direccion, nuevo_telefono, nuevo_precinto):
    """Guarda un nuevo cliente en la hoja de cálculo con feedback visual mejorado"""
    
    # Validación de campos obligatorios
    if not nuevo_nombre.strip():
        st.markdown("""
        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-4">
            <div class="flex items-start">
                <span class="text-red-600 text-lg mr-3">❌</span>
                <p class="text-red-700">El nombre del cliente es obligatorio</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return False
        
    if not nueva_direccion.strip():
        st.markdown("""
        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-4">
            <div class="flex items-start">
                <span class="text-red-600 text-lg mr-3">❌</span>
                <p class="text-red-700">La dirección del cliente es obligatoria</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return False
    
    if not nuevo_nro.strip():
        st.markdown("""
        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-4">
            <div class="flex items-start">
                <span class="text-red-600 text-lg mr-3">❌</span>
                <p class="text-red-700">El número de cliente no puede estar vacío</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return False
        
    # Validar que el número de cliente sea único
    clientes_existentes = df_clientes["Nº Cliente"].astype(str).str.strip()
    if str(nuevo_nro).strip() in clientes_existentes.values:
        st.markdown("""
        <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-4">
            <div class="flex items-start">
                <span class="text-red-600 text-lg mr-3">❌</span>
                <p class="text-red-700">Este número de cliente ya existe. Usá otro número</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return False

    # Validar formato del teléfono
    if nuevo_telefono.strip() and not nuevo_telefono.strip().replace(" ", "").replace("-", "").isdigit():
        st.markdown("""
        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg mb-4">
            <div class="flex items-start">
                <span class="text-yellow-600 text-lg mr-3">⚠️</span>
                <p class="text-yellow-700">El teléfono parece tener formato incorrecto. Solo debe contener números, espacios o guiones</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.spinner("🔄 Guardando nuevo cliente..."):
        try:
            nuevo_id = str(uuid.uuid4())

            nueva_fila = [
                nuevo_nro.strip(), 
                str(nuevo_sector),
                nuevo_nombre.strip().upper(),
                nueva_direccion.strip().upper(), 
                nuevo_telefono.strip(),
                nuevo_precinto.strip(), 
                nuevo_id,
                format_fecha(ahora_argentina())
            ]

            success, error = api_manager.safe_sheet_operation(
                sheet_clientes.append_row,
                nueva_fila
            )

            if success:
                st.markdown(f"""
                <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg mb-4">
                    <div class="flex items-start">
                        <span class="text-green-600 text-lg mr-3">✅</span>
                        <div>
                            <p class="text-green-700 font-medium">Nuevo cliente agregado correctamente</p>
                            <p class="text-green-600 text-sm">Cliente: {nuevo_nombre.strip().upper()} - N° {nuevo_nro.strip()}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if 'notification_manager' in st.session_state:
                    mensaje = f"🆕 Se agregó el cliente N° {nuevo_nro.strip()} - {nuevo_nombre.strip().upper()} al sistema"
                    st.session_state.notification_manager.add(
                        notification_type="cliente_nuevo",
                        message=mensaje,
                        user_target="all"
                    )

                return True
            else:
                st.markdown(f"""
                <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                    <div class="flex items-start">
                        <span class="text-red-600 text-lg mr-3">❌</span>
                        <p class="text-red-700">Error al guardar: {error}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                return False

        except Exception as e:
            st.markdown(f"""
            <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                <div class="flex items-start">
                    <span class="text-red-600 text-lg mr-3">❌</span>
                    <p class="text-red-700">Error inesperado: {str(e)}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return False