"""
Componente de navegación profesional con iconos y estados activos
Versión 3.0 - Diseño CRM profesional
"""
import streamlit as st
from utils.styles import get_main_styles, get_loading_spinner, loading_indicator
from utils.permissions import has_permission

def render_main_navigation():
    """
    Renderiza la navegacion horizontal principal con estilo Monokai
    """
    
    # Obtener pagina actual
    current_page = st.session_state.get('current_page', 'Inicio')
    
    st.markdown("""
    <div style="
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        border: 2px solid var(--border-color);
        padding: 1rem;
        margin: 2rem 0;
        box-shadow: var(--shadow-md);
    ">
        <h3 style="
            margin: 0 0 1rem 0;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-family: 'Fira Code', monospace;
        ">
            <span style="font-size: 1.5rem;">??</span>
            Navegacion Principal
        </h3>
    """, unsafe_allow_html=True)
    
    # Opciones de navegacion
    opciones_navegacion = [
        {"key": "Inicio", "icon": "??", "label": "Inicio"},
        {"key": "Reclamos cargados", "icon": "??", "label": "Reclamos"},
        {"key": "Gestion de clientes", "icon": "??", "label": "Clientes"},
        {"key": "Imprimir reclamos", "icon": "???", "label": "Imprimir"},
        {"key": "Seguimiento tecnico", "icon": "??", "label": "Tecnico"},
        {"key": "Cierre de Reclamos", "icon": "?", "label": "Cierre"}
    ]
    
    # Crear columnas para los botones de navegacion
    cols = st.columns(len(opciones_navegacion))
    
    for i, item in enumerate(opciones_navegacion):
        with cols[i]:
            # Verificar permisos
            permiso_requerido = OPCIONES_PERMISOS.get(item["key"])
            if permiso_requerido and not st.session_state.get('auth', {}).get('user_info', {}).get('permisos', []):
                continue
                
            # Determinar si es la pagina activa
            is_active = current_page == item["key"]
            
            # Estilos dinamicos
            button_bg = "var(--gradient-primary)" if is_active else "var(--bg-surface)"
            text_color = "#272822" if is_active else "var(--text-primary)"
            border_color = "var(--primary-color)" if is_active else "var(--border-color)"
            
            if st.button(
                f"{item['icon']} {item['label']}",
                key=f"nav_{item['key'].replace(' ', '_').lower()}",
                use_container_width=True,
                help=f"Ir a {item['label']}"
            ):
                st.session_state.current_page = item["key"]
                st.rerun()
            
            # Aplicar estilos CSS al boton
            st.markdown(f"""
            <style>
            div[data-testid="stButton"] > button[kind="secondary"] {{
                background: {button_bg} !important;
                color: {text_color} !important;
                border: 2px solid {border_color} !important;
                font-weight: {600 if is_active else 500} !important;
                font-family: 'Fira Code', monospace !important;
                transition: var(--transition-base) !important;
            }}
            
            div[data-testid="stButton"] > button[kind="secondary"]:hover {{
                transform: translateY(-2px) !important;
                box-shadow: var(--shadow-lg) !important;
                border-color: var(--primary-color) !important;
            }}
            </style>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_quick_actions():
    """
    Renderiza acciones rapidas debajo de la navegacion principal
    """
    
    quick_actions = [
        {"icon": "?", "label": "Nuevo Reclamo", "action": "nuevo_reclamo"},
        {"icon": "??", "label": "Dashboard", "action": "dashboard"},
        {"icon": "??", "label": "Buscar", "action": "buscar"},
        {"icon": "??", "label": "Hoy", "action": "hoy"}
    ]
    
    st.markdown("""
    <div style="
        background: var(--bg-surface);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
        padding: 1rem;
        margin-bottom: 2rem;
    ">
        <h4 style="
            margin: 0 0 0.75rem 0;
            color: var(--text-secondary);
            font-family: 'Fira Code', monospace;
            font-size: 0.9rem;
        ">
            ?? Acciones Rapidas
        </h4>
    """, unsafe_allow_html=True)
    
    # Botones de acciones rapidas
    cols = st.columns(len(quick_actions))
    
    for i, action in enumerate(quick_actions):
        with cols[i]:
            if st.button(
                f"{action['icon']}",
                key=f"quick_{action['action']}",
                use_container_width=True,
                help=action["label"]
            ):
                handle_quick_action(action["action"])
    
    st.markdown("</div>", unsafe_allow_html=True)

def handle_quick_action(action):
    """
    Maneja las acciones rapidas
    """
    action_handlers = {
        "nuevo_reclamo": lambda: st.session_state.update({"current_page": "Inicio", "focus_form": True}),
        "dashboard": lambda: st.session_state.update({"current_page": "Reclamos cargados", "view_mode": "dashboard"}),
        "buscar": lambda: st.session_state.update({"show_search": True}),
        "hoy": lambda: st.session_state.update({"filter_date": "today"})
    }
    
    if action in action_handlers:
        action_handlers[action]()
        st.rerun()

def render_breadcrumb():
    """
    Renderiza el breadcrumb de navegacion
    """
    current_page = st.session_state.get('current_page', 'Inicio')
    
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 1.5rem;
        background: var(--bg-surface);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        margin: 1rem 0 2rem 0;
        font-family: 'Fira Code', monospace;
    ">
        <span style="color: var(--text-muted);">??</span>
        <span style="color: var(--text-secondary);">Fusion CRM</span>
        <span style="color: var(--text-muted);">/</span>
        <span style="color: var(--primary-color); font-weight: 600;">{get_page_icon(current_page)} {current_page}</span>
    </div>
    """, unsafe_allow_html=True)

def render_mobile_navigation():
    """
    Renderiza navegacion optimizada para moviles
    """
    if st.session_state.get('is_mobile', False):
        st.markdown("""
        <div style="
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--bg-card);
            border-top: 2px solid var(--border-color);
            padding: 0.5rem;
            z-index: 1000;
        ">
        """, unsafe_allow_html=True)
        
        mobile_items = [
            {"key": "Inicio", "icon": "??", "label": "Inicio"},
            {"key": "Reclamos cargados", "icon": "??", "label": "Reclamos"},
            {"key": "Gestion de clientes", "icon": "??", "label": "Clientes"},
            {"key": "Cierre de Reclamos", "icon": "?", "label": "Cierre"}
        ]
        
        cols = st.columns(len(mobile_items))
        
        for i, item in enumerate(mobile_items):
            with cols[i]:
                if st.button(
                    item["icon"],
                    key=f"mobile_{item['key']}",
                    use_container_width=True,
                    help=item["label"]
                ):
                    st.session_state.current_page = item["key"]
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# Funcion de compatibilidad
def render_navigation():
    """
    Funcion de compatibilidad para navegacion anterior
    """
    return render_main_navigation()