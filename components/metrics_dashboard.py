"""
Dashboard de métricas profesional con TailwindCSS
Versión 4.0 - Diseño CRM moderno
"""

import streamlit as st
import pandas as pd
from datetime import datetime

def metric_card(value, label, icon="📊", trend=None, variant="primary"):
    """Tarjeta de métrica moderna con TailwindCSS"""
    
    variant_config = {
        "primary": {"bg": "bg-gradient-to-r from-blue-500 to-blue-600", "text": "text-white", "icon_bg": "bg-blue-600"},
        "success": {"bg": "bg-gradient-to-r from-green-500 to-green-600", "text": "text-white", "icon_bg": "bg-green-600"},
        "warning": {"bg": "bg-gradient-to-r from-yellow-500 to-yellow-600", "text": "text-gray-900", "icon_bg": "bg-yellow-600"},
        "danger": {"bg": "bg-gradient-to-r from-red-500 to-red-600", "text": "text-white", "icon_bg": "bg-red-600"},
        "neutral": {"bg": "bg-gradient-to-r from-gray-100 to-gray-200", "text": "text-gray-900", "icon_bg": "bg-gray-200"},
        "info": {"bg": "bg-gradient-to-r from-blue-400 to-blue-500", "text": "text-white", "icon_bg": "bg-blue-500"}  # ✅ Añadido
    }
    
    config = variant_config.get(variant, variant_config["primary"])
    
    trend_html = ""
    if trend:
        trend_color = "text-green-200" if trend.get('positive', True) else "text-red-200"
        trend_icon = "↗" if trend.get('positive', True) else "↘"
        trend_html = f"""
        <div class="flex items-center {trend_color} text-sm mt-1">
            <span class="mr-1">{trend_icon}</span>
            <span>{trend['value']}</span>
        </div>
        """
    
    return f"""
    <div class="{config['bg']} {config['text']} rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm opacity-90 font-medium">{label}</p>
                <p class="text-2xl font-bold mt-1">{value}</p>
                {trend_html}
            </div>
            <div class="{config['icon_bg']} rounded-full p-3">
                <span class="text-xl">{icon}</span>
            </div>
        </div>
    </div>
    """

def status_badge(status, count, description=""):
    """Badge de estado moderno"""
    
    status_config = {
        "Pendiente": {"color": "yellow", "icon": "⏳"},
        "En curso": {"color": "blue", "icon": "🔧"},
        "Resuelto": {"color": "green", "icon": "✅"},
        "Desconexión": {"color": "red", "icon": "🔌"},
        "Cerrado": {"color": "gray", "icon": "🔒"}
    }
    
    config = status_config.get(status, {"color": "gray", "icon": "❓"})
    color = config["color"]
    
    # ✅ CORREGIDO: Problema con comillas en f-strings
    description_html = f'<p class="text-{color}-600 text-sm">{description}</p>' if description else ''
    
    return f"""
    <div class="bg-{color}-50 border border-{color}-200 rounded-lg p-4 hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <span class="text-{color}-600 text-xl">{config['icon']}</span>
                <div>
                    <p class="text-{color}-800 font-semibold">{status}</p>
                    {description_html}
                </div>
            </div>
            <span class="text-{color}-800 font-bold text-xl">{count}</span>
        </div>
    </div>
    """

