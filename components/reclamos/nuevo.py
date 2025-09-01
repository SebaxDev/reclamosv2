# components/reclamos/nuevo.py
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.date_utils import ahora_argentina, format_fecha, parse_fecha
from utils.api_manager import api_manager
from utils.data_manager import batch_update_sheet
from config.settings import (
    SECTORES_DISPONIBLES,
    TIPOS_RECLAMO,
    DEBUG_MODE
)

# --- FUNCIONES HELPER NUEVAS ---
def _normalizar_datos(df_clientes, df_reclamos, nro_cliente):
    """Normaliza datos solo cuando es necesario"""
    if not nro_cliente:
        return df_clientes, df_reclamos
    
    df_clientes_normalizado = df_clientes.copy()
    df_reclamos_normalizado = df_reclamos.copy()
    
    df_clientes_normalizado["Nº Cliente"] = df_clientes_normalizado["Nº Cliente"].astype(str).str.strip()
    df_reclamos_normalizado["Nº Cliente"] = df_reclamos_normalizado["Nº Cliente"].astype(str).str.strip()
    
    return df_clientes_normalizado, df_reclamos_normalizado

def _validar_y_normalizar_sector(sector_input):
    """Valida y normaliza el sector ingresado"""
    try:
        sector_limpio = str(sector_input).strip()
        sector_num = int(sector_limpio)
        
        if 1 <= sector_num <= 17:
            return str(sector_num), None
        else:
            return None, f"⚠️ El sector debe estar entre 1 y 17. Se ingresó: {sector_num}"
            
    except ValueError:
        return None, f"⚠️ El sector debe ser un número válido. Se ingresó: {sector_input}"

def _verificar_reclamos_activos(nro_cliente, df_reclamos):
    """Verifica reclamos activos de forma eficiente"""
    if nro_cliente not in df_reclamos["Nº Cliente"].values:
        return pd.DataFrame()
    
    reclamos_cliente = df_reclamos[df_reclamos["Nº Cliente"] == nro_cliente]
    
    # Convertir estados a minúsculas para comparación case-insensitive
    estados_activos = ["pendiente", "en curso"]
    reclamos_activos = reclamos_cliente[
        reclamos_cliente["Estado"].str.strip().str.lower().isin(estados_activos) |
        (reclamos_cliente["Tipo de reclamo"].str.strip().str.lower() == "Desconexion a Pedido")
    ]
    
    return reclamos_activos

def generar_id_unico():
    """Genera un ID único para reclamos"""
    import uuid
    return str(uuid.uuid4())[:8].upper()

# --- FUNCIÓN PRINCIPAL OPTIMIZADA ---
def render_nuevo_reclamo(df_reclamos, df_clientes, sheet_reclamos, sheet_clientes, current_user=None):
    """
    Muestra la sección para cargar nuevos reclamos
    """
    st.subheader("📝 Cargar nuevo reclamo")

    estado = {
        'nro_cliente': '',
        'cliente_existente': None,
        'formulario_bloqueado': False,
        'reclamo_guardado': False,
        'cliente_nuevo': False
    }

    estado['nro_cliente'] = st.text_input(
        "🔢 N° de Cliente", 
        placeholder="Ingresa el número de cliente"
    ).strip()

    if estado['nro_cliente']:
        # Normalizar datos solo cuando sea necesario
        df_clientes_norm, df_reclamos_norm = _normalizar_datos(
            df_clientes, df_reclamos, estado['nro_cliente']
        )
        
        # Buscar cliente
        match = df_clientes_norm[df_clientes_norm["Nº Cliente"] == estado['nro_cliente']]
        
        if not match.empty:
            estado['cliente_existente'] = match.iloc[0].to_dict()
            st.success("✅ Cliente reconocido, datos auto-cargados.")

        else:
            estado['cliente_nuevo'] = True
            st.info("ℹ️ Este cliente no existe en la base y se cargará como cliente nuevo.")
        
        # Verificar reclamos activos
        reclamos_activos = _verificar_reclamos_activos(estado['nro_cliente'], df_reclamos_norm)
        
        if not reclamos_activos.empty:
            estado['formulario_bloqueado'] = True
            st.error("⚠️ Este cliente ya tiene un reclamo sin resolver o una desconexión activa.")
            
            # Mostrar reclamos activos
            for _, reclamo in reclamos_activos.iterrows():
                with st.expander(f"🔍 Reclamo activo - {format_fecha(reclamo['Fecha y hora'], '%d/%m/%Y %H:%M')}"):
                    st.markdown(f"**👤 Cliente:** {reclamo.get('Nombre', 'N/A')}")
                    st.markdown(f"**📌 Tipo:** {reclamo.get('Tipo de reclamo', 'N/A')}")
                    st.markdown(f"**📝 Detalles:** {reclamo.get('Detalles', 'N/A')[:200]}...")
                    st.markdown(f"**⚙️ Estado:** {reclamo.get('Estado', 'Sin estado')}")

    if estado['reclamo_guardado']:
        st.success("✅ Reclamo registrado correctamente.")
    elif not estado['formulario_bloqueado']:
        estado = _mostrar_formulario_reclamo(estado, df_clientes, sheet_reclamos, sheet_clientes, current_user)

    return estado

