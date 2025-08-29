# utils/permissions.py - ASEGURARSE QUE TENGA:

from config.settings import PERMISOS_POR_ROL

def has_permission(permiso_requerido):
    """Verifica si el usuario actual tiene un permiso específico"""
    # Verificar si auth existe en session_state
    if 'auth' not in st.session_state:
        return False
        
    user_info = st.session_state.auth.get('user_info', {})
    rol = user_info.get('rol', '')
    
    if not rol:
        return False
    
    # Si es admin, tiene todos los permisos
    if rol == 'admin':
        return True
    
    permisos = PERMISOS_POR_ROL.get(rol, {}).get('permisos', [])
    
    # Verificar si tiene el permiso específico o todos los permisos (*)
    return '*' in permisos or permiso_requerido in permisos