"""
Componente de autenticación profesional estilo CRM
Versión mejorada con diseño elegante
"""
import streamlit as st
from utils.data_manager import safe_get_sheet_data
from config.settings import (
    WORKSHEET_USUARIOS,
    COLUMNAS_USUARIOS,
    PERMISOS_POR_ROL
)
import time
from utils.styles import get_loading_spinner

def init_auth_session():
    """Inicializa las variables de sesión de autenticación"""
    if 'auth' not in st.session_state:
        st.session_state.auth = {
            'logged_in': False,
            'user_info': None,
            'login_attempts': 0
        }

def logout():
    """Cierra la sesión del usuario y limpia el estado"""
    st.session_state.auth = {'logged_in': False, 'user_info': None, 'login_attempts': 0}
    st.cache_data.clear()
    st.success("Sesión cerrada correctamente")

def verify_credentials(username, password, sheet_usuarios):
    """
    Verifica las credenciales del usuario contra Google Sheets
    
    Args:
        username: Nombre de usuario
        password: Contraseña
        sheet_usuarios: Hoja de cálculo de usuarios
    
    Returns:
        Diccionario con información del usuario o None si falla
    """
    try:
        df_usuarios = safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)
        
        if df_usuarios.empty:
            return None
            
        # Normalización de datos
        df_usuarios["username"] = df_usuarios["username"].str.strip().str.lower()
        df_usuarios["password"] = df_usuarios["password"].astype(str).str.strip()
        
        # Manejo flexible de campo 'activo'
        df_usuarios["activo"] = df_usuarios["activo"].astype(str).str.upper().isin([
            "SI", "TRUE", "1", "SÍ", "VERDADERO", "YES", "Y"
        ])
        
        # Buscar usuario
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

