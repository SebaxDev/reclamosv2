"""Componentes de UI reutilizables con TailwindCSS - Versión CRM Profesional"""

import streamlit as st
from datetime import datetime

def card(title, content, icon=None, actions=None, variant="default"):
    """Componente de tarjeta elegante con TailwindCSS"""
    
    variant_classes = {
        "default": "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700",
        "primary": "bg-gradient-to-r from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 border border-primary-200 dark:border-primary-700",
        "success": "bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-700",
        "warning": "bg-gradient-to-r from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border border-yellow-200 dark:border-yellow-700",
        "danger": "bg-gradient-to-r from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border border-red-200 dark:border-red-700"
    }
    
    return f"""
    <div class="{variant_classes[variant]} rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow duration-200 mb-4">
        <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
                {f'<span class="text-2xl text-primary-500">{icon}</span>' if icon else ''}
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
            </div>
        </div>
        <div class="text-gray-700 dark:text-gray-300">
            {content}
        </div>
        {f'<div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">{actions}</div>' if actions else ''}
    </div>
    """

def metric_card(value, label, icon="📊", trend=None, subtitle=None, variant="primary"):
    """Tarjeta de métrica elegante con TailwindCSS"""
    
    variant_config = {
        "primary": {"bg": "bg-primary-500", "text": "text-white", "icon_bg": "bg-primary-600"},
        "success": {"bg": "bg-green-500", "text": "text-white", "icon_bg": "bg-green-600"},
        "warning": {"bg": "bg-yellow-500", "text": "text-gray-900", "icon_bg": "bg-yellow-600"},
        "danger": {"bg": "bg-red-500", "text": "text-white", "icon_bg": "bg-red-600"},
        "neutral": {"bg": "bg-gray-100", "text": "text-gray-900", "icon_bg": "bg-gray-200"}
    }
    
    config = variant_config[variant]
    
    trend_html = ""
    if trend:
        trend_color = "text-green-300" if trend.get('positive', True) else "text-red-300"
        trend_icon = "↗" if trend.get('positive', True) else "↘"
        trend_html = f"""
        <div class="flex items-center {trend_color} text-sm mt-1">
            <span class="mr-1">{trend_icon}</span>
            <span>{trend['value']}</span>
        </div>
        """
    
    subtitle_html = f'<p class="text-gray-300 text-sm mt-1">{subtitle}</p>' if subtitle else ""
    
    return f"""
    <div class="{config['bg']} {config['text']} rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
        <div class="flex items-center justify-between mb-4">
            <div>
                <p class="text-sm opacity-90">{label}</p>
                <p class="text-3xl font-bold mt-1">{value}</p>
                {trend_html}
                {subtitle_html}
            </div>
            <div class="{config['icon_bg']} rounded-lg p-3">
                <span class="text-2xl">{icon}</span>
            </div>
        </div>
    </div>
    """

def badge(text, type="primary", icon=None, size="md"):
    """Badge elegante con TailwindCSS"""
    
    color_classes = {
        "primary": "bg-primary-100 text-primary-800 dark:bg-primary-900/30 dark:text-primary-300",
        "success": "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
        "warning": "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
        "danger": "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
        "info": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
        "neutral": "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300"
    }
    
    size_classes = {
        "sm": "px-2 py-1 text-xs",
        "md": "px-3 py-1 text-sm",
        "lg": "px-4 py-2 text-base"
    }
    
    icon_html = f'<span class="mr-1">{icon}</span>' if icon else ""
    
    return f"""
    <span class="inline-flex items-center rounded-full font-medium {color_classes[type]} {size_classes[size]}">
        {icon_html}{text}
    </span>
    """

def breadcrumb(current_page, items=None, show_date=True):
    """Breadcrumb moderno con TailwindCSS"""
    
    icons = {
        "Inicio": "🏠",
        "Reclamos cargados": "📊", 
        "Gestión de clientes": "👥",
        "Imprimir reclamos": "🖨️",
        "Seguimiento técnico": "🔧",
        "Cierre de Reclamos": "✅"
    }
    
    breadcrumb_items = ""
    if items:
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            breadcrumb_items += f"""
            <span class="flex items-center">
                <span class="mx-2 text-gray-400">/</span>
                {'<span class="text-gray-900 dark:text-white font-medium">' if is_last else '<a href="#" class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">'}
                {item}
                {'</span>' if is_last else '</a>'}
            </span>
            """
    
    date_section = f"""
    <div class="flex-1"></div>
    <span class="text-sm text-gray-500 dark:text-gray-400">
        {datetime.now().strftime('%d/%m/%Y %H:%M')}
    </span>
    """ if show_date else ""
    
    return f"""
    <div class="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg px-6 py-4 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <div class="flex items-center space-x-2">
            <span class="text-xl text-primary-600">{icons.get(current_page, '📋')}</span>
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{current_page}</h2>
            {breadcrumb_items}
        </div>
        {date_section}
    </div>
    """

def loading_spinner(message="Cargando...", size="md"):
    """Spinner de carga elegante"""
    
    size_classes = {
        "sm": "w-4 h-4",
        "md": "w-8 h-8", 
        "lg": "w-12 h-12"
    }
    
    return f"""
    <div class="flex flex-col items-center justify-center py-8">
        <div class="animate-spin rounded-full {size_classes[size]} border-b-2 border-primary-500"></div>
        <p class="mt-3 text-gray-600 dark:text-gray-400 text-sm">{message}</p>
    </div>
    """

def alert(message, type="info", title=None):
    """Alerta moderna"""
    
    config = {
        "info": {"color": "blue", "icon": "ℹ️"},
        "success": {"color": "green", "icon": "✅"},
        "warning": {"color": "yellow", "icon": "⚠️"},
        "error": {"color": "red", "icon": "❌"}
    }
    
    conf = config[type]
    
    return f"""
    <div class="bg-{conf['color']}-50 border-l-4 border-{conf['color']}-500 p-4 rounded-lg mb-4">
        <div class="flex items-start">
            <span class="text-{conf['color']}-600 text-lg mr-3">{conf['icon']}</span>
            <div>
                {f'<h4 class="text-{conf['color']}-800 font-semibold mb-1">{title}</h4>' if title else ''}
                <p class="text-{conf['color']}-700 text-sm">{message}</p>
            </div>
        </div>
    </div>
    """