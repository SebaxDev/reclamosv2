# components/reclamos/gestion.py

import streamlit as st
import pandas as pd
from utils.date_utils import parse_fecha, format_fecha
from utils.api_manager import api_manager, batch_update_sheet
from config.settings import SECTORES_DISPONIBLES, DEBUG_MODE

def render_gestion_reclamos(df_reclamos, df_clientes, sheet_reclamos, user):
    """
    Muestra la sección de gestión de reclamos cargados
    
    Args:
        df_reclamos (pd.DataFrame): DataFrame con los reclamos
        df_clientes (pd.DataFrame): DataFrame con los clientes
        sheet_reclamos: Objeto de conexión a la hoja de reclamos
        user (dict): Información del usuario actual
        
    Returns:
        dict: {
            'needs_refresh': bool,  # Si se necesita recargar datos
            'message': str,         # Mensaje para mostrar al usuario
            'data_updated': bool    # Si se modificaron datos
        }
    """
    result = {
        'needs_refresh': False,
        'message': None,
        'data_updated': False
    }
    
    st.subheader("📊 Gestión de reclamos cargados")

    try:
        # Preprocesar datos una sola vez
        df = _preparar_datos(df_reclamos, df_clientes)
        
        # Mostrar estadísticas (no produce cambios) - ✅ ELIMINADA la distribución
        _mostrar_conteo_tipos(df)  # ✅ Solo mantenemos el conteo por tipo con estilo Monokai
        
        # Mostrar filtros y tabla (no produce cambios)
        df_filtrado = _mostrar_filtros_y_tabla(df)
        
        # Sección de edición de reclamos - ✅ OPTIMIZADA para ser más ágil
        cambios_edicion = _mostrar_edicion_reclamo_optimizada(df_filtrado, sheet_reclamos)
        if cambios_edicion:
            result.update({
                'needs_refresh': True,
                'message': 'Reclamo actualizado correctamente',
                'data_updated': True
            })
            return result
        
        # Gestión de desconexiones
        cambios_desconexiones = _gestionar_desconexiones(df_filtrado, sheet_reclamos)
        if cambios_desconexiones:
            result.update({
                'needs_refresh': True,
                'message': 'Desconexiones actualizadas',
                'data_updated': True
            })
            return result

    except Exception as e:
        st.error(f"⚠️ Error en la gestión de reclamos: {str(e)}")
        if DEBUG_MODE:
            st.exception(e)
        result['message'] = f"Error: {str(e)}"
    
    return result

def _preparar_datos(df_reclamos, df_clientes):
    """Prepara y limpia los datos para su visualización"""
    # Hacer copias para no modificar los dataframes originales
    df = df_reclamos.copy()
    df_clientes = df_clientes.copy()
    
    # Normalización de datos (una sola vez)
    df_clientes["Nº Cliente"] = df_clientes["Nº Cliente"].astype(str).str.strip()
    df["Nº Cliente"] = df["Nº Cliente"].astype(str).str.strip()
    df["ID Reclamo"] = df["ID Reclamo"].astype(str).str.strip()

    # Optimización: Solo traer las columnas necesarias de clientes
    cols_clientes = ["Nº Cliente", "N° de Precinto", "Teléfono"]
    df_clientes = df_clientes[cols_clientes].drop_duplicates(subset=["Nº Cliente"])

    # Merge más eficiente con datos de clientes
    df = pd.merge(
        df, 
        df_clientes,
        on="Nº Cliente", 
        how="left", 
        suffixes=("", "_cliente")
    )

    # Procesamiento de fechas
    if 'Fecha y hora' in df.columns:
        df["Fecha y hora"] = df["Fecha y hora"].apply(parse_fecha)
        df["Fecha_formateada"] = df["Fecha y hora"].apply(
            lambda x: format_fecha(x, '%d/%m/%Y %H:%M')
        )

        # Validación de fechas
        if df["Fecha y hora"].isna().any():
            num_fechas_invalidas = df["Fecha y hora"].isna().sum()
            st.warning(f"⚠️ {num_fechas_invalidas} reclamos tienen fechas inválidas o faltantes")

    return df.sort_values("Fecha y hora", ascending=False)

