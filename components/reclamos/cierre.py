# components/reclamos/cierre.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.date_utils import parse_fecha, format_fecha, ahora_argentina
from utils.api_manager import api_manager, batch_update_sheet
from config.settings import SECTORES_DISPONIBLES, DEBUG_MODE
from components.ui_kit import crm_card, crm_metric, crm_badge, crm_loading, crm_alert
from components.ui import breadcrumb, metric_card, card, badge, loading_spinner as loading_indicator

def render_cierre_reclamos(df_reclamos, df_clientes, sheet_reclamos, sheet_clientes, user):
    """
    Muestra la sección de cierre y gestión avanzada de reclamos
    
    Args:
        df_reclamos (pd.DataFrame): DataFrame con los reclamos
        df_clientes (pd.DataFrame): DataFrame con los clientes
        sheet_reclamos: Objeto de conexión a la hoja de reclamos
        sheet_clientes: Objeto de conexión a la hoja de clientes
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
    
    # Header moderno
    st.markdown("""
    <div class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center space-x-3">
            <span class="text-xl text-primary-600">✅</span>
            <div>
                <h1 class="text-xl font-bold text-gray-900 dark:text-white">Cierre de Reclamos</h1>
                <p class="text-sm text-gray-500 dark:text-gray-400">Gestión avanzada y limpieza de reclamos</p>
            </div>
        </div>
        <span class="text-sm text-gray-400">
            {ahora_argentina().strftime('%d/%m/%Y %H:%M')}
        </span>
    </div>
    """.format(ahora_argentina=ahora_argentina), unsafe_allow_html=True)

    try:
        # Preprocesar datos una sola vez
        df = _preparar_datos(df_reclamos, df_clientes)
        
        # Mostrar estadísticas en tarjetas modernas
        _mostrar_estadisticas_mejoradas(df)
        
        # Gestión de cierre de reclamos
        cambios_cierre = _gestion_cierre_reclamos(df, sheet_reclamos)
        if cambios_cierre:
            result.update({
                'needs_refresh': True,
                'message': 'Reclamos cerrados correctamente',
                'data_updated': True
            })
            return result
        
        # Gestión de limpieza de reclamos antiguos
        cambios_limpieza = _gestion_limpieza_reclamos(df, sheet_reclamos)
        if cambios_limpieza:
            result.update({
                'needs_refresh': True,
                'message': 'Limpieza de reclamos completada',
                'data_updated': True
            })
            return result

    except Exception as e:
        st.error(f"❌ Error en el cierre de reclamos: {str(e)}")
        if DEBUG_MODE:
            st.exception(e)
        result['message'] = f"Error: {str(e)}"
    
    return result

def _preparar_datos(df_reclamos, df_clientes):
    """Prepara y limpia los datos para su visualización"""
    # Hacer copias para no modificar los dataframes originales
    df = df_reclamos.copy()
    df_clientes = df_clientes.copy()
    
    # Normalización de datos
    df_clientes["Nº Cliente"] = df_clientes["Nº Cliente"].astype(str).str.strip()
    df["Nº Cliente"] = df["Nº Cliente"].astype(str).str.strip()
    df["ID Reclamo"] = df["ID Reclamo"].astype(str).str.strip()

    # Procesamiento de fechas
    if 'Fecha y hora' in df.columns:
        df["Fecha y hora"] = df["Fecha y hora"].apply(parse_fecha)
        df["Fecha_formateada"] = df["Fecha y hora"].apply(
            lambda x: format_fecha(x, '%d/%m/%Y %H:%M') if pd.notna(x) else "Fecha inválida"
        )

    return df.sort_values("Fecha y hora", ascending=False)

def _mostrar_estadisticas_mejoradas(df):
    """Muestra estadísticas visuales de reclamos con diseño moderno"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">📊 Estadísticas de Reclamos</h3>
    """, unsafe_allow_html=True)
    
    # Métricas en grid moderno
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df)
        st.markdown(f"""
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{total}</div>
            <div class="text-sm text-blue-700 dark:text-blue-300">Total Reclamos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        pendientes = len(df[df["Estado"] == "Pendiente"])
        st.markdown(f"""
        <div class="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{pendientes}</div>
            <div class="text-sm text-yellow-700 dark:text-yellow-300">Pendientes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        en_curso = len(df[df["Estado"] == "En curso"])
        st.markdown(f"""
        <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{en_curso}</div>
            <div class="text-sm text-orange-700 dark:text-orange-300">En Curso</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        resueltos = len(df[df["Estado"] == "Resuelto"])
        st.markdown(f"""
        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-green-600 dark:text-green-400">{resueltos}</div>
            <div class="text-sm text-green-700 dark:text-green-300">Resueltos</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def _gestion_cierre_reclamos(df, sheet_reclamos):
    """Gestión de cierre de reclamos pendientes/en curso"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">✅ Cierre de Reclamos Activos</h3>
    """, unsafe_allow_html=True)
    
    # Filtrar reclamos activos (pendientes o en curso)
    reclamos_activos = df[df["Estado"].isin(["Pendiente", "En curso"])]
    
    if reclamos_activos.empty:
        st.success("🎉 No hay reclamos activos para cerrar.")
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    
    st.info(f"📋 Hay {len(reclamos_activos)} reclamos activos disponibles para cerrar.")
    
    # Selector de reclamos
    reclamos_activos["opcion"] = reclamos_activos.apply(
        lambda x: f"{x['Nº Cliente']} - {x['Nombre']} ({x['Estado']}) - Sector {x['Sector']}", 
        axis=1
    )
    
    reclamo_seleccionado = st.selectbox(
        "Selecciona un reclamo para cerrar:",
        options=[""] + reclamos_activos["opcion"].tolist(),
        help="Selecciona un reclamo para marcarlo como resuelto"
    )
    
    if not reclamo_seleccionado:
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    
    # Obtener datos del reclamo seleccionado
    nro_cliente = reclamo_seleccionado.split(" - ")[0]
    reclamo_data = reclamos_activos[reclamos_activos["Nº Cliente"] == nro_cliente].iloc[0]
    
    # Mostrar información del reclamo
    with st.expander("📋 Información del Reclamo", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**👤 Cliente:** {reclamo_data['Nombre']}")
            st.markdown(f"**📍 Dirección:** {reclamo_data['Dirección']}")
            st.markdown(f"**📞 Teléfono:** {reclamo_data['Teléfono']}")
        with col2:
            st.markdown(f"**📍 Sector:** {reclamo_data['Sector']}")
            st.markdown(f"**📌 Tipo:** {reclamo_data['Tipo de reclamo']}")
            st.markdown(f"**🔄 Estado:** {reclamo_data['Estado']}")
    
    # Formulario de cierre
    with st.form(f"form_cierre_{reclamo_data['ID Reclamo']}"):
        observaciones = st.text_area(
            "Observaciones de cierre:",
            placeholder="Describí cómo se resolvió el reclamo...",
            help="Información adicional sobre la resolución"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button(
                "✅ Cerrar Reclamo", 
                use_container_width=True,
                type="primary"
            ):
                if _cerrar_reclamo(reclamo_data, observaciones, sheet_reclamos):
                    st.markdown('</div>', unsafe_allow_html=True)
                    return True
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False

def _cerrar_reclamo(reclamo_data, observaciones, sheet_reclamos):
    """Marca un reclamo como resuelto en la hoja de cálculo"""
    with st.spinner("Cerrando reclamo..."):
        try:
            fila = reclamo_data.name + 2
            fecha_cierre = ahora_argentina().strftime('%d/%m/%Y %H:%M')
            
            # Preparar actualizaciones
            updates = [
                {"range": f"I{fila}", "values": [["Resuelto"]]},  # Estado
                {"range": f"M{fila}", "values": [[fecha_cierre]]},  # Fecha de cierre
            ]
            
            if observaciones.strip():
                detalles_actualizados = f"{reclamo_data.get('Detalles', '')}\n\n--- CIERRE ---\n{observaciones}"
                updates.append({"range": f"H{fila}", "values": [[detalles_actualizados]]})
            
            # Guardar en Google Sheets
            success, error = api_manager.safe_sheet_operation(
                batch_update_sheet, 
                sheet_reclamos, 
                updates, 
                is_batch=True
            )
            
            if success:
                st.success("✅ Reclamo cerrado correctamente.")
                
                # Notificación
                if 'notification_manager' in st.session_state:
                    mensaje = f"El reclamo {reclamo_data['ID Reclamo']} fue cerrado por {st.session_state.auth.get('user_info', {}).get('nombre', 'Sistema')}"
                    st.session_state.notification_manager.add(
                        notification_type="status_change",
                        message=mensaje,
                        user_target="all",
                        claim_id=reclamo_data['ID Reclamo']
                    )
                
                return True
            else:
                st.error(f"❌ Error al cerrar reclamo: {error}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            if DEBUG_MODE:
                st.exception(e)
            return False

def _gestion_limpieza_reclamos(df, sheet_reclamos):
    """Gestión de limpieza de reclamos antiguos"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">🗑️ Limpieza de Reclamos Antiguos</h3>
    """, unsafe_allow_html=True)
    
    # Filtrar reclamos resueltos con más de 15 días
    hoy = ahora_argentina()
    fecha_limite = hoy - timedelta(days=15)
    
    reclamos_antiguos = df[
        (df["Estado"] == "Resuelto") &
        (df["Fecha y hora"] <= fecha_limite)
    ]
    
    if reclamos_antiguos.empty:
        st.success("✅ No hay reclamos resueltos con más de 15 días para eliminar.")
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    
    st.warning(f"⚠️ Se encontraron {len(reclamos_antiguos)} reclamos resueltos con más de 15 días.")
    
    # Mostrar reclamos a eliminar
    with st.expander("📋 Reclamos a eliminar", expanded=False):
        for _, reclamo in reclamos_antiguos.iterrows():
            dias_antiguedad = (hoy - reclamo["Fecha y hora"]).days
            st.markdown(f"""
            **{reclamo['Nº Cliente']} - {reclamo['Nombre']}**
            - 📅 {format_fecha(reclamo['Fecha y hora'])} ({dias_antiguedad} días)
            - 📌 {reclamo['Tipo de reclamo']}
            - 🔢 ID: {reclamo['ID Reclamo']}
            """)
    
    # Confirmación de eliminación
    st.markdown("""
    <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-lg p-4 mb-4">
        <h4 class="font-semibold text-red-800 dark:text-red-200">⚠️ Advertencia Importante</h4>
        <p class="text-red-700 dark:text-red-300 text-sm">
            Esta acción eliminará permanentemente los reclamos seleccionados. 
            Esta operación no se puede deshacer.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    confirmacion = st.checkbox(
        "Confirmo que quiero eliminar estos reclamos antiguos",
        help="Debes confirmar para habilitar la eliminación"
    )
    
    if confirmacion:
        if st.button(
            "🗑️ Eliminar Reclamos Antiguos", 
            type="secondary",
            use_container_width=True,
            help="Eliminar reclamos resueltos con más de 15 días"
        ):
            if _eliminar_reclamos_antiguos(reclamos_antiguos, sheet_reclamos):
                st.markdown('</div>', unsafe_allow_html=True)
                return True
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False

def _eliminar_reclamos_antiguos(reclamos_antiguos, sheet_reclamos):
    """Elimina reclamos resueltos con más de 15 días"""
    with st.spinner("Eliminando reclamos antiguos..."):
        try:
            # Obtener todas las filas de la hoja
            all_data = sheet_reclamos.get_all_values()
            
            # Identificar filas a eliminar (basado en ID Reclamo)
            filas_a_eliminar = []
            ids_a_eliminar = set(reclamos_antiguos["ID Reclamo"].astype(str))
            
            for i, fila in enumerate(all_data[1:], start=2):  # Saltar encabezado
                if len(fila) > 13 and fila[13].strip() in ids_a_eliminar:  # Columna N (ID Reclamo)
                    filas_a_eliminar.append(i)
            
            if not filas_a_eliminar:
                st.error("❌ No se encontraron los reclamos en la hoja.")
                return False
            
            # Eliminar filas (empezando desde la última para evitar problemas de indexación)
            for fila in sorted(filas_a_eliminar, reverse=True):
                sheet_reclamos.delete_rows(fila)
            
            st.success(f"✅ Se eliminaron {len(filas_a_eliminar)} reclamos antiguos.")
            
            # Notificación
            if 'notification_manager' in st.session_state:
                mensaje = f"Se eliminaron {len(filas_a_eliminar)} reclamos resueltos con más de 15 días"
                st.session_state.notification_manager.add(
                    notification_type="status_change",
                    message=mensaje,
                    user_target="admin"
                )
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error al eliminar reclamos: {str(e)}")
            if DEBUG_MODE:
                st.exception(e)
            return False