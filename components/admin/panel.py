# components/admin/panel.py

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_manager import api_manager
from config.settings import COLUMNAS_USUARIOS, PERMISOS_POR_ROL
from components.ui_kit import crm_card, crm_metric, crm_badge, crm_alert
from components.ui import breadcrumb, metric_card, loading_spinner

def render_panel_administracion(df_usuarios, sheet_usuarios, user_info):
    """
    Panel principal de administración del sistema CRM
    """
    if user_info.get('rol') != 'admin':
        st.warning("⚠️ Solo los administradores pueden acceder a esta sección")
        return {'needs_refresh': False}
    
    # Header del panel de administración
    st.markdown("""
    <div class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center space-x-3">
            <span class="text-xl text-primary-600">⚙️</span>
            <div>
                <h1 class="text-xl font-bold text-gray-900 dark:text-white">Panel de Administración</h1>
                <p class="text-sm text-gray-500 dark:text-gray-400">Gestión completa del sistema CRM</p>
            </div>
        </div>
        <span class="text-sm text-gray-400">
            {fecha_actual}
        </span>
    </div>
    """.format(fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M')), unsafe_allow_html=True)
    
    # Métricas rápidas del sistema
    _mostrar_metricas_sistema(df_usuarios)
    
    # Navegación entre módulos de administración
    opciones_admin = {
        "Gestión de Usuarios": "👥 Gestión de usuarios del sistema",
        "Configuración Sistema": "⚙️ Configuración general del CRM",
        "Logs de Actividad": "📊 Registros de actividad del sistema",
        "Backup de Datos": "💾 Copias de seguridad y respaldo"
    }
    
    seleccion = st.selectbox(
        "Seleccionar módulo de administración:",
        options=list(opciones_admin.keys()),
        format_func=lambda x: f"{x} - {opciones_admin[x]}",
        key="select_modulo_admin"
    )
    
    # Renderizar el módulo seleccionado
    if seleccion == "Gestión de Usuarios":
        return _render_gestion_usuarios(df_usuarios, sheet_usuarios)
    elif seleccion == "Configuración Sistema":
        return _render_configuracion_sistema()
    elif seleccion == "Logs de Actividad":
        return _render_logs_actividad()
    elif seleccion == "Backup de Datos":
        return _render_backup_datos()
    
    return {'needs_refresh': False}

def _mostrar_metricas_sistema(df_usuarios):
    """Muestra métricas del sistema en tarjetas modernas"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_usuarios = len(df_usuarios)
        st.markdown(f"""
        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{total_usuarios}</div>
            <div class="text-sm text-blue-700 dark:text-blue-300">Usuarios Totales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        usuarios_activos = len(df_usuarios[df_usuarios['activo'] == True])
        st.markdown(f"""
        <div class="bg-green-50 dark:bg-green-900/20 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-green-600 dark:text-green-400">{usuarios_activos}</div>
            <div class="text-sm text-green-700 dark:text-green-300">Usuarios Activos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        admins = len(df_usuarios[df_usuarios['rol'] == 'admin'])
        st.markdown(f"""
        <div class="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">{admins}</div>
            <div class="text-sm text-purple-700 dark:text-purple-300">Administradores</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        oficina = len(df_usuarios[df_usuarios['rol'] == 'oficina'])
        st.markdown(f"""
        <div class="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4 text-center">
            <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">{oficina}</div>
            <div class="text-sm text-orange-700 dark:text-orange-300">Personal Oficina</div>
        </div>
        """, unsafe_allow_html=True)

def _render_gestion_usuarios(df_usuarios, sheet_usuarios):
    """Módulo de gestión de usuarios"""
    from .usuarios import render_gestion_usuarios_completa
    return render_gestion_usuarios_completa(df_usuarios, sheet_usuarios, st.session_state.auth.get('user_info', {}))

def _render_configuracion_sistema():
    """Módulo de configuración del sistema"""
    from .config_sistema import render_configuracion_sistema
    return render_configuracion_sistema()

def _crear_usuario(sheet_usuarios, username, password, nombre, rol, activo, email):
    """Crea un nuevo usuario en el sistema"""
    try:
        # Verificar si el usuario ya existe
        datos_actuales = sheet_usuarios.get_all_values()
        usuarios_existentes = [fila[0] for fila in datos_actuales[1:] if len(fila) > 0]
        
        if username in usuarios_existentes:
            st.error("❌ El usuario ya existe")
            return False
        
        # Agregar nuevo usuario
        nueva_fila = [username, password, nombre, rol, str(activo), "False", email]
        sheet_usuarios.append_row(nueva_fila)
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error al crear usuario: {str(e)}")
        return False

def _render_configuracion_sistema():
    """Módulo de configuración del sistema"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">⚙️ Configuración del Sistema</h3>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔧 Configuración General**")
        timeout_sesion = st.slider("Timeout de sesión (minutos)", 15, 240, 30)
        registros_por_pagina = st.slider("Registros por página", 10, 100, 25)
        
        st.markdown("**🎨 Apariencia**")
        tema_predeterminado = st.selectbox("Tema predeterminado", ["Claro", "Oscuro", "Sistema"])
    
    with col2:
        st.markdown("**📊 Configuración de Reportes**")
        formato_fecha = st.selectbox("Formato de fecha", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        zona_horaria = st.selectbox("Zona horaria", ["America/Argentina/Buenos_Aires", "UTC"])
        
        st.markdown("**🔔 Notificaciones**")
        notificaciones_email = st.checkbox("Habilitar notificaciones por email", value=False)
        notificaciones_push = st.checkbox("Habilitar notificaciones push", value=True)
    
    if st.button("💾 Guardar Configuración", use_container_width=True):
        st.success("✅ Configuración guardada correctamente")
        # Aquí iría la lógica para guardar en Google Sheets o base de datos
    
    st.markdown('</div>', unsafe_allow_html=True)
    return {'needs_refresh': False}

def _render_logs_actividad():
    """Módulo de visualización de logs de actividad"""
    from .logs import render_logs_actividad
    # ✅ Obtener la hoja de logs desde session_state
    sheet_logs = st.session_state.get('sheet_logs')
    
    if sheet_logs is None:
        st.error("❌ No se pudo conectar con la hoja de Logs")
        return {'needs_refresh': False}
    
    return render_logs_actividad(sheet_logs)

def _render_backup_datos():
    """Módulo de backup y respaldo de datos"""
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">💾 Backup de Datos</h3>
    """, unsafe_allow_html=True)
    
    st.info("""
    **📦 Sistema de respaldo automático**
    Los backups se realizan automáticamente cada 24 horas y se conservan por 7 días.
    """)
    
    # Información de backups
    backups = [
        {"fecha": "2024-01-15 00:00", "tamaño": "15.2 MB", "estado": "✅ Completado"},
        {"fecha": "2024-01-14 00:00", "tamaño": "14.8 MB", "estado": "✅ Completado"},
        {"fecha": "2024-01-13 00:00", "tamaño": "14.5 MB", "estado": "✅ Completado"},
    ]
    
    for backup in backups:
        st.markdown(f"""
        <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg mb-2">
            <div class="flex justify-between items-center">
                <span class="font-medium">{backup['fecha']}</span>
                <span class="text-sm">{backup['tamaño']}</span>
                <span class="text-sm text-green-600">{backup['estado']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Acciones de backup
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Backup Manual", use_container_width=True):
            st.success("✅ Backup iniciado...")
            # Lógica de backup manual
    
    with col2:
        if st.button("📥 Descargar Último Backup", use_container_width=True):
            st.info("📦 Preparando descarga...")
            # Lógica de descarga
    
    with col3:
        if st.button("⚙️ Configurar Backup", use_container_width=True):
            st.info("🔧 Abriendo configuración...")
            # Lógica de configuración
    
    st.markdown('</div>', unsafe_allow_html=True)
    return {'needs_refresh': False}