def render_login_form(sheet_usuarios):
    """
    Renderiza el formulario de login estilo Facebook con tema Monokai
    Diseño responsive: horizontal en desktop, vertical en móvil
    """
    
    # CSS personalizado para el login estilo Facebook
    login_styles = """
    <style>
    .login-main-container {
        min-height: 100vh;
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .login-container {
        background: var(--bg-card);
        border-radius: var(--radius-2xl);
        border: 2px solid var(--border-color);
        box-shadow: var(--shadow-xl);
        overflow: hidden;
        max-width: 1000px;
        width: 100%;
    }
    
    .login-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        min-height: 500px;
    }
    
    .login-left {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--info-color) 100%);
        padding: 3rem 2rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .login-left::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: float 6s ease-in-out infinite;
    }
    
    .login-right {
        padding: 3rem 2rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .login-logo {
        font-size: 4rem;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #F8F8F2 0%, #CFCFC2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        position: relative;
        z-index: 2;
    }
    
    .login-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        color: #F8F8F2;
        position: relative;
        z-index: 2;
        font-family: 'Fira Code', monospace;
    }
    
    .login-subtitle {
        color: rgba(248, 248, 242, 0.9);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        position: relative;
        z-index: 2;
        max-width: 300px;
    }
    
    .login-features {
        text-align: left;
        margin-top: 2rem;
        position: relative;
        z-index: 2;
    }
    
    .login-feature {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        color: rgba(248, 248, 242, 0.9);
    }
    
    .login-feature-icon {
        font-size: 1.2rem;
        margin-right: 0.75rem;
        background: linear-gradient(135deg, #66D9EF 0%, #AE81FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        margin-bottom: 0.5rem;
        color: var(--text-secondary);
        font-weight: 600;
        font-size: 0.9rem;
        font-family: 'Fira Code', monospace;
    }
    
    .login-input {
        width: 100%;
        padding: 1rem 1.25rem;
        border: 2px solid var(--border-color);
        border-radius: var(--radius-lg);
        background: var(--bg-surface);
        color: var(--text-primary);
        font-size: 1rem;
        font-family: 'Fira Code', monospace;
        transition: var(--transition-base);
    }
    
    .login-input:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(102, 217, 239, 0.2);
        background: var(--bg-card);
    }
    
    .login-button {
        width: 100%;
        padding: 1rem;
        background: var(--gradient-primary);
        color: #272822 !important;
        border: none;
        border-radius: var(--radius-lg);
        font-size: 1rem;
        font-weight: 700;
        font-family: 'Fira Code', monospace;
        cursor: pointer;
        transition: var(--transition-base);
        margin-top: 1rem;
    }
    
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .login-footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid var(--border-light);
        color: var(--text-muted);
        font-size: 0.85rem;
    }
    
    .login-error {
        background: rgba(255, 97, 136, 0.15);
        border: 2px solid var(--danger-color);
        color: var(--danger-color);
        padding: 1rem;
        border-radius: var(--radius-lg);
        margin: 1rem 0;
        text-align: center;
        font-family: 'Fira Code', monospace;
        font-weight: 600;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .login-grid {
            grid-template-columns: 1fr;
        }
        
        .login-left {
            padding: 2rem 1.5rem;
            min-height: 300px;
        }
        
        .login-right {
            padding: 2rem 1.5rem;
        }
        
        .login-title {
            font-size: 2rem;
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(5deg); }
    }
    </style>
    """
    
    st.markdown(login_styles, unsafe_allow_html=True)
    
    # Inicializar estado de login
    if 'login_loading' not in st.session_state:
        st.session_state.login_loading = False
    if 'login_username' not in st.session_state:
        st.session_state.login_username = ""
    if 'login_password' not in st.session_state:
        st.session_state.login_password = ""

    # Contenedor principal
    st.markdown("""
    <div class="login-main-container">
        <div class="login-container">
            <div class="login-grid">
                <div class="login-left">
                    <div class="login-logo">📋</div>
                    <h1 class="login-title">Fusion CRM</h1>
                    <p class="login-subtitle">Sistema profesional de gestión de reclamos</p>
                    
                    <div class="login-features">
                        <div class="login-feature">
                            <span class="login-feature-icon">⚡</span>
                            Gestión eficiente de reclamos
                        </div>
                        <div class="login-feature">
                            <span class="login-feature-icon">🔧</span>
                            Seguimiento técnico en tiempo real
                        </div>
                        <div class="login-feature">
                            <span class="login-feature-icon">📊</span>
                            Reportes y métricas avanzadas
                        </div>
                    </div>
                </div>
                
                <div class="login-right">
    """, unsafe_allow_html=True)

    # Mostrar spinner si está cargando
    if st.session_state.login_loading:
        st.markdown(get_loading_spinner(), unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-top: 20px;">
            <p style="color: var(--text-secondary); font-family: 'Fira Code', monospace;">
                Verificando credenciales...
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Procesar autenticación
        try:
            user_info = verify_credentials(
                st.session_state.login_username, 
                st.session_state.login_password, 
                sheet_usuarios
            )
            
            if user_info:
                st.session_state.auth = {
                    'logged_in': True,
                    'user_info': user_info,
                    'login_attempts': 0
                }
                st.session_state.login_loading = False
                st.rerun()
            else:
                st.session_state.auth['login_attempts'] += 1
                st.session_state.login_loading = False
                st.rerun()
                
        except Exception as e:
            st.session_state.login_loading = False
            st.error(f"Error en autenticación: {str(e)}")
            st.rerun()
    
    else:
        # Formulario de login
        with st.form("login_form", clear_on_submit=False):
            st.markdown("""
            <h2 style="color: var(--text-primary); margin-bottom: 2rem; text-align: center; font-family: 'Fira Code', monospace;">
                Iniciar Sesión
            </h2>
            """, unsafe_allow_html=True)
            
            # Campo de usuario
            username = st.text_input(
                "Usuario",
                value=st.session_state.login_username,
                placeholder="Ingresa tu usuario",
                key="login_user_input"
            ).strip()
            
            # Campo de contraseña
            password = st.text_input(
                "Contraseña",
                type="password",
                value=st.session_state.login_password,
                placeholder="Ingresa tu contraseña",
                key="login_pass_input"
            )
            
            # Botón de login
            if st.form_submit_button("🚀 Ingresar al sistema", use_container_width=True):
                if not username or not password:
                    st.error("⚠️ Usuario y contraseña son requeridos")
                else:
                    st.session_state.login_username = username
                    st.session_state.login_password = password
                    st.session_state.login_loading = True
                    st.rerun()

    # Footer y cierre de contenedores
    st.markdown("""
                </div>
            </div>
            
            <div class="login-footer">
                <p>© 2025 Fusion CRM • v2.3.0</p>
                <p style="font-size: 0.8rem; margin-top: 5px; color: var(--text-muted);">
                    Sistema optimizado con tecnología Monokai Pro
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def check_authentication():
    """Verifica si el usuario está autenticado"""
    init_auth_session()
    return st.session_state.auth['logged_in']

def auth_has_permission(required_permission):
    """Verifica si el usuario tiene el permiso requerido"""
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
    """Muestra la información del usuario en el sidebar con estilo Monokai"""
    if not check_authentication():
        return
        
    user_info = st.session_state.auth['user_info']
    role_config = {
        'admin': {'icon': '👑', 'color': '#FF6188', 'badge': 'Admin'},
        'oficina': {'icon': '💼', 'color': '#66D9EF', 'badge': 'Oficina'},
        'tecnico': {'icon': '🔧', 'color': '#A6E22E', 'badge': 'Técnico'},
        'supervisor': {'icon': '👔', 'color': '#AE81FF', 'badge': 'Supervisor'}
    }
    
    config = role_config.get(user_info['rol'].lower(), 
                           {'icon': '👤', 'color': '#75715E', 'badge': 'Usuario'})
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1.5rem; padding: 1.5rem; 
                background: var(--bg-card); border-radius: var(--radius-xl); 
                border: 1px solid var(--border-color);">
        <div style="font-size: 3.5rem; margin-bottom: 0.5rem; 
                    background: linear-gradient(135deg, {config['color']}, var(--primary-color));
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {config['icon']}
        </div>
        <h3 style="margin: 0; color: var(--text-primary); font-weight: 700; 
                   font-family: 'Fira Code', monospace;">
            {user_info['nombre']}
        </h3>
        <div style="background: rgba({int(config['color'][1:3], 16)}, {int(config['color'][3:5], 16)}, {int(config['color'][5:7], 16)}, 0.15); 
                  color: {config['color']}; 
                  padding: 0.5rem 1rem; 
                  border-radius: var(--radius-xl); 
                  font-size: 0.8rem; 
                  font-weight: 700;
                  font-family: 'Fira Code', monospace;
                  margin: 0.75rem 0;
                  display: inline-block;
                  border: 2px solid {config['color']};
                  text-transform: uppercase;
                  letter-spacing: 0.5px;">
            {config['badge']}
        </div>
        <p style="color: var(--text-secondary); margin: 0.5rem 0 0 0; 
                  font-size: 0.85rem; font-family: 'Fira Code', monospace;">
            @{user_info['username']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 **Cerrar sesión**", use_container_width=True, 
                 key="logout_btn", use_container_width=True,
                 help="Cerrar la sesión actual"):
        logout()
        st.rerun()