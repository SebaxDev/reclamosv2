# components/admin/usuarios.py

import streamlit as st
import pandas as pd
from utils.api_manager import api_manager
from utils.permissions import has_permission

def render_gestion_usuarios_completa(df_usuarios, sheet_usuarios, user_info):
    """
    Versión completa de gestión de usuarios con pestañas
    """
    if not has_permission('admin'):
        st.warning("⚠️ No tienes permisos para acceder a esta sección")
        return {'needs_refresh': False}
    
    st.markdown("""
    <div class="bg-white dark:bg-gray-800 rounded-xl p-4 mb-6 border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">👥 Gestión Completa de Usuarios</h3>
    """, unsafe_allow_html=True)
    
    # Pestañas para diferentes acciones
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Usuarios", "➕ Nuevo Usuario", "⚙️ Editar Usuario"])
    
    with tab1:
        _mostrar_lista_usuarios(df_usuarios, sheet_usuarios)
    
    with tab2:
        _formulario_nuevo_usuario(sheet_usuarios)
    
    with tab3:
        _formulario_editar_usuario(df_usuarios, sheet_usuarios)
    
    st.markdown('</div>', unsafe_allow_html=True)
    return {'needs_refresh': st.session_state.get('usuarios_need_refresh', False)}

def _mostrar_lista_usuarios(df_usuarios, sheet_usuarios):
    """Muestra la lista de usuarios con opciones de gestión"""
    
    # Filtros de búsqueda
    col1, col2 = st.columns(2)
    with col1:
        filtro_rol = st.selectbox("Filtrar por rol", ["Todos", "admin", "oficina"])
    with col2:
        filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "Activos", "Inactivos"])
    
    # Aplicar filtros
    df_filtrado = df_usuarios.copy()
    if filtro_rol != "Todos":
        df_filtrado = df_filtrado[df_filtrado['rol'] == filtro_rol]
    if filtro_estado != "Todos":
        activo = filtro_estado == "Activos"
        df_filtrado = df_filtrado[df_filtrado['activo'] == activo]
    
    # Mostrar tabla
    st.dataframe(
        df_filtrado[['username', 'nombre', 'email', 'rol', 'activo', 'modo_oscuro']],
        use_container_width=True,
        column_config={
            "username": "Usuario",
            "nombre": "Nombre Completo",
            "email": "Email",
            "rol": st.column_config.SelectboxColumn("Rol", options=["admin", "oficina"]),
            "activo": "Activo",
            "modo_oscuro": "Modo Oscuro"
        }
    )
    
    # Estadísticas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total usuarios", len(df_usuarios))
    with col2:
        st.metric("Administradores", len(df_usuarios[df_usuarios['rol'] == 'admin']))
    with col3:
        st.metric("Activos", len(df_usuarios[df_usuarios['activo'] == True]))

def _formulario_nuevo_usuario(sheet_usuarios):
    """Formulario para crear nuevo usuario"""
    
    with st.form("form_nuevo_usuario_completo", clear_on_submit=True):
        st.markdown("### 📝 Crear Nuevo Usuario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Usuario*", help="Nombre de usuario para login", key="new_user")
            nombre = st.text_input("Nombre Completo*", key="new_nombre")
            email = st.text_input("Email*", key="new_email")
        
        with col2:
            rol = st.selectbox("Rol*", options=["admin", "oficina"], key="new_rol")
            password = st.text_input("Contraseña*", type="password", key="new_password")
            activo = st.checkbox("Usuario Activo", value=True, key="new_activo")
            modo_oscuro = st.checkbox("Modo Oscuro predeterminado", value=False, key="new_modo_oscuro")
        
        if st.form_submit_button("💾 Crear Usuario", use_container_width=True):
            if all([username, nombre, email, password]):
                if _crear_usuario(sheet_usuarios, username, password, nombre, email, rol, activo, modo_oscuro):
                    st.success("✅ Usuario creado correctamente")
                    st.session_state.usuarios_need_refresh = True
            else:
                st.error("❌ Todos los campos marcados con * son obligatorios")

