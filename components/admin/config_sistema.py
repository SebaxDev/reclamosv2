# components/admin/config_sistema.py

import streamlit as st
import pandas as pd
from utils.api_manager import api_manager

def render_configuracion_sistema():
    """Módulo de configuración persistente del sistema"""
    
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">⚙️ Configuración del Sistema</h3>
    """, unsafe_allow_html=True)
    
    # Cargar configuración actual
    config_actual = _cargar_configuracion()
    
    # Pestañas de configuración
    tab1, tab2, tab3 = st.tabs(["🔧 General", "🎨 Apariencia", "🔔 Notificaciones"])
    
    with tab1:
        _config_general(config_actual)
    
    with tab2:
        _config_apariencia(config_actual)
    
    with tab3:
        _config_notificaciones(config_actual)
    
    st.markdown('</div>', unsafe_allow_html=True)
    return {'needs_refresh': False}

def _cargar_configuracion():
    """Carga la configuración actual del sistema"""
    # Por ahora valores por defecto, luego se conectarán con Google Sheets
    return {
        "timeout_sesion": 30,
        "registros_por_pagina": 25,
        "tema_predeterminado": "Sistema",
        "formato_fecha": "DD/MM/YYYY",
        "zona_horaria": "America/Argentina/Buenos_Aires",
        "notificaciones_email": False,
        "notificaciones_push": True,
        "backup_automatico": True,
        "dias_retencion_backup": 7
    }

def _config_general(config_actual):
    """Configuración general del sistema"""
    st.markdown("### 🔧 Configuración General")
    
    col1, col2 = st.columns(2)
    
    with col1:
        timeout_sesion = st.slider(
            "Timeout de sesión (minutos)", 
            15, 240, config_actual["timeout_sesion"],
            help="Tiempo de inactividad antes de cerrar sesión automáticamente"
        )
    
    with col2:
        registros_por_pagina = st.slider(
            "Registros por página", 
            10, 100, config_actual["registros_por_pagina"],
            help="Cantidad de registros a mostrar en las tablas"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        formato_fecha = st.selectbox(
            "Formato de fecha",
            ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
            index=["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"].index(config_actual["formato_fecha"])
        )
    
    with col2:
        zona_horaria = st.selectbox(
            "Zona horaria",
            ["America/Argentina/Buenos_Aires", "UTC", "America/New_York"],
            index=["America/Argentina/Buenos_Aires", "UTC", "America/New_York"].index(config_actual["zona_horaria"])
        )
    
    if st.button("💾 Guardar Configuración General", use_container_width=True):
        _guardar_configuracion({**config_actual, "timeout_sesion": timeout_sesion, "registros_por_pagina": registros_por_pagina, "formato_fecha": formato_fecha, "zona_horaria": zona_horaria})
        st.success("✅ Configuración general guardada")

def _config_apariencia(config_actual):
    """Configuración de apariencia"""
    st.markdown("### 🎨 Configuración de Apariencia")
    
    tema_predeterminado = st.selectbox(
        "Tema predeterminado", 
        ["Sistema", "Claro", "Oscuro"],
        index=["Sistema", "Claro", "Oscuro"].index(config_actual["tema_predeterminado"]),
        help="Tema visual predeterminado de la aplicación"
    )
    
    if st.button("💾 Guardar Configuración Apariencia", use_container_width=True):
        _guardar_configuracion({**config_actual, "tema_predeterminado": tema_predeterminado})
        st.success("✅ Configuración de apariencia guardada")

def _config_notificaciones(config_actual):
    """Configuración de notificaciones y backup"""
    st.markdown("### 🔔 Configuración de Notificaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        notificaciones_email = st.checkbox(
            "Habilitar notificaciones por email", 
            value=config_actual["notificaciones_email"],
            help="Enviar notificaciones por correo electrónico"
        )
    
    with col2:
        notificaciones_push = st.checkbox(
            "Habilitar notificaciones push", 
            value=config_actual["notificaciones_push"],
            help="Mostrar notificaciones en tiempo real dentro de la aplicación"
        )
    
    st.markdown("### 💾 Configuración de Backup")
    
    backup_automatico = st.checkbox(
        "Backup automático diario", 
        value=config_actual["backup_automatico"],
        help="Realizar copias de seguridad automáticas cada 24 horas"
    )
    
    if backup_automatico:
        dias_retencion_backup = st.slider(
            "Días de retención de backups",
            1, 30, config_actual["dias_retencion_backup"],
            help="Cantidad de días que se conservan las copias de seguridad"
        )
    else:
        dias_retencion_backup = config_actual["dias_retencion_backup"]
    
    if st.button("💾 Guardar Configuración Notificaciones", use_container_width=True):
        _guardar_configuracion({
            **config_actual, 
            "notificaciones_email": notificaciones_email,
            "notificaciones_push": notificaciones_push,
            "backup_automatico": backup_automatico,
            "dias_retencion_backup": dias_retencion_backup
        })
        st.success("✅ Configuración de notificaciones guardada")

def _guardar_configuracion(nueva_config):
    """Guarda la configuración en Google Sheets"""
    # Por ahora solo muestra el mensaje, luego se implementará la persistencia
    st.info("🔧 Función de persistencia en desarrollo - Los cambios se guardarán en Google Sheets")
    # Aquí irá el código para guardar en la hoja de configuración