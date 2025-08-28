# components/reclamos/impresion.py

import io
import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from utils.date_utils import format_fecha, parse_fecha
from utils.pdf_utils import agregar_pie_pdf
from utils.date_utils import ahora_argentina
from utils.reporte_diario import *
from components.ui_kit import crm_card, crm_metric, crm_badge, crm_loading, crm_alert
from components.ui import breadcrumb, metric_card, card, badge, loading_spinner as loading_indicator


def render_impresion_reclamos(df_reclamos, df_clientes, user):
    """
    Muestra la sección para imprimir reclamos en formato PDF
    
    Args:
        df_reclamos (pd.DataFrame): DataFrame con los reclamos
        df_clientes (pd.DataFrame): DataFrame con los clientes
        user (dict): Información del usuario actual
        
    Returns:
        dict: {
            'needs_refresh': bool,  # Siempre False para este módulo
            'message': str,         # Mensaje sobre la operación realizada
            'data_updated': bool    # Siempre False para este módulo
        }
    """
    result = {
        'needs_refresh': False,
        'message': None,
        'data_updated': False
    }
    
    # Header moderno con breadcrumb
    st.markdown("""
    <div class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center space-x-3">
            <span class="text-xl text-primary-600">📨️</span>
            <div>
                <h1 class="text-xl font-bold text-gray-900 dark:text-white">Impresión de Reclamos</h1>
                <p class="text-sm text-gray-500 dark:text-gray-400">Formato técnico compacto para impresión</p>
            </div>
        </div>
        <span class="text-sm text-gray-400">
            {ahora_argentina().strftime('%d/%m/%Y %H:%M')}
        </span>
    </div>
    """.format(ahora_argentina=ahora_argentina), unsafe_allow_html=True)

    try:
        # Preparar datos con información del usuario
        df_merged = _preparar_datos(df_reclamos, df_clientes, user)
        
        # Mostrar reclamos pendientes en tarjeta moderna
        _mostrar_reclamos_pendientes(df_merged)
        
        # Configuración de impresión en tarjeta
        with st.container():
            st.markdown("""
            <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">⚙️ Configuración de Impresión</h3>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                solo_pendientes = st.checkbox(
                    "📜 Mostrar solo reclamos pendientes", 
                    value=True,
                    help="Filtrar únicamente reclamos con estado 'Pendiente'"
                )
            with col2:
                incluir_usuario = st.checkbox(
                    "👤 Incluir mi nombre en el PDF",
                    value=True,
                    help="Agregar tu nombre como generador del reporte"
                )
            
            st.markdown('</div>', unsafe_allow_html=True)

        # Grid de opciones de impresión
        col1, col2 = st.columns(2)
        
        with col1:
            # Nueva opción para imprimir todos los pendientes
            mensaje_todos = _generar_pdf_todos_pendientes(df_merged, user if incluir_usuario else None)
            if mensaje_todos:
                result['message'] = mensaje_todos

            # Impresión por tipo
            mensaje_tipo = _generar_pdf_por_tipo(df_merged, solo_pendientes, user if incluir_usuario else None)
            if mensaje_tipo:
                result['message'] = mensaje_tipo
            
            # Impresión manual
            mensaje_manual = _generar_pdf_manual(df_merged, solo_pendientes, user if incluir_usuario else None)
            if mensaje_manual:
                result['message'] = mensaje_manual
        
        with col2:
            # Impresión Desconexiones
            mensaje_desconexiones = _generar_pdf_desconexiones(df_merged, user if incluir_usuario else None)
            if mensaje_desconexiones:
                result['message'] = mensaje_desconexiones
                
            # Impresión En Curso por Técnico
            mensaje_en_curso = _generar_pdf_en_curso_por_tecnico(df_merged, user if incluir_usuario else None)
            if mensaje_en_curso:
                result['message'] = mensaje_en_curso

        # === NUEVA SECCIÓN: Reporte Diario ===
        st.markdown("""
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">📄 Generar Reporte Diario</h3>
            <p class="text-gray-600 dark:text-gray-400 mb-4">Genera una imagen resumen del día en formato PNG</p>
        """, unsafe_allow_html=True)
        
        # Botón centrado con estilo moderno
        if st.button(
            "🖼️ Generar Imagen del Día", 
            use_container_width=True,
            type="primary",
            help="Crear reporte visual de las actividades del día"
        ):
            img_buffer = generar_reporte_diario_imagen(df_reclamos)
            fecha_hoy = ahora_argentina().strftime("%Y-%m-%d")
            
            st.download_button(
                label="⬇️ Descargar Reporte Diario",
                data=img_buffer,
                file_name=f"reporte_diario_{fecha_hoy}.png",
                mime="image/png",
                use_container_width=True,
                type="secondary"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al generar PDF: {str(e)}")
        result['message'] = f"Error al generar PDF: {str(e)}"
        if DEBUG_MODE:
            st.exception(e)
    
    return result

def _preparar_datos(df_reclamos, df_clientes, user):
    """Prepara y combina los datos para impresión incluyendo info de usuario"""
    df_pdf = df_reclamos.copy()
    
    # Procesamiento de fechas
    df_pdf["Fecha y hora"] = pd.to_datetime(
        df_pdf["Fecha y hora"], 
        dayfirst=True, 
        errors='coerce'
    )
    
    # Agregar información del usuario a los datos
    df_pdf["Usuario_impresion"] = user.get('nombre', 'Sistema')
    
    # Merge con clientes (optimizado)
    return pd.merge(
        df_pdf,
        df_clientes[["Nº Cliente", "N° de Precinto"]].drop_duplicates(),
        on="Nº Cliente",
        how="left",
        suffixes=("", "_cliente")
    )

def _mostrar_reclamos_pendientes(df_merged):
    """Muestra tabla de reclamos pendientes con mejor formato"""
    with st.expander("🕒 Reclamos Pendientes de Resolución", expanded=True):
        df_pendientes = df_merged[
            df_merged["Estado"].astype(str).str.strip().str.lower() == "pendiente"
        ]
        
        if not df_pendientes.empty:
            # Formatear datos para visualización
            df_pendientes_display = df_pendientes.copy()
            df_pendientes_display["Fecha y hora"] = df_pendientes_display["Fecha y hora"].apply(
                lambda f: format_fecha(f, '%d/%m/%Y %H:%M') if not pd.isna(f) else 'Sin fecha'
            )
            
            # Mostrar tabla con configuración mejorada
            st.dataframe(
                df_pendientes_display[[
                    "Fecha y hora", "Nº Cliente", "Nombre", 
                    "Dirección", "Sector", "Tipo de reclamo"
                ]],
                use_container_width=True,
                column_config={
                    "Fecha y hora": st.column_config.DatetimeColumn(
                        "Fecha y hora",
                        format="DD/MM/YYYY HH:mm"
                    ),
                    "Nº Cliente": st.column_config.TextColumn(
                        "N° Cliente",
                        help="Número de cliente"
                    ),
                    "Sector": st.column_config.NumberColumn(
                        "Sector",
                        format="%d"
                    )
                },
                height=400
            )
            
            # Métrica rápida
            st.markdown(f"""
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 mt-2">
                <p class="text-sm text-blue-800 dark:text-blue-200">
                    📊 Total: <strong>{len(df_pendientes)}</strong> reclamos pendientes
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✅ No hay reclamos pendientes actualmente.")

def _generar_pdf_todos_pendientes(df_merged, usuario=None):
    """Genera PDF con todos los reclamos pendientes, ordenados por tipo o sector"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-4 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h4 class="font-semibold text-gray-900 dark:text-white mb-3">📋 Imprimir TODOS los Reclamos Pendientes</h4>
    """, unsafe_allow_html=True)
    
    # Filtrar solo pendientes
    df_pendientes = df_merged[
        df_merged["Estado"].astype(str).str.strip().str.lower() == "pendiente"
    ]
    
    if df_pendientes.empty:
        st.info("✅ No hay reclamos pendientes para imprimir.")
        st.markdown('</div>', unsafe_allow_html=True)
        return None
    
    # Opciones de ordenamiento
    orden = st.radio(
        "Ordenar reclamos por:",
        ["Tipo de reclamo", "Sector"],
        horizontal=True,
        key="orden_todos_pendientes"
    )
    
    # Ordenar según selección
    if orden == "Tipo de reclamo":
        df_pendientes = df_pendientes.sort_values("Tipo de reclamo")
        titulo = "TODOS LOS RECLAMOS PENDIENTES (ORDENADOS POR TIPO)"
    else:
        df_pendientes = df_pendientes.sort_values("Sector")
        titulo = "TODOS LOS RECLAMOS PENDIENTES (ORDENADOS POR SECTOR)"
    
    st.success(f"📋 Se encontraron {len(df_pendientes)} reclamos pendientes.")
    
    if st.button(
        "📄 Generar PDF con TODOS los Pendientes", 
        key="pdf_todos_pendientes",
        use_container_width=True
    ):
        buffer = _crear_pdf_reclamos(
            df_pendientes, 
            titulo,
            usuario
        )
        
        nombre_archivo = f"todos_reclamos_pendientes_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        st.download_button(
            label="⬇️ Descargar PDF Completo",
            data=buffer,
            file_name=nombre_archivo,
            mime="application/pdf",
            use_container_width=True,
            help=f"Descargar {len(df_pendientes)} reclamos pendientes"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        return f"PDF generado con {len(df_pendientes)} reclamos pendientes (ordenados por {orden.lower()})"
    
    st.markdown('</div>', unsafe_allow_html=True)
    return None

