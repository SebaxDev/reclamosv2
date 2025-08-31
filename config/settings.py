"""
Configuración central de la aplicación - Fusion CRM
Versión 2.3 - Configuración optimizada para Monokai
"""

# ==================== CONSTANTES PRINCIPALES ====================

# --------------------------
# CONFIGURACIÓN DE GOOGLE SHEETS
# --------------------------
SHEET_ID = "13R_3Mdr25Jd-nGhK7CxdcbKkFWLc0LPdYrOLOY8sZJo"
WORKSHEET_RECLAMOS = "Reclamos"
WORKSHEET_CLIENTES = "Clientes" 
WORKSHEET_USUARIOS = "usuarios"
WORKSHEET_NOTIFICACIONES = "Notificaciones"

# IDENTIFICADORES ÚNICOS
COLUMNA_ID_RECLAMO = "ID Reclamo"  # Columna P en WORKSHEET_RECLAMOS
COLUMNA_ID_CLIENTE = "ID Cliente"   # Columna G en WORKSHEET_CLIENTES

# --------------------------
# ESTRUCTURAS DE DATOS - COLUMNAS
# --------------------------
COLUMNAS_RECLAMOS = [
    "Fecha y hora", "Nº Cliente", "Sector", "Nombre", 
    "Dirección", "Teléfono", "Tipo de reclamo", "Detalles", 
    "Estado", "Técnico", "N° de Precinto", "Atendido por", "Fecha_formateada", "ID Reclamo"
]

COLUMNAS_CLIENTES = [
    "Nº Cliente", "Sector", "Nombre", "Dirección", 
    "Teléfono", "N° de Precinto", "ID Cliente", "Última Modificación"
]

COLUMNAS_USUARIOS = [
    "username", "password", "nombre", "rol", "activo", "modo_oscuro"
]

COLUMNAS_NOTIFICACIONES = [
    "ID", "Tipo", "Prioridad", "Mensaje", 
    "Usuario_Destino", "ID_Reclamo", "Fecha_Hora", "Leída", "Acción"
]

# ==================== CONFIGURACIÓN DE DOMINIO ====================

# --------------------------
# OPCIONES DE SELECCIÓN
# --------------------------
SECTORES_DISPONIBLES = [str(n) for n in range(1, 18)]

TECNICOS_DISPONIBLES = [
    "Braian", "Conejo", "Juan", "Junior", "Maxi", 
    "Ramon", "Roque", "Viki", "Oficina", "Base"
]

TIPOS_RECLAMO = [
    "Conexion C+I", "Conexion Cable", "Conexion Internet", "Suma Internet",
    "Suma Cable", "Reconexion", "Reconexion C+I", "Reconexion Internet", "Reconexion Cable", 
    "Sin Señal Ambos", "Sin Señal Cable", "Sin Señal Internet", "Sintonia", "Interferencia", 
    "Traslado", "Extension", "Extension x2", "Extension x3", "Extension x4", "Cambio de Ficha",
    "Cambio de Equipo", "Reclamo", "Cambio de Plan", "Desconexion a Pedido"
]

# --------------------------
# MATERIALES Y EQUIPOS
# --------------------------
ROUTER_POR_SECTOR = {
    "1": "huawei", "2": "huawei", "3": "huawei", "4": "huawei", "5": "huawei",
    "6": "vsol", "7": "vsol", "8": "vsol", "9": "huawei", "10": "huawei",
    "11": "vsol", "12": "huawei", "13": "huawei", "14": "vsol", "15": "huawei",
    "16": "huawei", "17": "huawei"
}

MATERIALES_POR_RECLAMO = {
    "Conexion C+I": {"router_catv": 1, "conector": 2, "ficha_f": 2},
    "Conexion Cable": {"ficha_f": 2, "micro": 1},
    # ... (mantener todo igual aquí)
}

# ==================== SEGURIDAD Y PERMISOS ====================

# --------------------------
# ROLES Y PERMISOS
# --------------------------
PERMISOS_POR_ROL = {
    'admin': {
        'descripcion': 'Acceso completo a todas las funciones',
        'permisos': ['*']  # El asterisco significa todos los permisos
    },
    'oficina': {
        'descripcion': 'Personal administrativo/atención al cliente',
        'permisos': ['inicio', 'reclamos_cargados', 'gestion_clientes', 'imprimir_reclamos']
    }
}

OPCIONES_PERMISOS = {
    "Inicio": "inicio",
    "Reclamos cargados": "reclamos_cargados", 
    "Gestión de clientes": "gestion_clientes",
    "Imprimir reclamos": "imprimir_reclamos",
    "Seguimiento técnico": "seguimiento_tecnico",
    "Cierre de Reclamos": "cierre_reclamos"
}

# ==================== CONFIGURACIÓN TÉCNICA ====================

# --------------------------
# RENDIMIENTO
# --------------------------
API_DELAY = 2.0
BATCH_DELAY = 2.0  
SESSION_TIMEOUT = 1800  # 30 minutos

# --------------------------
# ESTILOS (ahora solo Monokai)
# --------------------------
COLOR_ADMIN = "#FF5733"
COLOR_OFICINA = "#338AFF"

# --------------------------
# MODO DEPURACIÓN
# --------------------------
DEBUG_MODE = False

# ==================== FUNCIONES DE UTILIDAD ====================

def obtener_permisos_por_rol(rol):
    """Devuelve los permisos asociados a un rol"""
    return PERMISOS_POR_ROL.get(rol, {}).get('permisos', [])

def rol_tiene_permiso(rol, permiso_requerido):
    """Verifica si un rol tiene un permiso específico"""
    if permiso_requerido == 'admin':
        return rol == 'admin'
    
    permisos = obtener_permisos_por_rol(rol)
    return '*' in permisos or permiso_requerido in permisos