"""
Componente de autenticación profesional estilo CRM
Versión 4.0 - Diseño moderno con TailwindCSS
"""

import streamlit as st
from utils.data_manager import safe_get_sheet_data
from config.settings import (
    WORKSHEET_USUARIOS,
    COLUMNAS_USUARIOS,
    PERMISOS_POR_ROL
)
import time

def init_auth_session():
    """Inicializa las variables de sesión"""
    if 'auth' not in st.session_state:
        st.session_state.auth = {
            'logged_in': False,
            'user_info': None
        }

def logout():
    """Cierra la sesión del usuario"""
    st.session_state.auth = {'logged_in': False, 'user_info': None}
    st.cache_data.clear()

def verify_credentials(username, password, sheet_usuarios):
    try:
        df_usuarios = safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)
        
        # Normalización de datos
        df_usuarios["username"] = df_usuarios["username"].str.strip().str.lower()
        df_usuarios["password"] = df_usuarios["password"].astype(str).str.strip()
        
        # Manejo flexible de campo 'activo'
        df_usuarios["activo"] = df_usuarios["activo"].astype(str).str.upper().isin(["SI", "TRUE", "1", "SÍ", "VERDADERO"])
        
        usuario = df_usuarios[
            (df_usuarios["username"] == username.strip().lower()) & 
            (df_usuarios["password"] == password.strip()) &
            (df_usuarios["activo"])
        ]
        
        if not usuario.empty:
            return {
                "username": usuario.iloc[0]["username"],
                "nombre": usuario.iloc[0]["nombre"],
                "rol": usuario.iloc[0]["rol"].lower(),
                "permisos": PERMISOS_POR_ROL.get(usuario.iloc[0]["rol"].lower(), {}).get('permisos', [])
            }
    except Exception as e:
        st.error(f"Error en autenticación: {str(e)}")
    return None