def _generar_pdf_por_tipo(df_merged, solo_pendientes, usuario=None):
    """Genera PDF filtrado por tipos de reclamo"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-4 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h4 class="font-semibold text-gray-900 dark:text-white mb-3">📋 Imprimir por Tipo de Reclamo</h4>
    """, unsafe_allow_html=True)
    
    tipos_disponibles = sorted(df_merged["Tipo de reclamo"].dropna().unique())
    tipos_seleccionados = st.multiselect(
        "Seleccioná tipos de reclamo a imprimir",
        tipos_disponibles,
        default=tipos_disponibles[0] if tipos_disponibles else None,
        key="select_tipos_pdf",
        placeholder="Elige uno o más tipos..."
    )

    if not tipos_seleccionados:
        st.markdown('</div>', unsafe_allow_html=True)
        return None

    # Aplicar filtros
    df_filtrado = df_merged.copy()
    if solo_pendientes:
        df_filtrado = df_filtrado[
            df_filtrado["Estado"].str.strip().str.lower() == "pendiente"
        ]
    
    reclamos_filtrados = df_filtrado[
        df_filtrado["Tipo de reclamo"].isin(tipos_seleccionados)
    ]

    if reclamos_filtrados.empty:
        st.info("No hay reclamos para los tipos seleccionados.")
        st.markdown('</div>', unsafe_allow_html=True)
        return None

    st.success(f"📋 Se encontraron {len(reclamos_filtrados)} reclamos de los tipos seleccionados.")

    if st.button(
        "📄 Generar PDF por Tipo", 
        key="pdf_tipo",
        use_container_width=True
    ):
        buffer = _crear_pdf_reclamos(
            reclamos_filtrados, 
            f"RECLAMOS - {', '.join(tipos_seleccionados)}",
            usuario
        )
        
        nombre_archivo = f"reclamos_{'_'.join(t.lower().replace(' ', '_') for t in tipos_seleccionados)}.pdf"
        
        st.download_button(
            label="⬇️ Descargar PDF Filtrado",
            data=buffer,
            file_name=nombre_archivo,
            mime="application/pdf",
            use_container_width=True,
            help=f"Descargar {len(reclamos_filtrados)} reclamos de tipo {', '.join(tipos_seleccionados)}"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        return f"PDF generado con {len(reclamos_filtrados)} reclamos de tipo {', '.join(tipos_seleccionados)}"
    
    st.markdown('</div>', unsafe_allow_html=True)
    return None

def _generar_pdf_manual(df_merged, solo_pendientes, usuario=None):
    """Genera PDF con selección manual de reclamos"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-4 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h4 class="font-semibold text-gray-900 dark:text-white mb-3">📋 Selección Manual de Reclamos</h4>
    """, unsafe_allow_html=True)

    df_filtrado = df_merged.copy()
    if solo_pendientes:
        df_filtrado = df_filtrado[
            df_filtrado["Estado"].astype(str).str.strip().str.lower() == "pendiente"
        ]

    # Selector mejorado con más información
    selected = st.multiselect(
        "Seleccioná los reclamos a imprimir:",
        df_filtrado.index,
        format_func=lambda x: (
            f"{df_filtrado.at[x, 'Nº Cliente']} - "
            f"{df_filtrado.at[x, 'Nombre']} - "
            f"Sector {df_filtrado.at[x, 'Sector']} - "
            f"{df_filtrado.at[x, 'Tipo de reclamo']}"
        ),
        key="multiselect_reclamos",
        placeholder="Selecciona uno o más reclamos..."
    )

    if not selected:
        st.info("ℹ️ Seleccioná al menos un reclamo para generar el PDF.")
        st.markdown('</div>', unsafe_allow_html=True)
        return None

    if st.button(
        "📄 Generar PDF con Seleccionados", 
        key="pdf_manual",
        use_container_width=True
    ):
        buffer = _crear_pdf_reclamos(
            df_filtrado.loc[selected],
            f"RECLAMOS SELECCIONADOS",
            usuario
        )
        
        st.download_button(
            label="⬇️ Descargar PDF Seleccionados",
            data=buffer,
            file_name="reclamos_seleccionados.pdf",
            mime="application/pdf",
            use_container_width=True,
            help=f"Descargar {len(selected)} reclamos seleccionados"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        return f"PDF generado con {len(selected)} reclamos seleccionados"
    
    st.markdown('</div>', unsafe_allow_html=True)
    return None

def _crear_pdf_reclamos(df_reclamos, titulo, usuario=None):
    import io
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from utils.pdf_utils import agregar_pie_pdf
    from datetime import datetime

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40
    hoy = datetime.now().strftime('%d/%m/%Y %H:%M')

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, titulo)
    y -= 20

    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"Generado el: {hoy}")
    if usuario:
        c.drawString(width - 200, y, f"Por: {usuario.get('nombre', 'Sistema')}")
    y -= 30

    for _, reclamo in df_reclamos.iterrows():
        if y < 120:
            agregar_pie_pdf(c, width, height)
            c.showPage()
            y = height - 40
            c.setFont("Helvetica-Bold", 16)
            c.drawString(40, y, titulo + " (cont.)")
            y -= 30

        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, f"{reclamo['Nº Cliente']} - {reclamo['Nombre']}")
        y -= 15

        c.setFont("Helvetica", 11)
        fecha_pdf = reclamo['Fecha y hora'].strftime('%d/%m/%Y %H:%M') if not pd.isna(reclamo['Fecha y hora']) else 'Sin fecha'
        lineas = [
            f"Fecha: {fecha_pdf}",
            f"Dirección: {reclamo['Dirección']} - Tel: {reclamo['Teléfono']}",
            f"Sector: {reclamo['Sector']} - Precinto: {reclamo.get('N° de Precinto') or 'N/A'}",
            f"Tipo: {reclamo['Tipo de reclamo']}",
            f"Detalles: {reclamo['Detalles'][:100]}..." if len(reclamo['Detalles']) > 100 else f"Detalles: {reclamo['Detalles']}"
        ]

        for linea in lineas:
            c.drawString(40, y, linea)
            y -= 12

        y -= 5
        c.line(40, y, width - 40, y)
        y -= 15

    agregar_pie_pdf(c, width, height)
    c.save()
    buffer.seek(0)
    return buffer
    
