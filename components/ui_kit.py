# components/ui_kit.py - KIT DE COMPONENTES UI UNIFICADOS
"""Componentes UI reutilizables con el sistema de diseño unificado"""

import streamlit as st

def crm_card(title, content, icon=None, actions=None, variant="default"):
    """Tarjeta CRM moderna"""
    
    variant_classes = {
        "default": "crm-card",
        "primary": "crm-card border-l-4 border-primary-500",
        "success": "crm-card border-l-4 border-success-500", 
        "warning": "crm-card border-l-4 border-warning-500",
        "danger": "crm-card border-l-4 border-danger-500"
    }
    
    return f"""
    <div class="{variant_classes[variant]}">
        <div class="crm-card-header">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    {f'<span class="text-2xl text-primary-500">{icon}</span>' if icon else ''}
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
                </div>
            </div>
        </div>
        <div class="text-gray-700 dark:text-gray-300">
            {content}
        </div>
        {f'<div class="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">{actions}</div>' if actions else ''}
    </div>
    """

def crm_metric(value, label, icon="📊", trend=None, variant="primary"):
    """Métrica CRM profesional"""
    
    variant_config = {
        "primary": "bg-gradient-to-r from-primary-500 to-primary-600",
        "success": "bg-gradient-to-r from-success-500 to-success-600",
        "warning": "bg-gradient-to-r from-warning-500 to-warning-600",
        "danger": "bg-gradient-to-r from-danger-500 to-danger-600",
        "neutral": "bg-gradient-to-r from-gray-100 to-gray-200"
    }
    
    trend_html = ""
    if trend:
        trend_color = "text-green-200" if trend.get('positive', True) else "text-red-200"
        trend_icon = "↗" if trend.get('positive', True) else "↘"
        trend_html = f"""
        <div class="flex items-center {trend_color} text-sm mt-1">
            <span class="mr-1">{trend_icon}</span>
            <span>{trend['value']}</span>
        </div>
        """
    
    return f"""
    <div class="{variant_config[variant]} text-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300">
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm opacity-90 font-medium">{label}</p>
                <p class="text-2xl font-bold mt-1">{value}</p>
                {trend_html}
            </div>
            <div class="bg-white/20 rounded-full p-3">
                <span class="text-xl">{icon}</span>
            </div>
        </div>
    </div>
    """

def crm_badge(text, type="primary", icon=None):
    """Badge CRM moderno"""
    
    color_classes = {
        "primary": "crm-badge crm-badge-primary",
        "success": "crm-badge crm-badge-success",
        "warning": "crm-badge crm-badge-warning",
        "danger": "crm-badge crm-badge-danger",
        "neutral": "bg-gray-100 text-gray-800"
    }
    
    icon_html = f'<span class="mr-1">{icon}</span>' if icon else ""
    
    return f"""
    <span class="{color_classes[type]}">
        {icon_html}{text}
    </span>
    """

def crm_loading(message="Cargando..."):
    """Loading state CRM"""
    return f"""
    <div class="flex flex-col items-center justify-center py-8">
        <div class="crm-loading"></div>
        <p class="mt-3 text-gray-600 dark:text-gray-400 text-sm">{message}</p>
    </div>
    """

def crm_alert(message, type="info", title=None):
    """Alerta CRM moderna"""
    
    config = {
        "info": {"color": "blue", "icon": "ℹ️", "bg": "bg-blue-50", "border": "border-blue-200", "text": "text-blue-800"},
        "success": {"color": "green", "icon": "✅", "bg": "bg-green-50", "border": "border-green-200", "text": "text-green-800"},
        "warning": {"color": "yellow", "icon": "⚠️", "bg": "bg-yellow-50", "border": "border-yellow-200", "text": "text-yellow-800"},
        "error": {"color": "red", "icon": "❌", "bg": "bg-red-50", "border": "border-red-200", "text": "text-red-800"}
    }
    
    conf = config[type]
    
    return f"""
    <div class="{conf['bg']} border-l-4 border-{conf['color']}-500 p-4 rounded-lg mb-4">
        <div class="flex items-start">
            <span class="text-{conf['color']}-600 text-lg mr-3">{conf['icon']}</span>
            <div>
                {f'<h4 class="text-{conf['color']}-800 font-semibold mb-1">{title}</h4>' if title else ''}
                <p class="text-{conf['color']}-700 text-sm">{message}</p>
            </div>
        </div>
    </div>
    """