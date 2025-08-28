# styles.py - SISTEMA DE DISEÑO UNIFICADO CRM PROFESIONAL
"""Estilos CSS profesionales tipo CRM con diseño expandido y TailwindCSS"""

def get_main_styles_v3(dark_mode=True):
    """Sistema de diseño unificado CRM profesional con TailwindCSS"""
    
    # PALETA DE COLORES CORPORATIVA CRM
    if dark_mode:
        theme_vars = """
            --color-primary-50: #f0f9ff;
            --color-primary-100: #e0f2fe;
            --color-primary-200: #bae6fd;
            --color-primary-300: #7dd3fc;
            --color-primary-400: #38bdf8;
            --color-primary-500: #0ea5e9;
            --color-primary-600: #0284c7;
            --color-primary-700: #0369a1;
            --color-primary-800: #075985;
            --color-primary-900: #0c4a6e;
            
            --color-success-50: #f0fdf4;
            --color-success-100: #dcfce7;
            --color-success-200: #bbf7d0;
            --color-success-300: #86efac;
            --color-success-400: #4ade80;
            --color-success-500: #22c55e;
            --color-success-600: #16a34a;
            --color-success-700: #15803d;
            --color-success-800: #166534;
            --color-success-900: #14532d;
            
            --color-warning-50: #fffbeb;
            --color-warning-100: #fef3c7;
            --color-warning-200: #fde68a;
            --color-warning-300: #fcd34d;
            --color-warning-400: #fbbf24;
            --color-warning-500: #f59e0b;
            --color-warning-600: #d97706;
            --color-warning-700: #b45309;
            --color-warning-800: #92400e;
            --color-warning-900: #78350f;
            
            --color-danger-50: #fef2f2;
            --color-danger-100: #fee2e2;
            --color-danger-200: #fecaca;
            --color-danger-300: #fca5a5;
            --color-danger-400: #f87171;
            --color-danger-500: #ef4444;
            --color-danger-600: #dc2626;
            --color-danger-700: #b91c1c;
            --color-danger-800: #991b1b;
            --color-danger-900: #7f1d1d;
            
            --color-gray-50: #f9fafb;
            --color-gray-100: #f3f4f6;
            --color-gray-200: #e5e7eb;
            --color-gray-300: #d1d5db;
            --color-gray-400: #9ca3af;
            --color-gray-500: #6b7280;
            --color-gray-600: #4b5563;
            --color-gray-700: #374151;
            --color-gray-800: #1f2937;
            --color-gray-900: #111827;
            
            /* Modo oscuro - CRM Professional Dark */
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-surface: #334155;
            --bg-card: #1e293b;
            --bg-hover: #334155;
            
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #64748b;
            --text-inverse: #0f172a;
            
            --border-color: #334155;
            --border-light: #475569;
            --border-focus: #60a5fa;
            
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.4), 0 2px 4px -1px rgba(0,0,0,0.3);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.5), 0 4px 6px -2px rgba(0,0,0,0.4);
            --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.6), 0 10px 10px -5px rgba(0,0,0,0.5);
        """
    else:
        theme_vars = """
            --color-primary-50: #f0f9ff;
            --color-primary-100: #e0f2fe;
            --color-primary-200: #bae6fd;
            --color-primary-300: #7dd3fc;
            --color-primary-400: #38bdf8;
            --color-primary-500: #0ea5e9;
            --color-primary-600: #0284c7;
            --color-primary-700: #0369a1;
            --color-primary-800: #075985;
            --color-primary-900: #0c4a6e;
            
            --color-success-50: #f0fdf4;
            --color-success-100: #dcfce7;
            --color-success-200: #bbf7d0;
            --color-success-300: #86efac;
            --color-success-400: #4ade80;
            --color-success-500: #22c55e;
            --color-success-600: #16a34a;
            --color-success-700: #15803d;
            --color-success-800: #166534;
            --color-success-900: #14532d;
            
            --color-warning-50: #fffbeb;
            --color-warning-100: #fef3c7;
            --color-warning-200: #fde68a;
            --color-warning-300: #fcd34d;
            --color-warning-400: #fbbf24;
            --color-warning-500: #f59e0b;
            --color-warning-600: #d97706;
            --color-warning-700: #b45309;
            --color-warning-800: #92400e;
            --color-warning-900: #78350f;
            
            --color-danger-50: #fef2f2;
            --color-danger-100: #fee2e2;
            --color-danger-200: #fecaca;
            --color-danger-300: #fca5a5;
            --color-danger-400: #f87171;
            --color-danger-500: #ef4444;
            --color-danger-600: #dc2626;
            --color-danger-700: #b91c1c;
            --color-danger-800: #991b1b;
            --color-danger-900: #7f1d1d;
            
            --color-gray-50: #f9fafb;
            --color-gray-100: #f3f4f6;
            --color-gray-200: #e5e7eb;
            --color-gray-300: #d1d5db;
            --color-gray-400: #9ca3af;
            --color-gray-500: #6b7280;
            --color-gray-600: #4b5563;
            --color-gray-700: #374151;
            --color-gray-800: #1f2937;
            --color-gray-900: #111827;
            
            /* Modo claro - CRM Professional Light */
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-surface: #f1f5f9;
            --bg-card: #ffffff;
            --bg-hover: #f1f5f9;
            
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --text-inverse: #ffffff;
            
            --border-color: #e2e8f0;
            --border-light: #f1f5f9;
            --border-focus: #3b82f6;
            
            --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
            --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
        """
    
    return f"""
    <style>
    :root {{
        {theme_vars}
        --radius-sm: 0.25rem;
        --radius-md: 0.375rem;
        --radius-lg: 0.5rem;
        --radius-xl: 0.75rem;
        --radius-2xl: 1rem;
        
        --transition-base: all 0.2s ease-in-out;
        --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono: 'SF Mono', Monaco, Inconsolata, 'Roboto Mono', monospace;
    }}
    
    /* IMPORTAR FUENTES */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* RESET Y BASE */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    body, .stApp {{
        font-family: var(--font-sans);
        background-color: var(--bg-primary);
        color: var(--text-primary);
        line-height: 1.6;
        transition: var(--transition-base);
    }}
    
    /* CLASE PARA MODO OSCURO */
    .dark {{
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }}
    
    /* CONTENEDORES PRINCIPALES */
    .main .block-container {{
        max-width: 1400px !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }}
    
    /* COMPONENTES CRM UNIFICADOS */
    .crm-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition-smooth);
    }}
    
    .crm-card:hover {{
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }}
    
    .crm-card-header {{
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }}
    
    .crm-button {{
        background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.625rem 1.25rem;
        font-weight: 500;
        transition: var(--transition-smooth);
        cursor: pointer;
    }}
    
    .crm-button:hover {{
        background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-700));
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }}
    
    .crm-button-secondary {{
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }}
    
    .crm-button-secondary:hover {{
        background: var(--bg-hover);
        border-color: var(--border-focus);
    }}
    
    .crm-input {{
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        color: var(--text-primary);
        transition: var(--transition-base);
        width: 100%;
    }}
    
    .crm-input:focus {{
        outline: none;
        border-color: var(--border-focus);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }}
    
    .crm-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }}
    
    .crm-table th {{
        background: var(--bg-secondary);
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 600;
        color: var(--text-secondary);
        border-bottom: 1px solid var(--border-color);
    }}
    
    .crm-table td {{
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border-light);
    }}
    
    .crm-table tr:hover td {{
        background: var(--bg-hover);
    }}
    
    .crm-badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: var(--radius-full);
        font-size: 0.75rem;
        font-weight: 500;
        line-height: 1;
    }}
    
    .crm-badge-primary {{
        background: var(--color-primary-100);
        color: var(--color-primary-800);
    }}
    
    .crm-badge-success {{
        background: var(--color-success-100);
        color: var(--color-success-800);
    }}
    
    .crm-badge-warning {{
        background: var(--color-warning-100);
        color: var(--color-warning-800);
    }}
    
    .crm-badge-danger {{
        background: var(--color-danger-100);
        color: var(--color-danger-800);
    }}
    
    /* LOADING STATES */
    .crm-loading {{
        display: inline-block;
        width: 1.5rem;
        height: 1.5rem;
        border: 2px solid var(--border-color);
        border-radius: 50%;
        border-top-color: var(--color-primary-500);
        animation: spin 1s ease-in-out infinite;
    }}
    
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    
    /* RESPONSIVE */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        
        .crm-card {{
            padding: 1rem;
            margin: 0.5rem;
        }}
    }}
    
    /* UTILITY CLASSES */
    .text-gradient {{
        background: linear-gradient(135deg, var(--color-primary-600), var(--color-primary-700));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .shadow-gradient {{
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
                    0 2px 4px -1px rgba(0, 0, 0, 0.06),
                    0 0 0 1px var(--border-color);
    }}
    </style>
    """