def _generar_pdf_desconexiones(df_merged, usuario=None):
    """Genera un PDF con desconexiones a pedido (estado = desconexión)"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-4 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h4 class="font-semibold text-gray-900 dark:text-white mb-3">🔌 Imprimir Desconexiones a Pedido</h4>
    """, unsafe_allow_html=True)

    df_desconexiones = df_merged[
        (df_merged["Tipo de reclamo"].str.strip().str.lower() == "desconexion a pedido") &
        (df_merged["Estado"].str.strip().str.lower() == "desconexión")
    ]

    if df_desconexiones.empty:
        st.info("✅ No hay reclamos de tipo Desconexión a Pedido con estado 'Desconexión'.")
        st.markdown('</div>', unsafe_allow_html=True)
        return None

    st.success(f"📋 Se encontraron {len(df_desconexiones)} reclamos para desconectar.")

    if st.button(
        "📄 Generar PDF de Desconexiones", 
        key="pdf_desconexiones",
        use_container_width=True
    ):
        buffer = _crear_pdf_reclamos(
            df_desconexiones, 
            "LISTADO DE CLIENTES PARA DESCONEXIÓN",
            usuario
        )
        nombre_archivo = f"desconexiones_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"

        st.download_button(
            label="⬇️ Descargar PDF de Desconexiones",
            data=buffer,
            file_name=nombre_archivo,
            mime="application/pdf",
            use_container_width=True,
            help=f"Descargar {len(df_desconexiones)} reclamos de desconexión"
        )

        st.markdown('</div>', unsafe_allow_html=True)
        return f"PDF generado con {len(df_desconexiones)} desconexiones pendientes"

    st.markdown('</div>', unsafe_allow_html=True)
    return None