def render_metrics_dashboard(df_reclamos, is_mobile=False):
    """Renderiza el dashboard de métricas moderno"""
    try:
        if df_reclamos.empty:
            st.markdown("""
            <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded-lg">
                <div class="flex items-start">
                    <span class="text-yellow-600 text-lg mr-3">⚠️</span>
                    <p class="text-yellow-700">No hay datos de reclamos para mostrar</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return

        df_metricas = df_reclamos.copy()

        # ✅ Verificar si existe la columna "Estado"
        if "Estado" not in df_metricas.columns:
            st.error("❌ La columna 'Estado' no existe en los datos")
            return

        # Procesamiento de datos
        df_activos = df_metricas[df_metricas["Estado"].isin(["Pendiente", "En curso"])]
        total_activos = len(df_activos)
        pendientes = len(df_activos[df_activos["Estado"] == "Pendiente"])
        en_curso = len(df_activos[df_activos["Estado"] == "En curso"])
        resueltos = len(df_metricas[df_metricas["Estado"] == "Resuelto"])
        
        # ✅ Manejo seguro de desconexiones
        try:
            desconexiones = df_metricas["Estado"].str.strip().str.lower().eq("desconexión").sum()
        except:
            desconexiones = 0
        
        # Calcular porcentajes de forma segura
        total_reclamos = len(df_metricas)
        porcentaje_activos = (total_activos / total_reclamos * 100) if total_reclamos > 0 else 0
        porcentaje_resueltos = (resueltos / total_reclamos * 100) if total_reclamos > 0 else 0

        # Header del dashboard
        st.markdown("""
        <div class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center">
                <span class="mr-3">📈</span> Dashboard de Métricas
            </h2>
            <p class="text-gray-600 dark:text-gray-400 mt-1">
                Resumen general de la gestión de reclamos
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Diseño responsive
        if is_mobile:
            # Layout móvil (2 columnas)
            cols = st.columns(2)
            
            with cols[0]:
                st.markdown(metric_card(total_activos, "Activos", "📄", {"value": "+12%", "positive": True}, "primary"), unsafe_allow_html=True)
                st.markdown(metric_card(en_curso, "En Curso", "🔧", variant="info"), unsafe_allow_html=True)
                
            with cols[1]:
                st.markdown(metric_card(pendientes, "Pendientes", "⏳", {"value": "-5%", "positive": False}, "warning"), unsafe_allow_html=True)
                st.markdown(metric_card(resueltos, "Resueltos", "✅", {"value": "+8%", "positive": True}, "success"), unsafe_allow_html=True)
                
            # Sección de estados
            st.markdown("""
            <div class="mt-6">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">📊 Distribución por Estado</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(status_badge("Pendiente", pendientes, "Esperando atención"), unsafe_allow_html=True)
            st.markdown(status_badge("En curso", en_curso, "En proceso"), unsafe_allow_html=True)
            st.markdown(status_badge("Resuelto", resueltos, "Completados"), unsafe_allow_html=True)
            if desconexiones > 0:
                st.markdown(status_badge("Desconexión", desconexiones, "Servicio interrumpido"), unsafe_allow_html=True)
                
        else:
            # Layout desktop (4 columnas)
            cols = st.columns(4)
            
            with cols[0]:
                st.markdown(metric_card(total_activos, "Activos", "📄", {"value": "+12%", "positive": True}, "primary"), unsafe_allow_html=True)
            with cols[1]:
                st.markdown(metric_card(pendientes, "Pendientes", "⏳", {"value": "-5%", "positive": False}, "warning"), unsafe_allow_html=True)
            with cols[2]:
                st.markdown(metric_card(en_curso, "En Curso", "🔧", variant="info"), unsafe_allow_html=True)
            with cols[3]:
                st.markdown(metric_card(resueltos, "Resuelto", "✅", {"value": "+8%", "positive": True}, "success"), unsafe_allow_html=True)
            
            # Segunda fila de métricas
            cols2 = st.columns(4)
            
            with cols2[0]:
                st.markdown(metric_card(f"{porcentaje_activos:.1f}%", "Tasa Activos", "📊", variant="neutral"), unsafe_allow_html=True)
            with cols2[1]:
                st.markdown(metric_card(f"{porcentaje_resueltos:.1f}%", "Tasa Resolución", "🎯", variant="success"), unsafe_allow_html=True)
            with cols2[2]:
                st.markdown(metric_card(desconexiones, "Desconexiones", "🔌", variant="danger"), unsafe_allow_html=True)
            with cols2[3]:
                st.markdown(metric_card(total_reclamos, "Total", "📋", variant="neutral"), unsafe_allow_html=True)
            
            # Sección de estados
            st.markdown("""
            <div class="mt-8">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">📊 Distribución por Estado</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            """, unsafe_allow_html=True)
            
            estado_cols = st.columns(4)
            
            with estado_cols[0]:
                st.markdown(status_badge("Pendiente", pendientes, "Esperando atención"), unsafe_allow_html=True)
            with estado_cols[1]:
                st.markdown(status_badge("En curso", en_curso, "En proceso"), unsafe_allow_html=True)
            with estado_cols[2]:
                st.markdown(status_badge("Resuelto", resueltos, "Completados"), unsafe_allow_html=True)
            with estado_cols[3]:
                if desconexiones > 0:
                    st.markdown(status_badge("Desconexión", desconexiones, "Servicio interrumpido"), unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center text-gray-500">
                        No hay desconexiones
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error al mostrar métricas: {str(e)}")
        if st.session_state.get('DEBUG_MODE', False):
            st.exception(e)