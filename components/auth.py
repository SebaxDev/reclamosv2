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
    """Verifica las credenciales del usuario contra Google Sheets"""
    try:
        df_usuarios = safe_get_sheet_data(sheet_usuarios, COLUMNAS_USUARIOS)
        
        if df_usuarios.empty:
            return None
            
        # Normalización
        df_usuarios["username"] = df_usuarios["username"].str.strip().str.lower()
        df_usuarios["password"] = df_usuarios["password"].astype(str).str.strip()
        
        # Campo activo flexible
        df_usuarios["activo"] = df_usuarios["activo"].astype(str).str.upper().isin([
            "SI", "TRUE", "1", "SÍ", "VERDADERO", "YES", "Y"
        ])
        
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
    """Renderiza el formulario de login estilo Facebook con tema Monokai"""
    
    # CSS personalizado para el formulario de login
    st.markdown("""
    <style>
    :root {
        --primary-color: #FF6188;
        --secondary-color: #66D9EF;
        --accent-color: #A6E22E;
        --purple-color: #AE81FF;
        --bg-primary: #2D2A2E;
        --bg-secondary: #403E41;
        --bg-card: #3A3739;
        --text-primary: #FCFCFA;
        --text-secondary: #CFCFC2;
        --text-muted: #75715E;
        --border-color: #5B595C;
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
    }
    
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        padding: 2rem;
        font-family: 'Fira Code', monospace;
    }
    
    .login-card {
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        overflow: hidden;
        width: 100%;
        max-width: 400px;
        position: relative;
    }
    
    .login-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 50%, var(--accent-color) 100%);
        padding: 3rem 2rem 2rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .login-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(180deg); }
    }
    
    .login-logo {
        font-size: 4rem;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }
    
    .login-title {
        color: white;
        font-size: 2rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .login-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    .login-form {
        padding: 2rem;
    }
    
    .form-group {
        margin-bottom: 1.5rem;
    }
    
    .form-label {
        display: block;
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .form-input {
        width: 100%;
        padding: 1rem;
        background: var(--bg-secondary);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-md);
        color: var(--text-primary);
        font-size: 1rem;
        font-family: 'Fira Code', monospace;
        transition: all 0.3s ease;
        box-sizing: border-box;
    }
    
    .form-input:focus {
        outline: none;
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(255, 97, 136, 0.1);
        background: var(--bg-primary);
    }
    
    .form-input::placeholder {
        color: var(--text-muted);
    }
    
    .login-button {
        width: 100%;
        padding: 1rem;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        border: none;
        border-radius: var(--radius-md);
        color: white;
        font-size: 1rem;
        font-weight: 700;
        font-family: 'Fira Code', monospace;
        text-transform: uppercase;
        letter-spacing: 1px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 97, 136, 0.3);
    }
    
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 97, 136, 0.4);
    }
    
    .login-button:active {
        transform: translateY(0);
    }
    
    .error-message {
        background: rgba(255, 97, 136, 0.1);
        border: 1px solid var(--primary-color);
        border-radius: var(--radius-md);
        padding: 1rem;
        margin-bottom: 1rem;
        color: var(--primary-color);
        text-align: center;
        font-weight: 600;
    }
    
    .login-footer {
        text-align: center;
        padding: 1.5rem;
        background: var(--bg-secondary);
        border-top: 1px solid var(--border-color);
    }
    
    .login-footer p {
        margin: 0;
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    
    /* Ocultar elementos de Streamlit */
    .stApp > header {display: none;}
    .stApp > .main .block-container {padding-top: 0; max-width: none;}
    .stSelectbox > div > div > div {background-color: var(--bg-secondary);}
    </style>
    """, unsafe_allow_html=True)
    
    # Contenedor principal del login
    st.markdown("""
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <div class="login-logo">🔐</div>
                <h1 class="login-title">Fusion CRM</h1>
                <p class="login-subtitle">Sistema de Gestión de Reclamos</p>
            </div>
            <div class="login-form">
    """, unsafe_allow_html=True)
    
    # Inicializar sesión de autenticación
    init_auth_session()
    
    # Formulario de login usando Streamlit
    with st.form("login_form"):
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">👤 Usuario</label>', unsafe_allow_html=True)
        username = st.text_input(
            "Username",
            placeholder="Ingresa tu nombre de usuario",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.markdown('<label class="form-label">🔒 Contraseña</label>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Ingresa tu contraseña",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón de login
        login_clicked = st.form_submit_button(
            "🚀 INICIAR SESIÓN",
            use_container_width=True
        )
    
    # Procesar login
    if login_clicked:
        if not username or not password:
            st.markdown("""
            <div class="error-message">
                ⚠️ Por favor, completa todos los campos
            </div>
            """, unsafe_allow_html=True)
        else:
            # Mostrar spinner de carga
            with st.spinner("Verificando credenciales..."):
                time.sleep(1)  # Simular tiempo de procesamiento
                
                user_info = verify_credentials(username, password, sheet_usuarios)
                
                if user_info:
                    st.session_state.auth['logged_in'] = True
                    st.session_state.auth['user_info'] = user_info
                    st.session_state.auth['login_attempts'] = 0
                    
                    st.markdown("""
                    <div class="error-message" style="background: rgba(166, 226, 46, 0.1); 
                                                   border-color: #A6E22E; 
                                                   color: #A6E22E;">
                        ✅ Bienvenido, iniciando sesión...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.auth['login_attempts'] += 1
                    attempts = st.session_state.auth['login_attempts']
                    
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Credenciales incorrectas ({attempts}/3 intentos)
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if attempts >= 3:
                        st.markdown("""
                        <div class="error-message">
                            🚫 Demasiados intentos fallidos. Contacta al administrador.
                        </div>
                        """, unsafe_allow_html=True)
    
    # Footer y cierre de contenedores
    st.markdown("""
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
                 key="logout_btn", help="Cerrar la sesión actual"):
        logout()
        st.rerun()