def _generar_pdf_en_curso_por_tecnico(df_merged, usuario=None):
    """Genera un PDF con reclamos en curso agrupados por técnico"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-4 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h4 class="font-semibold text-gray-900 dark:text-white mb-3">👷 Imprimir Reclamos EN CURSO</h4>
    """, unsafe_allow_html=True)

    df_en_curso = df_merged[
        df_merged["Estado"].astype(str).str.strip().str.lower() == "en curso"
    ].copy()

    if df_en_curso.empty:
        st.info("✅ No hay reclamos en curso para imprimir.")
        st.markdown('</div>', unsafe_allow_html=True)
        return None

    df_en_curso["Técnico"] = df_en_curso["Técnico"].fillna("Sin técnico").str.upper()
    reclamos_por_tecnico = df_en_curso.groupby("Técnico")

    if st.button(
        "📄 Generar PDF por Técnico", 
        key="pdf_en_curso_tecnico",
        use_container_width=True
    ):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        import io

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 40
        hoy = datetime.now().strftime('%d/%m/%Y')

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, f"RECLAMOS EN CURSO - {hoy}")
        if usuario:
            c.setFont("Helvetica", 10)
            c.drawString(width - 200, y, f"Por: {usuario.get('nombre', 'Sistema')}")
        y -= 30

        for tecnico, reclamos in reclamos_por_tecnico:
            if y < 100:
                agregar_pie_pdf(c, width, height)
                c.showPage()
                y = height - 40
                c.setFont("Helvetica-Bold", 16)
                c.drawString(40, y, f"RECLAMOS EN CURSO - {hoy}")
                y -= 30

            c.setFont("Helvetica-Bold", 13)
            c.drawString(40, y, f"👷 Técnico: {tecnico} ({len(reclamos)})")
            y -= 20

            c.setFont("Helvetica", 11)
            for _, row in reclamos.iterrows():
                texto = f"{row['Nº Cliente']} - {row['Tipo de reclamo']} - Sector {row['Sector']}"
                c.drawString(50, y, texto)
                y -= 15
                if y < 60:
                    agregar_pie_pdf(c, width, height)
                    c.showPage()
                    y = height - 40

            # Línea divisoria después de los reclamos de cada técnico
            c.setFont("Helvetica", 10)
            c.drawString(40, y, "-" * 80)
            y -= 20

        agregar_pie_pdf(c, width, height)
        c.save()
        buffer.seek(0)

        st.download_button(
            label="⬇️ Descargar PDF por Técnico",
            data=buffer,
            file_name=f"reclamos_en_curso_tecnicos_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            help="Reclamos agrupados por técnico"
        )

        st.markdown('</div>', unsafe_allow_html=True)
        return "PDF generado con reclamos en curso por técnico"

    st.markdown('</div>', unsafe_allow_html=True)
    return None