# --- FUNCIÓN DE FORMULARIO MEJORADA ---
def _mostrar_formulario_reclamo(estado, df_clientes, sheet_reclamos, sheet_clientes, current_user):
    """Muestra y procesa el formulario de nuevo reclamo"""
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    with st.form("reclamo_formulario", clear_on_submit=False):
        st.markdown("<h5>Datos del Cliente</h5>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        # Datos del cliente (existe o nuevo)
        if estado['cliente_existente']:
            cliente_data = estado['cliente_existente']
            
            with col1:
                nombre = st.text_input(
                    "👤 Nombre del Cliente",
                    value=cliente_data.get("Nombre", "")
                )
                direccion = st.text_input(
                    "📍 Dirección",
                    value=cliente_data.get("Dirección", "")
                )

            with col2:
                telefono = st.text_input(
                    "📞 Teléfono",
                    value=cliente_data.get("Teléfono", "")
                )
                
                # Sector con validación mejorada
                sector_existente = cliente_data.get("Sector", "1")
                sector_normalizado, error_sector = _validar_y_normalizar_sector(sector_existente)
                
                if error_sector:
                    st.warning(error_sector)
                    sector = st.text_input("🔢 Sector (1-17)", value="1")
                else:
                    sector = st.text_input("🔢 Sector (1-17)", value=sector_normalizado)

        else:
            with col1:
                nombre = st.text_input("👤 Nombre del Cliente", placeholder="Nombre completo")
                direccion = st.text_input("📍 Dirección", placeholder="Dirección completa")
            
            with col2:
                telefono = st.text_input("📞 Teléfono", placeholder="Número de contacto")
                sector = st.text_input("🔢 Sector (1-17)", placeholder="Ej: 5")

        # Campos del reclamo
        st.markdown("---")
        st.markdown("<h5>Detalles del Reclamo</h5>", unsafe_allow_html=True)
        tipo_reclamo = st.selectbox("📌 Tipo de Reclamo", TIPOS_RECLAMO)
        detalles = st.text_area("📝 Detalles del Reclamo", placeholder="Describe el problema...", height=100)

        col3, col4 = st.columns(2)
        with col3:
            precinto = st.text_input(
                "🔒 N° de Precinto (opcional)",
                value=estado['cliente_existente'].get("N° de Precinto", "") if estado['cliente_existente'] else "",
                placeholder="Número de precinto"
            )
        
        with col4:
            atendido_por = st.text_input(
                "👤 Atendido por", 
                placeholder="Nombre de quien atiende", 
                value=current_user or ""
            )

        enviado = st.form_submit_button("✅ Guardar Reclamo", use_container_width=True, type="primary")

    st.markdown('</div>', unsafe_allow_html=True)

    if enviado:
        estado = _procesar_envio_formulario(
            estado, nombre, direccion, telefono, sector, 
            tipo_reclamo, detalles, precinto, atendido_por,
            df_clientes, sheet_reclamos, sheet_clientes
        )
    
    return estado

# --- FUNCIÓN DE PROCESAMIENTO OPTIMIZADA ---
def _procesar_envio_formulario(estado, nombre, direccion, telefono, sector, tipo_reclamo, detalles, precinto, atendido_por, df_clientes, sheet_reclamos, sheet_clientes):
    """Procesa el envío del formulario de manera optimizada"""
    
    # Validar campos obligatorios
    campos_obligatorios = {
        "Nombre": nombre.strip(),
        "Dirección": direccion.strip(),
        "Sector": str(sector).strip(),
        "Tipo de reclamo": tipo_reclamo.strip(),
        "Atendido por": atendido_por.strip()
    }
    
    campos_vacios = [campo for campo, valor in campos_obligatorios.items() if not valor]
    
    if campos_vacios:
        st.error(f"⚠️ Campos obligatorios vacíos: {', '.join(campos_vacios)}")
        return estado

    # Validar y normalizar sector
    sector_normalizado, error_sector = _validar_y_normalizar_sector(sector)
    if error_sector:
        st.error(error_sector)
        return estado

    with st.spinner("Guardando reclamo..."):
        try:
            # Preparar datos del reclamo
            fecha_hora = ahora_argentina()
            
            # ✅ CAMBIO SOLICITADO: Estado "Desconexión" para desconexiones a pedido
            if tipo_reclamo.lower() == "desconexion a pedido":
                estado_reclamo = "Desconexión"
            else:
                estado_reclamo = "Pendiente"
                
            id_reclamo = generar_id_unico()

            fila_reclamo = [
                format_fecha(fecha_hora),
                estado['nro_cliente'],
                sector_normalizado,
                nombre.upper(),
                direccion.upper(),
                telefono.strip(),
                tipo_reclamo,
                detalles.upper(),
                estado_reclamo,  # ✅ Usa el estado correcto
                "",  # Técnico (vacío inicialmente)
                precinto.strip(),
                atendido_por.upper(),
                "", "", "",  # Campos adicionales
                id_reclamo
            ]

            # Guardar reclamo
            success, error = api_manager.safe_sheet_operation(
                sheet_reclamos.append_row,
                fila_reclamo
            )

            if success:
                estado.update({
                    'reclamo_guardado': True,
                    'formulario_bloqueado': True
                })
                
                st.success(f"✅ Reclamo guardado - ID: {id_reclamo}")
                
                # Gestionar cliente (nuevo o actualización)
                _gestionar_cliente(
                    estado['nro_cliente'], sector_normalizado, nombre, 
                    direccion, telefono, precinto, df_clientes, sheet_clientes
                )
                
                # Notificación
                if 'notification_manager' in st.session_state:
                    st.session_state.notification_manager.add(
                        notification_type="nuevo_reclamo",
                        message=f"📝 Nuevo reclamo {id_reclamo} - {tipo_reclamo}",
                        user_target="all",
                        claim_id=id_reclamo
                    )
                
                st.cache_data.clear()

                # 🔄 Forzar recarga para limpiar el formulario y mostrar reclamo activo
                st.rerun()
                
            else:
                st.error(f"❌ Error al guardar: {error}")

        except Exception as e:
            st.error(f"❌ Error inesperado: {str(e)}")
            if DEBUG_MODE:
                st.exception(e)
    
    return estado

def _gestionar_cliente(nro_cliente, sector, nombre, direccion, telefono, precinto, df_clientes, sheet_clientes):
    """Gestiona la creación o actualización del cliente"""
    cliente_existente = df_clientes[df_clientes["Nº Cliente"] == nro_cliente]
    
    if cliente_existente.empty:
        # Crear nuevo cliente
        fila_cliente = [nro_cliente, sector, nombre.upper(), direccion.upper(), telefono.strip(), precinto.strip()]
        success, _ = api_manager.safe_sheet_operation(sheet_clientes.append_row, fila_cliente)
        if success:
            st.info("ℹ️ Nuevo cliente registrado")
    else:
        # Actualizar cliente existente
        updates = []
        idx = cliente_existente.index[0] + 2
        
        campos_actualizar = {
            "B": ("Sector", sector),
            "C": ("Nombre", nombre.upper()),
            "D": ("Dirección", direccion.upper()),
            "E": ("Teléfono", telefono.strip()),
            "F": ("N° de Precinto", precinto.strip())
        }
        
        for col, (campo, nuevo_valor) in campos_actualizar.items():
            valor_actual = str(cliente_existente.iloc[0][campo]).strip() if campo in cliente_existente.columns else ""
            if valor_actual != nuevo_valor:
                updates.append({"range": f"{col}{idx}", "values": [[nuevo_valor]]})
        
        if updates:
            success, _ = api_manager.safe_sheet_operation(
                batch_update_sheet, sheet_clientes, updates, is_batch=True
            )
            if success:
                st.info("🔁 Datos del cliente actualizados")