"""
Configuración central de la aplicación
Versión 2.0 - Con gestión de usuarios y permisos
"""

# --------------------------
# CONFIGURACIÓN DE GOOGLE SHEETS
# --------------------------
SHEET_ID = "13R_3Mdr25Jd-nGhK7CxdcbKkFWLc0LPdYrOLOY8sZJo"
WORKSHEET_RECLAMOS = "Reclamos"
WORKSHEET_CLIENTES = "Clientes"
WORKSHEET_USUARIOS = "usuarios"

# --------------------------
# ESTRUCTURAS DE DATOS
# --------------------------
COLUMNAS_RECLAMOS = [
    "Fecha y hora", "Nº Cliente", "Sector", "Nombre", 
    "Dirección", "Teléfono", "Tipo de reclamo", 
    "Detalles", "Estado", "Técnico", "N° de Precinto", "Atendido por"
]

COLUMNAS_CLIENTES = [
    "Nº Cliente", "Sector", "Nombre", "Dirección", 
    "Teléfono", "N° de Precinto"
]

COLUMNAS_USUARIOS = [  # Nueva estructura para usuarios
    "username", "password", "nombre", "rol", "activo"
]

# --------------------------
# ROLES Y PERMISOS
# --------------------------
# Definición de permisos por rol
PERMISOS_POR_ROL = {
    'admin': {
        'descripcion': 'Acceso completo a todas las funciones',
        'permisos': ['*']  # El asterisco significa todos los permisos
    },
    'oficina': {
        'descripcion': 'Personal administrativo/atención al cliente',
        'permisos': [
            'inicio', 
            'reclamos_cargados', 
            'gestion_clientes',
            'imprimir_reclamos'
        ]
    }
}

# Mapeo de opciones de navegación a permisos
OPCIONES_PERMISOS = {
    "Inicio": "inicio",
    "Reclamos cargados": "reclamos_cargados",
    "Gestión de clientes": "gestion_clientes",
    "Imprimir reclamos": "imprimir_reclamos",
    "Seguimiento técnico": "seguimiento_tecnico",
    "Cierre de Reclamos": "cierre_reclamos"
}

# --------------------------
# CONFIGURACIÓN DE LA APLICACIÓN
# --------------------------
TECNICOS_DISPONIBLES = [
    "Braian", "Conejo", "Juan", "Junior", "Maxi", 
    "Ramon", "Roque", "Viki", "Oficina", "Base"
]

TIPOS_RECLAMO = [
    "Conexion C+I", "Conexion Cable", "Conexion Internet", "Suma Internet",
    "Suma Cable", "Reconexion", "Reconexion C+I", "Reconexion Internet", "Reconexion Cable", "Sin Señal Ambos", "Sin Señal Cable",
    "Sin Señal Internet", "Sintonia", "Interferencia", "Traslado",
    "Extension", "Extension x2", "Extension x3", "Extension x4", "Cambio de Ficha",
    "Cambio de Equipo", "Reclamo", "Cambio de Plan", "Desconexion a Pedido"
]

# --------------------------
# MATERIALES Y EQUIPOS POR RECLAMO Y SECTOR
# --------------------------

# Marca de router recomendada por sector (predeterminado)
ROUTER_POR_SECTOR = {
    "1": "huawei",
    "2": "huawei",
    "3": "huawei",
    "4": "huawei",
    "5": "huawei",
    "6": "vsol",
    "7": "vsol",
    "8": "vsol",
    "9": "huawei",
    "10": "huawei",
    "11": "vsol",
    "12": "huawei",
    "13": "huawei",
    "14": "vsol",
    "15": "huawei",
    "16": "huawei",
    "17": "huawei"
}

# Materiales mínimos requeridos por tipo de reclamo
MATERIALES_POR_RECLAMO = {
    "Conexion C+I": {"router_catv": 1, "conector": 2, "ficha_f": 2},
    "Conexion Cable": {"ficha_f": 2, "micro": 1},
    "Conexion Internet": {"router_internet": 1, "conector": 2},
    "Suma Internet": {"router_catv": 1, "conector": 2, "ficha_f": 2},
    "Suma Cable": {"router_catv": 1, "ficha_f": 2},
    "Reconexion": {},
    "Reconexion C+I": {"router_catv": 1, "conector": 2},
    "Reconexion Internet": {"router_internet": 1, "conector": 2},
    "Reconexion Cable": {"ficha_f": 2, "micro": 1},
    "Sin Señal Ambos": {"conector": 1},
    "Sin Señal Cable": {"ficha_f": 2, "micro": 1},
    "Sin Señal Internet": {"conector": 1},
    "Sintonia": {},
    "Interferencia": {"ficha_f": 2},
    "Traslado": {"conector": 2, "ficha_f": 2},
    "Extension": {},
    "Extension x2": {"derivador_x2": 1, "ficha_f": 4},
    "Extension x3": {"derivador_x3": 1, "ficha_f": 4},
    "Extension x4": {"derivador_x4": 1, "ficha_f": 8},
    "Cambio de Ficha": {"conector": 1, "ficha_f": 1, "micro": 1},
    "Cambio de Equipo": {"router": 1},
    "Reclamo": {},
    "Cambio de Plan": {},
    "Desconexion a Pedido": {}
}

# --------------------------
# SEGURIDAD Y API
# --------------------------
API_DELAY = 2.0  # Segundos entre llamadas a la API
BATCH_DELAY = 2.0  # Segundos entre operaciones batch
SESSION_TIMEOUT = 1800  # 30 minutos de inactividad para cerrar sesión

# --------------------------
# FUNCIONES DE UTILIDAD
# --------------------------
def obtener_permisos_por_rol(rol):
    """Devuelve los permisos asociados a un rol"""
    return PERMISOS_POR_ROL.get(rol, {}).get('permisos', [])

def rol_tiene_permiso(rol, permiso_requerido):
    """Verifica si un rol tiene un permiso específico"""
    if permiso_requerido == 'admin':
        return rol == 'admin'  # Solo los admin pueden gestionar otros admin
    
    permisos = obtener_permisos_por_rol(rol)
    return '*' in permisos or permiso_requerido in permisos

# --------------------------
# CONFIGURACIÓN DE ESTILOS
# --------------------------
COLOR_ADMIN = "#FF5733"  # Naranja
COLOR_OFICINA = "#338AFF"  # Azul

# --------------------------
# MODO DEPURACIÓN
# --------------------------
# Modo de depuración (True/False)
DEBUG_MODE = False  # Cambiar a True si necesitas ver mensajes de depuración