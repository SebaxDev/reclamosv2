import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def render_dashboard(df_reclamos):
    """
    Renderiza el dashboard principal con métricas y gráficos dinámicos.
    """
    st.header("Dashboard Principal")
    st.markdown("Análisis visual de los reclamos y tendencias.")

    if df_reclamos.empty:
        st.info("No hay datos suficientes para generar el dashboard.")
        return

    # Preparar datos
    try:
        df_reclamos['Fecha y hora'] = pd.to_datetime(df_reclamos['Fecha y hora'], errors='coerce')
        df_dashboard = df_reclamos.dropna(subset=['Fecha y hora'])
    except Exception as e:
        st.error(f"Error al procesar las fechas de los reclamos: {e}")
        return

    # --- Gráficos ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Reclamos en los últimos 30 días")
        # Filtrar datos de los últimos 30 días
        last_30_days = df_dashboard[df_dashboard['Fecha y hora'] >= (datetime.now() - timedelta(days=30))]
        reclamos_por_dia = last_30_days.set_index('Fecha y hora').resample('D').size().reset_index(name='count')
        reclamos_por_dia = reclamos_por_dia.rename(columns={'Fecha y hora': 'Fecha', 'count': 'Número de Reclamos'})

        if not reclamos_por_dia.empty:
            st.line_chart(reclamos_por_dia.set_index('Fecha'))
        else:
            st.write("No hay reclamos en los últimos 30 días.")

    with col2:
        st.subheader("Distribución por Tipo de Reclamo")
        if 'Tipo de reclamo' in df_dashboard.columns:
            reclamos_por_tipo = df_dashboard['Tipo de reclamo'].value_counts().reset_index()
            reclamos_por_tipo.columns = ['Tipo de Reclamo', 'Cantidad']
            st.bar_chart(reclamos_por_tipo.set_index('Tipo de Reclamo'))
        else:
            st.write("La columna 'Tipo de reclamo' no existe.")

    st.markdown("---")
    st.subheader("Datos de Reclamos Recientes")
    st.dataframe(df_dashboard.head(10))
