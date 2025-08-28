# components/admin/__init__.py - AGREGAR NUEVO IMPORT

from .panel import render_panel_administracion
from .usuarios import render_gestion_usuarios_completa
from .config_sistema import render_configuracion_sistema
from .logs import render_logs_actividad, registrar_log

__all__ = [
    'render_panel_administracion', 
    'render_gestion_usuarios_completa',
    'render_configuracion_sistema',
    'render_logs_actividad',
    'registrar_log'
]