def _mostrar_conteo_tipos(df):
    """Muestra conteo de reclamos por tipo con estilo Monokai"""
    df_activos = df[df["Estado"].isin(["Pendiente", "En curso", "Desconexión"])]
    
    if not df_activos.empty:
        st.markdown("#### 📊 Reclamos activos por tipo")
        conteo_por_tipo = df_activos["Tipo de reclamo"].value_counts().sort_index()
        
        # Crear columnas dinámicamente
        num_tipos = len(conteo_por_tipo)
        cols = st.columns(min(4, num_tipos))
        
        for i, (tipo, cant) in enumerate(conteo_por_tipo.items()):
            col_idx = i % 4
            with cols[col_idx]:
                # Estilo Monokai mejorado
                st.markdown(f"""
                <div style='
                    text-align:center;
                    background: var(--bg-card);
                    padding: 1rem;
                    border-radius: var(--radius-lg);
                    border: 2px solid var(--border-color);
                    margin-bottom: 1rem;
                    box-shadow: var(--shadow-sm);
                    transition: var(--transition-base);
                '>
                    <h5 style='
                        margin: 0 0 0.5rem 0;
                        color: var(--text-secondary);
                        font-size: 0.8rem;
                        font-family: "Fira Code", monospace;
                    '>{tipo}</h5>
                    <h4 style='
                        margin: 0;
                        color: var(--primary-color);
                        font-size: 1.5rem;
                        font-family: "Fira Code", monospace;
                        font-weight: 700;
                    '>{cant}</h4>
                </div>
                """, unsafe_allow_html=True)

