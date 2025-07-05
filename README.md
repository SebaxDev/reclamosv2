# Fusion Reclamos App - Sistema de Gestión de Reclamos

## 📌 Descripción

Fusion Reclamos App es una aplicación web desarrollada con Streamlit para la gestión integral de reclamos de servicios públicos. La aplicación permite:

- 🆕 Registrar nuevos reclamos con validación de clientes existentes
- 📋 Visualizar y gestionar reclamos activos
- 👥 Asignar técnicos y grupos de trabajo
- ✅ Cierre y seguimiento de reclamos
- 📊 Generación de reportes en PDF
- 📈 Dashboard con métricas clave

## 🚀 Características principales

- **Autenticación de usuarios** con diferentes niveles de permisos
- **Integración con Google Sheets** como base de datos
- **Modo oscuro/claro** adaptable al sistema
- **Interfaz intuitiva** con navegación por secciones
- **Generación de PDFs** para impresión y distribución
- **Sistema de asignación** de reclamos a grupos de técnicos
- **Validación en tiempo real** de reclamos duplicados
- **Historial completo** por cliente

## 🛠️ Tecnologías utilizadas

- ![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
- ![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-FF4B4B?logo=streamlit)
- ![Google Sheets API](https://img.shields.io/badge/Google_Sheets_API-v4-34A853?logo=google-sheets)
- ![Pandas](https://img.shields.io/badge/Pandas-1.5+-150458?logo=pandas)
- ![ReportLab](https://img.shields.io/badge/ReportLab-3.6+-000000)

## 📦 Instalación y configuración

### Requisitos previos
- Python 3.9 o superior
- Cuenta de Google Cloud Platform con Sheets API habilitada
- Archivo de credenciales de servicio de Google Cloud

### Pasos para instalar

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/fusion-reclamos-app.git
   cd fusion-reclamos-app
   ```

2. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar credenciales:
   - Crear archivo `.streamlit/secrets.toml` con las credenciales de Google Sheets:
     ```toml
     [gcp_service_account]
     type = "service_account"
     project_id = "tu-project-id"
     private_key_id = "tu-private-key-id"
     private_key = "-----BEGIN PRIVATE KEY-----\ntu-clave-privada\n-----END PRIVATE KEY-----\n"
     client_email = "tu-service-account@tu-project.iam.gserviceaccount.com"
     client_id = "tu-client-id"
     auth_uri = "https://accounts.google.com/o/oauth2/auth"
     token_uri = "https://oauth2.googleapis.com/token"
     auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
     client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/tu-service-account%40tu-project.iam.gserviceaccount.com"
     ```

5. Configurar IDs de Google Sheets:
   - Editar `config/settings.py` con los IDs de tus hojas de cálculo

6. Ejecutar la aplicación:
   ```bash
   streamlit run app.py
   ```

## 🖥️ Uso de la aplicación

### Secciones principales

1. **Inicio - Nuevo reclamo**
   - Registro de nuevos reclamos con validación de cliente existente
   - Bloqueo de múltiples reclamos activos para un mismo cliente
   - Carga automática de datos de clientes existentes

2. **Reclamos cargados**
   - Visualización de reclamos con filtros avanzados
   - Edición manual de reclamos
   - Gestión de estados (Pendiente/En curso/Resuelto)
   - Manejo especial de "Desconexiones a pedido"

3. **Historial por cliente**
   - Búsqueda por número de cliente
   - Visualización de todos los reclamos asociados
   - Exportación a CSV

4. **Editar cliente** (solo admin)
   - Modificación de datos de clientes existentes
   - Registro de nuevos clientes

5. **Imprimir reclamos**
   - Generación de PDFs por tipo de reclamo
   - Selección manual de reclamos para impresión
   - Exportación de todos los reclamos activos

6. **Seguimiento técnico** (solo admin)
   - Asignación de reclamos a grupos de trabajo
   - Designación de técnicos por grupo
   - Generación de PDFs por grupo asignado

7. **Cierre de Reclamos** (solo admin)
   - Cambio de estado a "Resuelto"
   - Actualización de precintos
   - Devolver reclamos a estado "Pendiente"

## 👥 Roles y permisos

- **Administrador**: Acceso completo a todas las funciones
- **Usuario estándar**: Puede cargar reclamos y ver información
- **Técnico**: Acceso limitado a funciones de seguimiento

## 📊 Estructura del proyecto

```
fusion-reclamos-app/
├── app.py                # Aplicación principal
├── components/           # Componentes reutilizables
│   ├── auth.py           # Autenticación
│   ├── navigation.py     # Navegación
│   └── metrics.py        # Dashboard de métricas
├── config/
│   └── settings.py       # Configuraciones
├── utils/
│   ├── data_manager.py   # Manejo de datos
│   ├── styles.py         # Estilos CSS
│   └── api_manager.py    # Gestión de API
├── requirements.txt      # Dependencias
└── .streamlit/
    └── secrets.toml      # Credenciales
```

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz un fork del proyecto
2. Crea una rama con tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Haz push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo la licencia MIT. Consulta el archivo `LICENSE` para más información.

## ✉️ Contacto

---

Hecho con ❤️ usando Streamlit