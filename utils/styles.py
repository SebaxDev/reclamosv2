# styles.py - Tema Monokai Profesional Completo
"""Estilos CSS profesionales Monokai para Fusion CRM"""

def get_main_styles():
    """Devuelve estilos CSS profesionales con tema Monokai completo"""
    
    theme_vars = """
        --primary-color: #66D9EF;     /* Azul verdoso Monokai */
        --primary-light: #78C6E9;     /* Azul más claro */
        --primary-dark: #56B6C2;      /* Azul oscuro */
        --secondary-color: #F92672;   /* Magenta Monokai */
        --secondary-light: #FF79C6;   /* Rosa claro */
        --success-color: #A6E22E;     /* Verde Monokai */
        --success-light: #B6E63E;     /* Verde claro */
        --warning-color: #FD971F;     /* Naranja Monokai */
        --warning-light: #FFA94D;     /* Naranja claro */
        --danger-color: #FF6188;      /* Rosa-rojo Monokai */
        --danger-light: #FF85B3;      /* Rosa claro */
        --info-color: #AE81FF;        /* Púrpura Monokai */
        --info-light: #C5A3FF;        /* Púrpura claro */
        
        --bg-primary: #272822;        /* Fondo principal Monokai */
        --bg-secondary: #2D2E27;      /* Fondo secundario */
        --bg-tertiary: #34352E;       /* Fondo terciario */
        --bg-surface: #3E3D32;        /* Superficie de elementos */
        --bg-card: #383830;           /* Tarjetas */
        --bg-hover: #46483D;          /* Fondo hover */
        --bg-active: #4F5144;         /* Fondo activo */
        
        --text-primary: #F8F8F2;      /* Texto principal */
        --text-secondary: #CFCFC2;    /* Texto secundario */
        --text-tertiary: #A6A699;     /* Texto terciario */
        --text-muted: #75715E;        /* Texto atenuado */
        --text-accent: #66D9EF;       /* Texto acento */
        
        --border-color: #49483E;      /* Color de bordes */
        --border-light: #5E5D56;      /* Bordes claros */
        --border-dark: #3C3D34;       /* Bordes oscuros */
        --border-accent: #66D9EF;     /* Borde acento */
        
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.25);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
        --shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.3);
        
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --radius-2xl: 1.5rem;
        
        --transition-base: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-colors: color 0.2s, background-color 0.2s, border-color 0.2s;
        --transition-transform: transform 0.2s;
        --transition-shadow: box-shadow 0.2s;
        
        --gradient-primary: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-light) 100%);
        --gradient-secondary: linear-gradient(135deg, var(--secondary-color) 0%, var(--secondary-light) 100%);
        --gradient-success: linear-gradient(135deg, var(--success-color) 0%, var(--success-light) 100%);
        --gradient-warning: linear-gradient(135deg, var(--warning-color) 0%, var(--warning-light) 100%);
        --gradient-danger: linear-gradient(135deg, var(--danger-color) 0%, var(--danger-light) 100%);
        --gradient-info: linear-gradient(135deg, var(--info-color) 0%, var(--info-light) 100%);
        
        --gradient-bg: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%);
        --gradient-card: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-surface) 100%);
    """
    
    return f"""
    <style>
    :root {{
        {theme_vars}
    }}
    
    /* FUENTES Y TIPOGRAFÍA MONOKAI */
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}
    
    body, .stApp {{
        font-family: 'Inter', 'Fira Code', 'SF Mono', Monaco, Inconsolata, 'Roboto Mono', monospace;
        background: var(--gradient-bg);
        color: var(--text-primary);
        line-height: 1.7;
        font-weight: 400;
        min-height: 100vh;
    }}
    
    /* MEJORAS PARA CONTENEDORES PRINCIPALES - ANCHO EXPANDIDO */
    .main .block-container {{
        max-width: 1500px !important;
        padding-top: 2.5rem;
        padding-bottom: 2.5rem;
        padding-left: 4rem;
        padding-right: 4rem;
        background: transparent;
    }}
    
    /* HEADERS Y TÍTULOS MONOKAI */
    h1, h2, h3, h4, h5, h6 {{
        font-weight: 700;
        margin-bottom: 1rem;
        color: var(--text-primary);
        letter-spacing: -0.025em;
        line-height: 1.2;
        font-family: 'Fira Code', 'Inter', monospace;
    }}
    
    h1 {{
        font-size: 3rem;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        position: relative;
        padding-bottom: 0.5rem;
    }}
    
    h1::after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100px;
        height: 4px;
        background: var(--gradient-primary);
        border-radius: var(--radius-md);
    }}
    
    h2 {{
        font-size: 2.25rem;
        color: var(--text-primary);
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border-color);
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
    }}
    
    h3 {{
        font-size: 1.75rem;
        color: var(--text-secondary);
        margin-bottom: 1.25rem;
    }}
    
    h4 {{
        font-size: 1.5rem;
        color: var(--text-tertiary);
        margin-bottom: 1rem;
    }}
    
    h5 {{
        font-size: 1.25rem;
        color: var(--text-muted);
        margin-bottom: 0.75rem;
    }}
    
    h6 {{
        font-size: 1.1rem;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
        font-weight: 600;
    }}
    
    /* BOTONES MONOKAI MEJORADOS */
    .stButton > button {{
        border: none;
        border-radius: var(--radius-lg);
        padding: 1rem 2rem;
        font-weight: 600;
        font-family: 'Fira Code', monospace;
        transition: var(--transition-base);
        cursor: pointer;
        box-shadow: var(--shadow-md);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        position: relative;
        overflow: hidden;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
    }}
    
    .stButton > button::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }}
    
    .stButton > button:hover::before {{
        left: 100%;
    }}
    
    .stButton > button:focus {{
        outline: none;
        box-shadow: 0 0 0 4px rgba(102, 217, 239, 0.4);
    }}
    
    /* Botón primario */
    .stButton > button:first-child {{
        background: var(--gradient-primary);
        color: #272822 !important;
        border: 2px solid var(--primary-color);
    }}
    
    .stButton > button:first-child:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: var(--shadow-lg);
        background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary-color) 100%);
    }}
    
    .stButton > button:first-child:active {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }}
    
    /* Botones secundarios */
    .stButton > button:not(:first-child) {{
        background: transparent;
        color: var(--primary-color) !important;
        border: 2px solid var(--primary-color);
        backdrop-filter: blur(10px);
    }}
    
    .stButton > button:not(:first-child):hover {{
        background: var(--primary-color);
        color: #272822 !important;
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
    }}
    
    /* Botones de éxito */
    .stButton > button.ui-button-success {{
        background: var(--gradient-success);
        color: #272822 !important;
        border: 2px solid var(--success-color);
    }}
    
    .stButton > button.ui-button-success:hover {{
        background: linear-gradient(135deg, var(--success-light) 0%, var(--success-color) 100%);
    }}
    
    /* Botones de peligro */
    .stButton > button.ui-button-danger {{
        background: var(--gradient-danger);
        color: #272822 !important;
        border: 2px solid var(--danger-color);
    }}
    
    .stButton > button.ui-button-danger:hover {{
        background: linear-gradient(135deg, var(--danger-light) 0%, var(--danger-color) 100%);
    }}
    
    /* Botones de advertencia */
    .stButton > button.ui-button-warning {{
        background: var(--gradient-warning);
        color: #272822 !important;
        border: 2px solid var(--warning-color);
    }}
    
    .stButton > button.ui-button-warning:hover {{
        background: linear-gradient(135deg, var(--warning-light) 0%, var(--warning-color) 100%);
    }}
    
    /* TARJETAS Y CONTENEDORES ELEGANTES MONOKAI */
    .card {{
        background: var(--gradient-card);
        border-radius: var(--radius-xl);
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        transition: var(--transition-base);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }}
    
    .card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--gradient-primary);
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .card:hover {{
        transform: translateY(-5px) scale(1.01);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary-color);
    }}
    
    .card:hover::before {{
        opacity: 1;
    }}
    
    .card-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }}
    
    .card-title {{
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        font-family: 'Fira Code', monospace;
    }}
    
    .card-content {{
        color: var(--text-secondary);
        line-height: 1.8;
    }}
    
    /* FORMULARIOS ELEGANTES MONOKAI */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {{
        background: var(--bg-surface);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1rem 1.25rem;
        color: var(--text-primary);
        font-size: 1rem;
        font-family: 'Fira Code', monospace;
        transition: var(--transition-base);
        box-shadow: var(--shadow-sm);
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus,
    .stTimeInput > div > div > input:focus {{
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(102, 217, 239, 0.2);
        outline: none;
        background: var(--bg-card);
        transform: translateY(-2px);
    }}
    
    .stTextInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover,
    .stSelectbox > div > div > select:hover,
    .stNumberInput > div > div > input:hover,
    .stDateInput > div > div > input:hover,
    .stTimeInput > div > div > input:hover {{
        border-color: var(--border-light);
        box-shadow: var(--shadow-md);
    }}
    
    /* LABELS MEJORADOS MONOKAI */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label,
    .stDateInput label,
    .stTimeInput label {{
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 0.75rem;
        display: block;
        font-family: 'Fira Code', monospace;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* SIDEBAR MONOKAI PROFESIONAL */
    .css-1d391kg {{
        background: var(--bg-secondary) !important;
        border-right: 2px solid var(--border-dark);
        box-shadow: var(--shadow-lg);
    }}
    
    .css-1d391kg .stButton > button {{
        width: 100%;
        justify-content: flex-start;
        margin-bottom: 0.75rem;
        border-radius: var(--radius-lg);
        background: transparent;
        color: var(--text-secondary) !important;
        border: 2px solid transparent;
        padding: 1rem 1.5rem;
        font-family: 'Fira Code', monospace;
        transition: var(--transition-base);
    }}
    
    .css-1d391kg .stButton > button:hover {{
        background: var(--bg-hover) !important;
        border-color: var(--primary-color);
        color: var(--text-primary) !important;
        transform: translateX(5px);
    }}
    
    .css-1d391kg .stButton > button:focus {{
        background: var(--bg-active) !important;
        border-color: var(--primary-color);
    }}
    
    /* MEJORAS PARA TABLAS MONOKAI */
    .dataframe {{
        border-radius: var(--radius-xl);
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 2px solid var(--border-color);
        margin: 2rem 0;
        min-width: 100% !important;
        background: var(--bg-card);
        font-family: 'Fira Code', monospace;
    }}
    
    .dataframe thead th {{
        background: var(--gradient-primary);
        color: #272822 !important;
        font-weight: 700;
        padding: 1.25rem;
        text-align: left;
        border: none;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .dataframe tbody td {{
        padding: 1.125rem 1.25rem;
        border-bottom: 1px solid var(--border-light);
        background: var(--bg-surface);
        color: var(--text-primary);
        transition: var(--transition-base);
        font-size: 0.9rem;
    }}
    
    .dataframe tbody tr:hover td {{
        background: var(--bg-hover);
        transform: scale(1.01);
        box-shadow: var(--shadow-sm);
    }}
    
    .dataframe tbody tr:last-child td {{
        border-bottom: none;
    }}
    
    /* Mejorar visualización de tablas */
    .dataframe th, .dataframe td {{
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    /* NOTIFICACIONES Y ALERTAS MEJORADAS MONOKAI */
    .stAlert {{
        border-radius: var(--radius-xl);
        border: none;
        box-shadow: var(--shadow-lg);
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        background: var(--bg-card);
        border-left: 6px solid var(--info-color);
        font-family: 'Fira Code', monospace;
    }}
    
    .stAlert[data-baseweb="notification"].success {{
        border-left-color: var(--success-color);
        background: linear-gradient(135deg, var(--bg-card) 0%, rgba(166, 226, 46, 0.1) 100%);
    }}
    
    .stAlert[data-baseweb="notification"].warning {{
        border-left-color: var(--warning-color);
        background: linear-gradient(135deg, var(--bg-card) 0%, rgba(253, 151, 31, 0.1) 100%);
    }}
    
    .stAlert[data-baseweb="notification"].error {{
        border-left-color: var(--danger-color);
        background: linear-gradient(135deg, var(--bg-card) 0%, rgba(255, 97, 136, 0.1) 100%);
    }}
    
    .stAlert .stAlertHeader {{
        color: var(--text-primary);
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }}
    
    .stAlert .stAlertContent {{
        color: var(--text-secondary);
        line-height: 1.6;
    }}
    
    /* BADGES Y ETIQUETAS MONOKAI */
    .badge {{
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1.25rem;
        border-radius: var(--radius-xl);
        font-size: 0.85rem;
        font-weight: 700;
        font-family: 'Fira Code', monospace;
        border: 2px solid;
        transition: var(--transition-base);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .badge-primary {{
        background: rgba(102, 217, 239, 0.15);
        color: var(--primary-color);
        border-color: var(--primary-color);
    }}
    
    .badge-success {{
        background: rgba(166, 226, 46, 0.15);
        color: var(--success-color);
        border-color: var(--success-color);
    }}
    
    .badge-warning {{
        background: rgba(253, 151, 31, 0.15);
        color: var(--warning-color);
        border-color: var(--warning-color);
    }}
    
    .badge-danger {{
        background: rgba(255, 97, 136, 0.15);
        color: var(--danger-color);
        border-color: var(--danger-color);
    }}
    
    .badge-info {{
        background: rgba(174, 129, 255, 0.15);
        color: var(--info-color);
        border-color: var(--info-color);
    }}
    
    .badge:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }}
    
    /* GRID SYSTEM MEJORADO */
    .stHorizontalBlock > div {{
        gap: 1.5rem;
    }}
    
    .stColumn {{
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        border: 1px solid var(--border-color);
        transition: var(--transition-base);
    }}
    
    .stColumn:hover {{
        border-color: var(--primary-color);
        box-shadow: var(--shadow-md);
    }}
    
    /* SCROLLBAR PERSONALIZADO MONOKAI */
    ::-webkit-scrollbar {{
        width: 12px;
        height: 12px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--bg-secondary);
        border-radius: var(--radius-md);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--border-color);
        border-radius: var(--radius-md);
        border: 3px solid var(--bg-secondary);
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--border-light);
    }}
    
    ::-webkit-scrollbar-corner {{
        background: var(--bg-secondary);
    }}
    
    /* EFECTOS DE CARGA Y ANIMACIONES MONOKAI */
    .skeleton {{
        background: linear-gradient(90deg, var(--bg-surface) 25%, var(--bg-secondary) 50%, var(--bg-surface) 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
        border-radius: var(--radius-md);
    }}
    
    @keyframes loading {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    
    .pulse {{
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
        100% {{ opacity: 1; }}
    }}
    
    .glow {{
        animation: glow 2s ease-in-out infinite alternate;
    }}
    
    @keyframes glow {{
        from {{ box-shadow: 0 0 5px var(--primary-color); }}
        to {{ box-shadow: 0 0 20px var(--primary-color), 0 0 30px var(--primary-light); }}
    }}
    
    /* RESPONSIVE DESIGN MONOKAI */
    @media (max-width: 1200px) {{
        .main .block-container {{
            padding-left: 3rem;
            padding-right: 3rem;
        }}
    }}
    
    @media (max-width: 992px) {{
        .main .block-container {{
            padding-left: 2rem;
            padding-right: 2rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
        }}
        
        h2 {{
            font-size: 2rem;
        }}
    }}
    
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: 1.5rem;
            max-width: 100% !important;
        }}
        
        .card {{
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        
        h1 {{
            font-size: 2.25rem;
        }}
        
        h2 {{
            font-size: 1.75rem;
        }}
        
        h3 {{
            font-size: 1.5rem;
        }}
        
        .stButton > button {{
            padding: 0.875rem 1.5rem;
            font-size: 0.85rem;
        }}
        
        /* Ajustar grid para móviles */
        .stHorizontalBlock > div {{
            grid-template-columns: 1fr !important;
            gap: 1.25rem;
        }}
    }}
    
    @media (max-width: 480px) {{
        .main .block-container {{
            padding: 1rem;
        }}
        
        .card {{
            padding: 1.25rem;
        }}
        
        h1 {{
            font-size: 2rem;
        }}
        
        h2 {{
            font-size: 1.5rem;
        }}
    }}
    
    /* UTILIDADES MONOKAI */
    .text-gradient {{
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .bg-gradient {{
        background: var(--gradient-bg);
    }}
    
    .border-gradient {{
        border: 2px solid transparent;
        background: linear-gradient(var(--bg-card), var(--bg-card)) padding-box,
                    var(--gradient-primary) border-box;
    }}
    
    .shadow-monokai {{
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), 0 5px 15px rgba(0, 0, 0, 0.2);
    }}
    
    .hover-lift:hover {{
        transform: translateY(-5px);
        box-shadow: var(--shadow-xl);
    }}
    
    .hover-glow:hover {{
        box-shadow: 0 0 15px rgba(102, 217, 239, 0.3);
    }}
    
    /* ELEMENTOS ESPECÍFICOS DE STREAMLIT */
    .stMarkdown {{
        color: var(--text-secondary);
        line-height: 1.8;
    }}
    
    .stMarkdown strong {{
        color: var(--text-primary);
    }}
    
    .stMarkdown a {{
        color: var(--primary-color);
        text-decoration: none;
        font-weight: 600;
        transition: var(--transition-colors);
    }}
    
    .stMarkdown a:hover {{
        color: var(--primary-light);
        text-decoration: underline;
    }}
    
    .stProgress > div > div {{
        background: var(--gradient-primary);
    }}
    
    .stSpinner > div {{
        border-color: var(--primary-color) transparent transparent transparent;
    }}
    
    /* SELECTORES Y DROPDOWNS MONOKAI */
    .stSelectbox > div > div {{
        background: var(--bg-surface);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-lg);
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: var(--border-light);
    }}
    
    .stSelectbox > div > div:focus-within {{
        border-color: var(--primary-color);
        box-shadow: 0 0 0 4px rgba(102, 217, 239, 0.2);
    }}
    
    /* CHECKBOXES Y RADIOS MONOKAI */
    .stCheckbox > label {{
        color: var(--text-secondary);
        font-family: 'Fira Code', monospace;
    }}
    
    .stCheckbox > label:hover {{
        color: var(--text-primary);
    }}
    
    .stRadio > label {{
        color: var(--text-secondary);
        font-family: 'Fira Code', monospace;
    }}
    
    .stRadio > div > label {{
        background: var(--bg-surface);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 0.75rem 1rem;
        transition: var(--transition-base);
    }}
    
    .stRadio > div > label:hover {{
        border-color: var(--primary-color);
        background: var(--bg-card);
    }}
    
    .stRadio > div > label[data-testid="stRadio"] {{
        background: var(--gradient-primary);
        color: #272822 !important;
        border-color: var(--primary-color);
    }}
    
    /* SLIDERS MONOKAI */
    .stSlider > div > div {{
        background: var(--border-color);
    }}
    
    .stSlider > div > div > div {{
        background: var(--gradient-primary);
    }}
    
    .stSlider > div > div > div:hover {{
        background: var(--primary-light);
    }}
    
    .stSlider > div > input {{
        color: var(--text-primary);
    }}
    
    /* TABS MONOKAI */
    .stTabs > div > button {{
        background: transparent !important;
        color: var(--text-secondary) !important;
        border: 2px solid transparent !important;
        font-family: 'Fira Code', monospace;
        font-weight: 600;
        transition: var(--transition-base);
    }}
    
    .stTabs > div > button:hover {{
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }}
    
    .stTabs > div > button[aria-selected="true"] {{
        color: var(--primary-color) !important;
        border-bottom: 3px solid var(--primary-color) !important;
        background: transparent !important;
    }}
    
    /* EXPANDERS MONOKAI */
    .streamlit-expanderHeader {{
        background: var(--bg-card);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 1rem 1.5rem;
        font-family: 'Fira Code', monospace;
        font-weight: 600;
        color: var(--text-secondary);
        transition: var(--transition-base);
    }}
    
    .streamlit-expanderHeader:hover {{
        border-color: var(--primary-color);
        color: var(--text-primary);
    }}
    
    .streamlit-expanderContent {{
        background: var(--bg-surface);
        border: 2px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 var(--radius-lg) var(--radius-lg);
        padding: 1.5rem;
    }}
    </style>
    """