def _mostrar_filtros_y_tabla(df):
    """Muestra filtros y tabla de reclamos (no produce cambios)"""
    st.markdown("#### 🔍 Filtros de búsqueda")
    
    # Filtros en columnas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        estado = st.selectbox(
            "Estado", 
            ["Todos"] + sorted(df["Estado"].dropna().unique())
        )
    
    with col2:
        sector = st.selectbox(
            "Sector", 
            ["Todos"] + sorted(SECTORES_DISPONIBLES)
        )
    
    with col3:
        tipo = st.selectbox(
            "Tipo de reclamo", 
            ["Todos"] + sorted(df["Tipo de reclamo"].dropna().unique())
        )

    # Aplicar filtros
    df_filtrado = df.copy()
    if estado != "Todos": 
        df_filtrado = df_filtrado[df_filtrado["Estado"] == estado]
    if sector != "Todos": 
        df_filtrado = df_filtrado[df_filtrado["Sector"] == str(sector)]
    if tipo != "Todos": 
        df_filtrado = df_filtrado[df_filtrado["Tipo de reclamo"] == tipo]

    st.markdown(f"**Mostrando {len(df_filtrado)} de {len(df)} reclamos**")

    # Mostrar tabla optimizada
    columnas = [
        "Fecha_formateada", "Nº Cliente", "Nombre", 
        "Sector", "Tipo de reclamo", "Teléfono", "Estado"
    ]
    
    st.dataframe(
        df_filtrado[columnas].rename(columns={"Fecha_formateada": "Fecha y hora"}),
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    return df_filtrado

def _mostrar_edicion_reclamo_optimizada(df, sheet_reclamos):
    """Muestra interfaz optimizada para editar reclamos (búsqueda y edición integradas)"""
    st.markdown("---")
    st.markdown("### ✏️ Editor Rápido de Reclamos")
    
    # Búsqueda integrada con selección
    col1, col2 = st.columns([3, 1])
    
    with col1:
        busqueda = st.text_input(
            "🔍 Buscar reclamo (por número de cliente, nombre o ID)",
            placeholder="Ej: 12345, Juan Pérez, ABC123..."
        )
    
    with col2:
        st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)
        limpiar_busqueda = st.button("🧹 Limpiar", use_container_width=True)
        if limpiar_busqueda:
            st.session_state.edicion_busqueda = ""
            st.rerun()
    
    # Filtrar reclamos basados en la búsqueda
    reclamos_filtrados = df.copy()
    if busqueda:
        busqueda_lower = busqueda.lower()
        mask = (
            reclamos_filtrados["Nº Cliente"].str.lower().str.contains(busqueda_lower) |
            reclamos_filtrados["Nombre"].str.lower().str.contains(busqueda_lower) |
            reclamos_filtrados["ID Reclamo"].str.lower().str.contains(busqueda_lower)
        )
        reclamos_filtrados = reclamos_filtrados[mask]
    
    if reclamos_filtrados.empty:
        if busqueda:
            st.info("🔍 No se encontraron reclamos con esa búsqueda")
        return False
    
    # Selección rápida con información compacta
    opciones = []
    for _, row in reclamos_filtrados.iterrows():
        opcion_texto = (
            f"{row['Nº Cliente']} - {row['Nombre']} | "
            f"Sector {row['Sector']} | "
            f"{format_fecha(row['Fecha y hora'], '%d/%m')} | "
            f"{row['Estado']}"
        )
        opciones.append((opcion_texto, row))
    
    # Selector compacto
    opciones_texto = [opc[0] for opc in opciones]
    seleccion_idx = st.selectbox(
        "Selecciona el reclamo a editar:",
        range(len(opciones_texto)),
        format_func=lambda i: opciones_texto[i],
        index=0
    )
    
    if seleccion_idx is None:
        return False
    
    reclamo_seleccionado = opciones[seleccion_idx][1]
    reclamo_id = reclamo_seleccionado["ID Reclamo"]
    
    # Mostrar información compacta del reclamo seleccionado
    with st.expander("📋 Información del reclamo seleccionado", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📅 Fecha:** {format_fecha(reclamo_seleccionado['Fecha y hora'])}")
            st.markdown(f"**👤 Cliente:** {reclamo_seleccionado['Nombre']}")
            st.markdown(f"**📍 Dirección:** {reclamo_seleccionado.get('Dirección', 'N/A')}")
        with col2:
            st.markdown(f"**📌 Tipo:** {reclamo_seleccionado['Tipo de reclamo']}")
            st.markdown(f"**🔢 Sector:** {reclamo_seleccionado['Sector']}")
            st.markdown(f"**⚙️ Estado:** {reclamo_seleccionado['Estado']}")
            st.markdown(f"**📞 Teléfono:** {reclamo_seleccionado.get('Teléfono', 'N/A')}")
    
    # Formulario de edición rápido
    with st.form(f"form_editar_rapido_{reclamo_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            nuevo_estado = st.selectbox(
                "🔄 Nuevo estado",
                ["Pendiente", "En curso", "Resuelto", "Desconexión"],
                index=["Pendiente", "En curso", "Resuelto", "Desconexión"].index(
                    reclamo_seleccionado["Estado"]
                ) if reclamo_seleccionado["Estado"] in ["Pendiente", "En curso", "Resuelto", "Desconexión"] 
                else 0
            )
            
            # Solo mostrar campos editables si el estado cambia
            if nuevo_estado != reclamo_seleccionado["Estado"]:
                st.info("💡 El estado cambiará al guardar")
        
        with col2:
            tecnico = st.text_input(
                "👷 Asignar técnico",
                value=reclamo_seleccionado.get("Técnico", ""),
                placeholder="Nombre del técnico",
                disabled=nuevo_estado == "Pendiente"
            )
        
        # Campos adicionales para edición completa
        with st.expander("✏️ Edición avanzada (opcional)"):
            col3, col4 = st.columns(2)
            with col3:
                direccion_edit = st.text_input(
                    "📍 Dirección",
                    value=reclamo_seleccionado.get("Dirección", "")
                )
                telefono_edit = st.text_input(
                    "📞 Teléfono",
                    value=reclamo_seleccionado.get("Teléfono", "")
                )
            with col4:
                detalles_edit = st.text_area(
                    "📝 Detalles",
                    value=reclamo_seleccionado.get("Detalles", ""),
                    height=100
                )
                precinto_edit = st.text_input(
                    "🔒 Precinto",
                    value=reclamo_seleccionado.get("N° de Precinto", "")
                )
        
        # Botones de acción
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            guardar_rapido = st.form_submit_button(
                "💾 Guardar cambios rápidos",
                use_container_width=True,
                help="Solo cambia estado y técnico"
            )
        
        with col_btn2:
            guardar_completo = st.form_submit_button(
                "🔄 Guardar todos los campos",
                use_container_width=True,
                help="Guarda todos los campos editables"
            )
    
    # Procesar acciones
    if guardar_rapido or guardar_completo:
        updates = {
            "estado": nuevo_estado,
            "tecnico": tecnico if nuevo_estado != "Pendiente" else ""
        }
        
        if guardar_completo:
            updates.update({
                "direccion": direccion_edit,
                "telefono": telefono_edit,
                "detalles": detalles_edit,
                "precinto": precinto_edit
            })
        
        return _actualizar_reclamo(
            df, sheet_reclamos, reclamo_id,
            updates,
            full_update=guardar_completo
        )
    
    return False

def _actualizar_reclamo(df, sheet_reclamos, reclamo_id, updates, full_update=False):
    """Actualiza el reclamo en la hoja de cálculo y genera notificaciones si corresponde"""
    from config.settings import NOTIFICATION_TYPES  # Para íconos (opcional)
    
    with st.spinner("Actualizando reclamo..."):
        try:
            fila = df[df["ID Reclamo"] == reclamo_id].index[0] + 2
            updates_list = []
            estado_anterior = df[df["ID Reclamo"] == reclamo_id]["Estado"].values[0]

            if full_update:
                # ✅ Mapeo corregido de columnas según tu hoja
                updates_list.extend([
                    {"range": f"E{fila}", "values": [[updates.get('direccion', '').upper()]]},  # Dirección
                    {"range": f"F{fila}", "values": [[str(updates.get('telefono', ''))]]},     # Teléfono
                    {"range": f"H{fila}", "values": [[updates.get('detalles', '')]]},          # Detalles
                    {"range": f"K{fila}", "values": [[updates.get('precinto', '')]]},          # Precinto
                ])

            # ✅ Estado (columna I)
            updates_list.append({"range": f"I{fila}", "values": [[updates['estado']]]})

            # ✅ Técnico (columna J) - solo si se proporciona
            if 'tecnico' in updates:
                updates_list.append({"range": f"J{fila}", "values": [[updates['tecnico']]]})

            # Si pasa a pendiente, limpiar columna J (técnico)
            if updates['estado'] == "Pendiente":
                updates_list.append({"range": f"J{fila}", "values": [[""]]})

            # Guardar en Google Sheets
            success, error = api_manager.safe_sheet_operation(
                batch_update_sheet, 
                sheet_reclamos, 
                updates_list, 
                is_batch=True
            )

            if success:
                st.success("✅ Reclamo actualizado correctamente.")

                # Crear notificación si cambió el estado
                if updates['estado'] != estado_anterior and 'notification_manager' in st.session_state:
                    mensaje = f"El reclamo {reclamo_id} cambió de estado: {estado_anterior} ➜ {updates['estado']}"
                    usuario = st.session_state.auth.get('user_info', {}).get('username', 'desconocido')
                    st.session_state.notification_manager.add(
                        notification_type="status_change",
                        message=mensaje,
                        user_target="all",
                        claim_id=reclamo_id
                    )

                return True
            else:
                st.error(f"❌ Error al actualizar: {error}")
                return False

        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            if DEBUG_MODE:
                st.exception(e)
            return False

def _gestionar_desconexiones(df, sheet_reclamos):
    """Gestiona las desconexiones a pedido (puede producir cambios)"""
    st.markdown("---")
    st.markdown("### 🔌 Gestión de Desconexiones a Pedido")

    desconexiones = df[
        (df["Tipo de reclamo"].str.strip().str.lower() == "desconexion a pedido") &
        (df["Estado"].str.strip().str.lower() == "desconexión")
    ]

    if desconexiones.empty:
        st.success("✅ No hay desconexiones pendientes de marcar como resueltas.")
        return False

    st.info(f"📄 Hay {len(desconexiones)} desconexiones cargadas ir a Impresion para imprimir listado.")
    
    cambios = False
    
    for i, row in desconexiones.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{row['Nº Cliente']} - {row['Nombre']}**")
                st.markdown(f"📅 {format_fecha(row['Fecha y hora'])} - Sector {row['Sector']}")
            
            with col2:
                if st.button("✅ Marcar como resuelto", key=f"resuelto_{i}", use_container_width=True):
                    if _marcar_desconexion_como_resuelta(row, sheet_reclamos):
                        cambios = True
            
            st.divider()
    
    return cambios

def _marcar_desconexion_como_resuelta(row, sheet_reclamos):
    """Marca una desconexión como resuelta en la hoja de cálculo"""
    with st.spinner("Actualizando estado..."):
        try:
            fila = row.name + 2
            success, error = api_manager.safe_sheet_operation(
                sheet_reclamos.update, 
                f"I{fila}", 
                [["Resuelto"]]
            )
            
            if success:
                st.success(f"✅ Desconexión de {row['Nombre']} marcada como resuelta.")
                return True
            else:
                st.error(f"❌ Error al actualizar: {error}")
                return False
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            if DEBUG_MODE:
                st.exception(e)
            return False