def render_login(sheet_usuarios):
    """Formulario de login con diseño moderno CRM"""
    
    # CSS personalizado para el login
    login_styles = """
    <style>
    .login-container {
        max-width: 420px;
        margin: 2rem auto;
        padding: 0;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .dark .login-container {
        background: #1f2937;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    
    .login-header {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        padding: 2.5rem 2rem;
        text-align: center;
        color: white;
    }
    
    .login-content {
        padding: 2rem;
    }
    
    .login-form-group {
        margin-bottom: 1.5rem;
    }
    
    .login-label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: 500;
        color: #374151;
    }
    
    .dark .login-label {
        color: #d1d5db;
    }
    
    .login-input {
        width: 100%;
        padding: 0.75rem 1rem;
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        font-size: 1rem;
        transition: all 0.2s;
    }
    
    .dark .login-input {
        background: #374151;
        border-color: #4b5563;
        color: white;
    }
    
    .login-input:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    .login-button {
        width: 100%;
        padding: 0.875rem;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .login-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .login-footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e5e7eb;
        color: #6b7280;
    }
    
    .dark .login-footer {
        border-color: #374151;
        color: #9ca3af;
    }
    </style>
    """
    
    st.markdown(login_styles, unsafe_allow_html=True)
    
    # Inicializar estado de carga
    if 'login_loading' not in st.session_state:
        st.session_state.login_loading = False
    if 'login_attempt' not in st.session_state:
        st.session_state.login_attempt = False
    
    # Mostrar spinner si está cargando
    if st.session_state.login_loading:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔐</div>
                <h1 style="margin: 0; font-size: 1.5rem; font-weight: 700;">Fusion CRM</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Verificando credenciales...</p>
            </div>
            <div class="login-content" style="text-align: center;">
                <div style="display: inline-block; width: 2rem; height: 2rem; border: 2px solid #3b82f6; 
                          border-top: 2px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                <p style="color: #6b7280; margin-top: 1rem;">Autenticando...</p>
            </div>
        </div>
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Procesar la autenticación
        try:
            user_info = verify_credentials(
                st.session_state.login_username, 
                st.session_state.login_password, 
                sheet_usuarios
            )
            
            if user_info:
                st.session_state.auth = {
                    'logged_in': True,
                    'user_info': user_info
                }
                st.session_state.login_loading = False
                st.session_state.login_attempt = False
                st.rerun()
            else:
                st.session_state.login_loading = False
                st.session_state.login_attempt = True
                st.rerun()
                
        except Exception as e:
            st.session_state.login_loading = False
            st.session_state.login_attempt = True
            st.rerun()
    
    else:
        # Formulario de login principal
        st.markdown("""
        <div class="login-container">
            <div class="login-header">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔐</div>
                <h1 style="margin: 0; font-size: 1.5rem; font-weight: 700;">Fusion CRM</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Sistema de gestión de reclamos</p>
            </div>
            
            <div class="login-content">
        """, unsafe_allow_html=True)
        
        # Mostrar mensaje de error si hubo un intento fallido
        if st.session_state.login_attempt:
            st.markdown("""
            <div style="background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; 
                      padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">❌</span>
                    <span>Credenciales incorrectas o usuario inactivo</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.login_attempt = False
        
        # Formulario de login
        with st.form("login_form", clear_on_submit=True):
            # Campo de usuario
            st.markdown('<div class="login-form-group">', unsafe_allow_html=True)
            st.markdown('<label class="login-label">Usuario</label>', unsafe_allow_html=True)
            username = st.text_input("Usuario", placeholder="Ingresa tu usuario", 
                                   label_visibility="collapsed", key="login_username")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Campo de contraseña
            st.markdown('<div class="login-form-group">', unsafe_allow_html=True)
            st.markdown('<label class="login-label">Contraseña</label>', unsafe_allow_html=True)
            password = st.text_input("Contraseña", type="password", 
                                   placeholder="Ingresa tu contraseña", 
                                   label_visibility="collapsed", key="login_password")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botón de envío
            if st.form_submit_button("Ingresar al sistema", use_container_width=True):
                if not username or not password:
                    st.error("Usuario y contraseña son requeridos")
                else:
                    # Guardar credenciales y activar loading
                    st.session_state.login_username = username
                    st.session_state.login_password = password
                    st.session_state.login_loading = True
                    st.rerun()
        
        st.markdown("""
            </div>
            
            <div class="login-footer">
                <p style="margin: 0; font-size: 0.875rem;">© 2025 Fusion CRM • v2.3.0</p>
                <p style="margin: 0.25rem 0 0 0; font-size: 0.75rem; opacity: 0.8;">Sistema optimizado para gestión eficiente</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def check_authentication():
    """Verifica si el usuario está autenticado"""
    init_auth_session()
    return st.session_state.auth['logged_in']

def has_permission(required_permission):
    """Verifica permisos del usuario"""
    if not check_authentication():
        return False
        
    user_info = st.session_state.auth.get('user_info')
    if not user_info:
        return False
        
    # Admin tiene acceso completo
    if user_info['rol'] == 'admin':
        return True
        
    return required_permission in user_info.get('permisos', [])

def render_user_info():
    """Información del usuario con diseño moderno"""
    if not check_authentication():
        return
        
    user_info = st.session_state.auth['user_info']
    role_config = {
        'admin': {'icon': '👑', 'color': '#f59e0b', 'badge': 'Administrador'},
        'oficina': {'icon': '💼', 'color': '#3b82f6', 'badge': 'Oficina'},
        'tecnico': {'icon': '🔧', 'color': '#10b981', 'badge': 'Técnico'},
        'supervisor': {'icon': '👔', 'color': '#8b5cf6', 'badge': 'Supervisor'}
    }
    
    config = role_config.get(user_info['rol'].lower(), {'icon': '👤', 'color': '#6b7280', 'badge': 'Usuario'})
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 1.5rem 1rem;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, {config['color']}, #3b82f6); 
                 -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {config['icon']}
        </div>
        <h3 style="margin: 0 0 0.5rem 0; color: var(--text-primary); font-weight: 600; font-size: 1.1rem;">
            {user_info['nombre']}
        </h3>
        <div style="background: {config['color']}15; color: {config['color']}; 
                 padding: 0.25rem 0.75rem; border-radius: 1rem; font-size: 0.8rem; 
                 font-weight: 500; display: inline-block; border: 1px solid {config['color']}30;">
            {config['badge']}
        </div>
        <p style="color: var(--text-secondary); margin: 0.5rem 0 0 0; font-size: 0.85rem;">
            @{user_info['username']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.button("🚪 Cerrar sesión", use_container_width=True, key="logout_btn"):
        logout()
        st.rerun()