def _formulario_editar_usuario(df_usuarios, sheet_usuarios):
    """Formulario para editar usuario existente"""
    
    usuarios_disponibles = df_usuarios['username'].tolist()
    usuario_seleccionado = st.selectbox(
        "Seleccionar usuario para editar",
        options=usuarios_disponibles,
        key="select_usuario_editar"
    )
    
    if usuario_seleccionado:
        usuario_data = df_usuarios[df_usuarios['username'] == usuario_seleccionado].iloc[0]
        
        with st.form(f"form_editar_{usuario_seleccionado}"):
            st.markdown(f"### ✏️ Editando usuario: {usuario_seleccionado}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_nombre = st.text_input("Nombre Completo*", value=usuario_data['nombre'], key="edit_nombre")
                nuevo_email = st.text_input("Email*", value=usuario_data.get('email', ''), key="edit_email")
            
            with col2:
                nuevo_rol = st.selectbox(
                    "Rol*", 
                    options=["admin", "oficina"],
                    index=0 if usuario_data['rol'] == 'admin' else 1,
                    key="edit_rol"
                )
                nuevo_activo = st.checkbox("Usuario Activo", value=usuario_data['activo'], key="edit_activo")
                nuevo_modo_oscuro = st.checkbox("Modo Oscuro", value=usuario_data.get('modo_oscuro', False), key="edit_modo_oscuro")
            
            nueva_password = st.text_input("Nueva Contraseña (dejar vacío para mantener actual)", type="password", key="edit_password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                    if _actualizar_usuario(sheet_usuarios, usuario_data, nuevo_nombre, nuevo_email, nuevo_rol, nuevo_activo, nuevo_modo_oscuro, nueva_password):
                        st.success("✅ Usuario actualizado correctamente")
                        st.session_state.usuarios_need_refresh = True
            
            with col2:
                if st.form_submit_button("🗑️ Desactivar Usuario", use_container_width=True, type="secondary"):
                    if _desactivar_usuario(sheet_usuarios, usuario_data):
                        st.success("✅ Usuario desactivado correctamente")
                        st.session_state.usuarios_need_refresh = True

def _crear_usuario(sheet_usuarios, username, password, nombre, email, rol, activo, modo_oscuro):
    """Crea un nuevo usuario en el sistema"""
    try:
        # Verificar si el usuario ya existe
        datos_actuales = sheet_usuarios.get_all_values()
        usuarios_existentes = [fila[0] for fila in datos_actuales[1:] if len(fila) > 0]
        
        if username in usuarios_existentes:
            st.error("❌ El usuario ya existe")
            return False
        
        # Agregar nuevo usuario
        nueva_fila = [
            username, 
            password, 
            nombre, 
            rol, 
            str(activo), 
            str(modo_oscuro), 
            email
        ]
        sheet_usuarios.append_row(nueva_fila)
        
        # Registrar en logs
        if 'notification_manager' in st.session_state:
            usuario_actual = st.session_state.auth.get('user_info', {}).get('username', 'Sistema')
            mensaje = f"Usuario {username} creado por {usuario_actual}"
            st.session_state.notification_manager.add(
                notification_type="user_created",
                message=mensaje,
                user_target="admin"
            )
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error al crear usuario: {str(e)}")
        return False

def _actualizar_usuario(sheet_usuarios, usuario_data, nombre, email, rol, activo, modo_oscuro, password):
    """Actualiza un usuario existente"""
    try:
        # Encontrar la fila del usuario
        datos_actuales = sheet_usuarios.get_all_values()
        fila_index = None
        
        for i, fila in enumerate(datos_actuales[1:], start=2):  # Saltar encabezado
            if len(fila) > 0 and fila[0] == usuario_data['username']:
                fila_index = i
                break
        
        if not fila_index:
            st.error("❌ Usuario no encontrado")
            return False
        
        # Preparar actualizaciones
        updates = [
            {"range": f"C{fila_index}", "values": [[nombre]]},
            {"range": f"D{fila_index}", "values": [[rol]]},
            {"range": f"E{fila_index}", "values": [[str(activo)]]},
            {"range": f"F{fila_index}", "values": [[str(modo_oscuro)]]},
            {"range": f"G{fila_index}", "values": [[email]]}
        ]
        
        if password:  # Solo actualizar password si se proporcionó una nueva
            updates.append({"range": f"B{fila_index}", "values": [[password]]})
        
        # Ejecutar actualizaciones
        success, error = api_manager.safe_sheet_operation(
            lambda: sheet_usuarios.batch_update([{
                'range': update['range'],
                'values': update['values']
            } for update in updates])
        )
        
        if success:
            # Registrar en logs
            if 'notification_manager' in st.session_state:
                usuario_actual = st.session_state.auth.get('user_info', {}).get('username', 'Sistema')
                mensaje = f"Usuario {usuario_data['username']} actualizado por {usuario_actual}"
                st.session_state.notification_manager.add(
                    notification_type="user_updated",
                    message=mensaje,
                    user_target="admin"
                )
            return True
        else:
            st.error(f"❌ Error al actualizar usuario: {error}")
            return False
            
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        return False

def _desactivar_usuario(sheet_usuarios, usuario_data):
    """Desactiva un usuario en lugar de eliminarlo"""
    try:
        # Encontrar la fila del usuario
        datos_actuales = sheet_usuarios.get_all_values()
        fila_index = None
        
        for i, fila in enumerate(datos_actuales[1:], start=2):
            if len(fila) > 0 and fila[0] == usuario_data['username']:
                fila_index = i
                break
        
        if not fila_index:
            st.error("❌ Usuario no encontrado")
            return False
        
        # Desactivar usuario
        success, error = api_manager.safe_sheet_operation(
            lambda: sheet_usuarios.update_cell(fila_index, 5, "False")  # Columna E (activo)
        )
        
        if success:
            # Registrar en logs
            if 'notification_manager' in st.session_state:
                usuario_actual = st.session_state.auth.get('user_info', {}).get('username', 'Sistema')
                mensaje = f"Usuario {usuario_data['username']} desactivado por {usuario_actual}"
                st.session_state.notification_manager.add(
                    notification_type="user_deactivated",
                    message=mensaje,
                    user_target="admin"
                )
            return True
        else:
            st.error(f"❌ Error al desactivar usuario: {error}")
            return False
            
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        return False