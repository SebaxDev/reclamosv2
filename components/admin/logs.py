# components/admin/logs.py

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_manager import api_manager
from utils.date_utils import ahora_argentina

# Columnas para la hoja de logs
COLUMNAS_LOGS = ["timestamp", "usuario", "nivel", "modulo", "accion", "detalles", "ip_address"]

def render_logs_actividad(sheet_logs):
    """Módulo de visualización de logs de actividad"""
    
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">📊 Logs de Actividad del Sistema</h3>
    """, unsafe_allow_html=True)
    
    # Cargar logs
    df_logs = _cargar_logs(sheet_logs)
    
    if df_logs.empty:
        st.info("No hay registros de actividad aún.")
        st.markdown('</div>', unsafe_allow_html=True)
        return {'needs_refresh': False}
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha_inicio = st.date_input("Fecha desde", value=datetime.now().replace(day=1))
    
    with col2:
        fecha_fin = st.date_input("Fecha hasta", value=datetime.now())
    
    with col3:
        nivel_filter = st.selectbox("Nivel", ["Todos", "INFO", "WARNING", "ERROR", "DEBUG"])
    
    # Aplicar filtros
    df_filtrado = df_logs.copy()
    df_filtrado = df_filtrado[
        (df_filtrado['timestamp'].dt.date >= fecha_inicio) & 
        (df_filtrado['timestamp'].dt.date <= fecha_fin)
    ]
    
    if nivel_filter != "Todos":
        df_filtrado = df_filtrado[df_filtrado['nivel'] == nivel_filter]
    
    # Mostrar estadísticas
    _mostrar_estadisticas_logs(df_filtrado)
    
    # Mostrar tabla de logs
    st.markdown("### 📋 Registros de Actividad")
    
    df_filtrado['fecha_formateada'] = df_filtrado['timestamp'].dt.strftime('%d/%m/%Y %H:%M')
    
    st.dataframe(
        df_filtrado[['fecha_formateada', 'usuario', 'nivel', 'modulo', 'accion', 'detalles']],
        use_container_width=True,
        column_config={
            "fecha_formateada": "Fecha/Hora",
            "usuario": "Usuario",
            "nivel": "Nivel",
            "modulo": "Módulo",
            "accion": "Acción",
            "detalles": "Detalles"
        },
        height=400
    )
    
    # Opciones de exportación
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Exportar a CSV", use_container_width=True):
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar CSV",
                data=csv,
                file_name=f"logs_sistema_{ahora_argentina().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("🗑️ Limpiar Logs Antiguos", use_container_width=True, type="secondary"):
            if _limpiar_logs_antiguos(sheet_logs, df_logs):
                st.success("✅ Logs antiguos eliminados")
                return {'needs_refresh': True}
    
    st.markdown('</div>', unsafe_allow_html=True)
    return {'needs_refresh': False}

def _cargar_logs(sheet_logs):
    """Carga los logs desde Google Sheets"""
    try:
        # Obtener todos los datos
        datos = sheet_logs.get_all_values()
        
        if len(datos) <= 1:  # Solo encabezados o vacío
            return pd.DataFrame(columns=COLUMNAS_LOGS)
        
        # Crear DataFrame
        df = pd.DataFrame(datos[1:], columns=COLUMNAS_LOGS)
        
        # Convertir tipos de datos
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        # Filtrar registros válidos
        df = df.dropna(subset=['timestamp'])
        
        # Ordenar por fecha más reciente primero
        df = df.sort_values('timestamp', ascending=False)
        
        return df
        
    except Exception as e:
        st.error(f"❌ Error al cargar logs: {str(e)}")
        return pd.DataFrame(columns=COLUMNAS_LOGS)

def _mostrar_estadisticas_logs(df_logs):
    """Muestra estadísticas de los logs"""
    if df_logs.empty:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total = len(df_logs)
        st.metric("Total registros", total)
    
    with col2:
        usuarios_unicos = df_logs['usuario'].nunique()
        st.metric("Usuarios únicos", usuarios_unicos)
    
    with col3:
        errores = len(df_logs[df_logs['nivel'] == 'ERROR'])
        st.metric("Errores", errores)
    
    with col4:
        modulos = df_logs['modulo'].nunique()
        st.metric("Módulos", modulos)

def _limpiar_logs_antiguos(sheet_logs, df_logs):
    """Elimina logs con más de 30 días"""
    try:
        fecha_limite = ahora_argentina() - pd.Timedelta(days=30)
        logs_antiguos = df_logs[df_logs['timestamp'] < fecha_limite]
        
        if logs_antiguos.empty:
            st.info("No hay logs antiguos para eliminar")
            return False
        
        # Obtener índices de las filas a eliminar
        datos = sheet_logs.get_all_values()
        filas_a_eliminar = []
        
        for i, fila in enumerate(datos[1:], start=2):  # Saltar encabezado
            if len(fila) > 0:
                try:
                    fecha_log = pd.to_datetime(fila[0])
                    if fecha_log < fecha_limite:
                        filas_a_eliminar.append(i)
                except:
                    continue
        
        # Eliminar filas (empezando desde la última para evitar problemas de indexación)
        for fila_num in sorted(filas_a_eliminar, reverse=True):
            sheet_logs.delete_rows(fila_num)
        
        st.success(f"✅ Se eliminaron {len(filas_a_eliminar)} logs antiguos")
        return True
        
    except Exception as e:
        st.error(f"❌ Error al limpiar logs: {str(e)}")
        return False

# FUNCIÓN PARA REGISTRAR NUEVOS LOGS (se usará en toda la aplicación)
def registrar_log(usuario, nivel, modulo, accion, detalles="", ip_address=""):
    """Registra una nueva entrada en el log del sistema"""
    try:
        sheet_logs = st.session_state.get('sheet_logs')
        
        if sheet_logs is None:
            print("⚠️ No hay conexión a hoja de logs")
            return False
        
        nueva_entrada = [
            ahora_argentina().strftime('%Y-%m-%d %H:%M:%S'),
            usuario,
            nivel,
            modulo,
            accion,
            detalles[:490],  # Limitar tamaño para evitar errores
            ip_address
        ]
        
        # ✅ Usar el api_manager para operaciones seguras
        success, error = api_manager.safe_sheet_operation(
            sheet_logs.append_row,
            nueva_entrada
        )
        
        return success
        
    except Exception as e:
        print(f"Error al registrar log: {str(e)}")
        return False