def get_loading_spinner():
    """Spinner de carga Monokai mejorado"""
    return """
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background: linear-gradient(135deg, rgba(39, 40, 34, 0.98) 0%, rgba(45, 46, 39, 0.98) 100%);
        z-index: 9999;
        backdrop-filter: blur(12px);
    ">
        <div style="text-align: center;">
            <div style="
                width: 80px;
                height: 80px;
                border: 4px solid rgba(73, 72, 62, 0.3);
                border-radius: 50%;
                border-top-color: #66D9EF;
                border-right-color: #F92672;
                border-bottom-color: #A6E22E;
                border-left-color: #AE81FF;
                animation: spin 1.5s ease-in-out infinite;
                margin-bottom: 1.5rem;
                box-shadow: 0 0 30px rgba(102, 217, 239, 0.3);
            "></div>
            <p style="color: #F8F8F2; font-size: 1.25rem; font-weight: 600; margin: 0; font-family: 'Fira Code', monospace;">
                Cargando Fusion CRM...
            </p>
            <p style="color: #75715E; font-size: 0.95rem; margin: 0.75rem 0 0 0; font-family: 'Fira Code', monospace;">
                ⚡ Optimizado para rendimiento
            </p>
        </div>
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
    </div>
    """

def loading_indicator(message="Cargando datos..."):
    """Indicador de carga elegante Monokai"""
    return f"""
    <div style="text-align: center; padding: 3rem; background: var(--bg-card); border-radius: var(--radius-xl); border: 2px solid var(--border-color);">
        <div style="
            width: 60px;
            height: 60px;
            border: 3px solid rgba(102, 217, 239, 0.3);
            border-top: 3px solid #66D9EF;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem;
            box-shadow: 0 0 20px rgba(102, 217, 239, 0.2);
        "></div>
        <p style="color: var(--text-secondary); margin: 0; font-size: 1rem; font-family: 'Fira Code', monospace; font-weight: 500;">{message}</p>
    </div>
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """