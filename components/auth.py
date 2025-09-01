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
    # ... (dejé tu código CSS y formulario igual que antes)
    # 👇 tu mismo contenido intacto
    # ...
    
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

def auth_has_permission(required_permission):  # 👈 renombrada para coincidir con app.py
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
                 key="logout_btn", help="Cerrar la sesión actual"):  # 👈 corregido, sin duplicar argumento
        logout()
        st.rerun()
