"""
Componente de navegación profesional con TailwindCSS
Versión 4.0 - Diseño CRM moderno
"""

import streamlit as st
from utils.permissions import has_permission

def render_sidebar_navigation():
    """Renderiza la navegación lateral profesional con diseño moderno"""
    
    menu_items = [
        {"icon": "🏠", "label": "Inicio", "key": "Inicio", "permiso": "inicio"},
        {"icon": "📊", "label": "Reclamos cargados", "key": "Reclamos cargados", "permiso": "reclamos_cargados"},
        {"icon": "👥", "label": "Gestión de clientes", "key": "Gestión de clientes", "permiso": "gestion_clientes"},
        {"icon": "🖨️", "label": "Imprimir reclamos", "key": "Imprimir reclamos", "permiso": "imprimir_reclamos"},
        {"icon": "🔧", "label": "Seguimiento técnico", "key": "Seguimiento técnico", "permiso": "seguimiento_tecnico"},
        {"icon": "✅", "label": "Cierre de Reclamos", "key": "Cierre de Reclamos", "permiso": "cierre_reclamos"}
    ]
    
    # AGREGAR OPCIÓN DE ADMINISTRACIÓN SI EL USUARIO ES ADMIN
    if st.session_state.auth.get('user_info', {}).get('rol') == 'admin':
        menu_items.append(
            {"icon": "⚙️", "label": "Administración", "key": "Administración", "permiso": "admin"}
        )
    
    # Header de navegación
    st.sidebar.markdown("""
    <div style="padding: 1.25rem 1rem 1rem 1rem; border-bottom: 1px solid #e5e7eb; margin-bottom: 0.5rem;">
        <h3 style="margin: 0; color: #3b82f6; display: flex; align-items: center; gap: 0.5rem; font-size: 1.1rem; font-weight: 600;">
            <span style="font-size: 1.3rem;">🧭</span> Navegación
        </h3>
    </div>
    <style>
    .dark .sidebar-nav-item {
        border-color: #374151 !important;
    }
    .dark .sidebar-nav-item:hover {
        background: #374151 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Botones de navegación
    for item in menu_items:
        if not has_permission(item["permiso"]):
            continue
            
        is_active = st.session_state.get('current_page') == item["key"]
        
        # Estilos diferentes para estado activo/inactivo
        if is_active:
            st.sidebar.markdown(f"""
            <div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
                     color: white; padding: 0.75rem 1rem; margin: 0.25rem 0; border-radius: 0.5rem;
                     display: flex; align-items: center; gap: 0.75rem; font-weight: 500; cursor: pointer;">
                <span style="font-size: 1.2rem;">{item['icon']}</span>
                <span>{item['label']}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.sidebar.button(
                f"{item['icon']} {item['label']}", 
                key=f"nav_{item['key'].replace(' ', '_').lower()}",
                use_container_width=True,
                help=f"Ir a {item['label']}"
            ):
                st.session_state.current_page = item["key"]
                st.rerun()
    
    st.sidebar.markdown("---")

def render_user_info():
    """Renderiza información del usuario con diseño moderno"""
    if st.session_state.auth.get("logged_in", False):
        user_info = st.session_state.auth.get('user_info', {})
        
        role_config = {
            'admin': {'icon': '👑', 'color': '#f59e0b'},
            'oficina': {'icon': '💼', 'color': '#3b82f6'},
            'tecnico': {'icon': '🔧', 'color': '#10b981'},
            'supervisor': {'icon': '👔', 'color': '#8b5cf6'}
        }
        
        config = role_config.get(user_info.get('rol', '').lower(), {'icon': '👤', 'color': '#6b7280'})
        
        st.sidebar.markdown(f"""
        <div style="padding: 1.25rem 1rem; background: #f8fafc; border-radius: 0.75rem; border: 1px solid #e2e8f0; margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                <div style="font-size: 2rem; color: {config['color']};">{config['icon']}</div>
                <div>
                    <div style="font-weight: 600; color: #1e293b; font-size: 1rem;">Bienvenido</div>
                    <div style="color: {config['color']}; font-size: 0.9rem; font-weight: 500;">{user_info.get('nombre', 'Usuario')}</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="background: {config['color']}15; color: {config['color']}; 
                      padding: 0.25rem 0.5rem; border-radius: 0.375rem; font-size: 0.75rem; 
                      font-weight: 500; border: 1px solid {config['color']}30;">
                    {user_info.get('rol', 'Usuario')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_navigation():
    """Renderiza el menú de navegación horizontal (compatibilidad)"""
    
    st.markdown("""
    <div style="margin: 1.5rem 0; padding: 1.25rem; background: #f8fafc; border-radius: 0.75rem; border: 1px solid #e2e8f0;">
        <h3 style="margin: 0; color: #1e293b; display: flex; align-items: center; gap: 0.5rem; font-size: 1.1rem; font-weight: 600;">
            <span style="font-size: 1.3rem;">🧭</span> Navegación Principal
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Opciones de navegación con emojis
    opciones = [
        "🏠 Inicio", 
        "📊 Reclamos cargados", 
        "👥 Gestión de clientes",  
        "🖨️ Imprimir reclamos", 
        "🔧 Seguimiento técnico", 
        "✅ Cierre de Reclamos"
    ]
    
    # Crear columnas para la navegación horizontal
    cols = st.columns(len(opciones))
    
    for i, opcion in enumerate(opciones):
        with cols[i]:
            if st.button(opcion.split(" ", 1)[0], 
                        help=opcion,
                        use_container_width=True):
                st.session_state.current_page = opcion.split(" ", 1)[1]
                st.rerun()
    
    return st.session_state.get('current_page', 'Inicio')

def render_mobile_navigation():
    """Navegación optimizada para dispositivos móviles"""
    
    menu_items = [
        {"icon": "🏠", "label": "Inicio", "key": "Inicio"},
        {"icon": "📊", "label": "Reclamos", "key": "Reclamos cargados"},
        {"icon": "👥", "label": "Clientes", "key": "Gestión de clientes"},
        {"icon": "🖨️", "label": "Imprimir", "key": "Imprimir reclamos"},
        {"icon": "🔧", "label": "Técnico", "key": "Seguimiento técnico"},
        {"icon": "✅", "label": "Cierre", "key": "Cierre de Reclamos"}
    ]
    
    # Crear navegación tipo bottom bar para móviles
    st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; right: 0; background: white; 
                border-top: 1px solid #e5e7eb; padding: 0.5rem; z-index: 1000;
                display: flex; justify-content: space-around;">
    """, unsafe_allow_html=True)
    
    for item in menu_items:
        is_active = st.session_state.get('current_page') == item["key"]
        
        st.markdown(f"""
        <div style="text-align: center; padding: 0.5rem; { 'color: #3b82f6;' if is_active else 'color: #6b7280;' }">
            <div style="font-size: 1.5rem;">{item['icon']}</div>
            <div style="font-size: 0.75rem; margin-top: 0.25rem;">{item['label']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Espacio para evitar que el contenido quede oculto
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)