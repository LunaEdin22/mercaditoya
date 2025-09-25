# 🛒 MercaditoYa

Sistema web completo de mercadito desarrollado con Flask (Python) siguiendo arquitectura MVC.

## 📋 Características

- **Gestión de Productos**: CRUD completo con categorías y control de stock
- **Sistema de Usuarios**: Registro, login con roles (admin, cliente, repartidor)
- **Carrito de Compras**: Funcionalidad completa con sesiones
- **Gestión de Pedidos**: Estados, delivery/retiro, historial
- **Panel de Administración**: Dashboard, estadísticas, gestión completa
- **Subida de Imágenes**: Integración con ImgBB API
- **Autenticación Segura**: bcrypt para contraseñas
- **Diseño Responsivo**: Bootstrap 5 con tema personalizado
- **Base de Datos**: SQL Server con consultas optimizadas

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- SQL Server 2017+ (Express o superior)
- ODBC Driver 17 for SQL Server
- Cuenta en ImgBB para API de imágenes

### 1. Clonar y Configurar el Proyecto

```bash
cd C:\minimarket

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass


# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar SQL Server

**Instalar SQL Server Express:**
1. Descargar de: https://www.microsoft.com/sql-server/sql-server-downloads
2. Instalar SQL Server Express
3. Instalar SQL Server Management Studio (SSMS)

**Instalar ODBC Driver:**
1. Descargar de: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Instalar "ODBC Driver 17 for SQL Server"

### 3. Configurar Variables de Entorno

Copiar `.env.example` a `.env` y editar:

```env
# Base de datos SQL Server
SQLSERVER_SERVER=localhost
SQLSERVER_DATABASE=minimarket_db
SQLSERVER_USERNAME=sa
SQLSERVER_PASSWORD=TuPasswordSQL123
SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server

# Clave secreta
SECRET_KEY=tu-clave-secreta-muy-segura-y-larga

# API de ImgBB
IMGBB_API_KEY=tu-api-key-de-imgbb
```

**Obtener API Key de ImgBB:**
1. Registrarse en https://imgbb.com/
2. Ir a https://api.imgbb.com/
3. Obtener tu API key

### 4. Inicializar Base de Datos

```bash
# Probar conexión y crear base de datos
python setup_sqlserver.py

# Ejecutar script de inicialización en SQL Server Management Studio
database/init_sqlserver.sql
```

### 5. Ejecutar la Aplicación

```bash
python run.py
```

La aplicación estará disponible en: http://localhost:5000

## 👤 Usuarios por Defecto

**Administrador:**
- Email: `admin@gmail.com`
- Contraseña: `123456`

## 📁 Estructura del Proyecto

```
minimarket/
│
├── app/
│   ├── models/              # Modelos de datos (SQLAlchemy)
│   │   ├── __init__.py      # Definición de todas las tablas
│   │   ├── usuario.py
│   │   ├── producto.py
│   │   ├── categoria.py
│   │   ├── pedido.py
│   │   └── rol.py
│   │
│   ├── controllers/         # Controladores (Blueprint routes)
│   │   ├── __init__.py
│   │   ├── auth_controller.py      # Login/logout/registro
│   │   ├── main_controller.py      # Páginas principales
│   │   ├── productos_controller.py # CRUD productos y categorías
│   │   ├── pedidos_controller.py   # Carrito y pedidos
│   │   └── usuarios_controller.py  # Gestión de usuarios
│   │
│   ├── views/               # Plantillas HTML (Jinja2)
│   │   ├── base.html        # Plantilla base
│   │   ├── index.html       # Página principal
│   │   ├── productos.html   # Lista de productos
│   │   ├── detalle_producto.html
│   │   ├── auth/            # Plantillas de autenticación
│   │   ├── carrito/         # Plantillas del carrito
│   │   ├── pedidos/         # Plantillas de pedidos
│   │   └── admin/           # Panel de administración
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Estilos personalizados
│   │   └── js/
│   │       └── main.js      # JavaScript principal
│   │
│   ├── __init__.py          # Configuración de Flask
│   └── app.py
│
├── instance/
│   └── config.py            # Configuración de la aplicación
│
├── database/
│   └── init_db.sql          # Script de inicialización
│
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias Python
├── run.py                   # Script principal
└── README.md               # Este archivo
```

## 🎯 Funcionalidades Principales

### Para Clientes
- ✅ Registro e inicio de sesión
- ✅ Explorar productos por categorías
- ✅ Búsqueda de productos
- ✅ Agregar productos al carrito
- ✅ Gestionar carrito (modificar cantidades, eliminar)
- ✅ Realizar pedidos (retiro/delivery)
- ✅ Ver historial de pedidos
- ✅ Gestionar perfil personal

### Para Administradores
- ✅ Dashboard con estadísticas
- ✅ CRUD completo de productos
- ✅ Gestión de categorías
- ✅ Subida de imágenes a ImgBB
- ✅ Control de stock
- ✅ Gestión de pedidos (cambiar estados)
- ✅ Administración de usuarios
- ✅ Cambio de roles
- ✅ Reportes y estadísticas

## 💾 Base de Datos

### Tablas Principales
- `roles` - Roles del sistema
- `usuarios` - Información de usuarios
- `categorias` - Categorías de productos
- `productos` - Catálogo de productos
- `pedidos` - Órdenes de compra
- `pedido_detalle` - Ítems de cada pedido

### Vistas Optimizadas
- `vista_productos_stock_bajo` - Productos con poco stock
- `vista_pedidos_recientes` - Pedidos del último mes
- `vista_productos_mas_vendidos` - Ranking de ventas

## 🔧 Desarrollo

### Estructura MVC
- **Models**: Definición de tablas y relaciones (SQLAlchemy)
- **Views**: Plantillas HTML con Jinja2
- **Controllers**: Lógica de negocio y rutas (Flask Blueprints)

### Características Técnicas
- **Autenticación**: Flask-Login + bcrypt
- **Base de Datos**: SQLAlchemy ORM
- **Frontend**: Bootstrap 5 + JavaScript vanilla
- **API Externa**: ImgBB para imágenes
- **Seguridad**: Validación de datos, protección CSRF

### APIs y Endpoints

#### Públicos
```
GET  /                    # Página principal
GET  /productos          # Lista de productos
GET  /producto/<id>      # Detalle de producto
POST /pedidos/agregar_carrito  # Agregar al carrito (AJAX)
```

#### Autenticación
```
GET/POST /auth/login     # Iniciar sesión
GET/POST /auth/register  # Registrarse
GET      /auth/logout    # Cerrar sesión
GET/POST /auth/perfil    # Ver/editar perfil
```

#### Carrito y Pedidos
```
GET  /pedidos/carrito           # Ver carrito
POST /pedidos/actualizar_carrito # Modificar carrito
GET  /pedidos/checkout          # Finalizar compra
POST /pedidos/procesar_pedido   # Crear pedido
GET  /pedidos/mis_pedidos       # Historial de pedidos
```

#### Administración
```
GET  /productos/admin                    # Dashboard admin
GET  /productos/admin/productos         # Lista productos admin
GET  /productos/admin/producto/nuevo    # Crear producto
POST /productos/admin/producto/<id>/eliminar # Eliminar producto
GET  /usuarios/admin/usuarios           # Gestión usuarios
POST /usuarios/admin/usuario/<id>/estado # Cambiar estado usuario
```

## 🎨 Personalización

### Modificar Tema
- Editar `app/static/css/style.css`
- Cambiar variables CSS en `:root`
- Modificar colores de Bootstrap

### Agregar Nuevas Funcionalidades
1. Crear modelo en `app/models/`
2. Crear controlador en `app/controllers/`
3. Agregar plantillas en `app/views/`
4. Registrar blueprint en `app/__init__.py`

## 📱 Responsive Design

- **Mobile First**: Diseño optimizado para móviles
- **Breakpoints**: sm (576px), md (768px), lg (992px), xl (1200px)
- **Componentes**: Cards, modals, navegación responsive

## 🔒 Seguridad

- **Contraseñas**: Hasheadas con bcrypt
- **Sesiones**: Flask-Login para autenticación
- **Validación**: Validación de entrada en formularios
- **SQL Injection**: Prevención con SQLAlchemy ORM
- **CSRF**: Protección con Flask-WTF

## 📊 Base de Datos

### Configuración MySQL
```sql
-- Crear usuario específico (opcional)
CREATE USER 'minimarket_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON minimarket_db.* TO 'minimarket_user'@'localhost';
FLUSH PRIVILEGES;
```

### Backup y Restore
```bash
# Backup
mysqldump -u root -p minimarket_db > backup.sql

# Restore
mysql -u root -p minimarket_db < backup.sql
```

## 🚀 Despliegue en Producción

### Variables de Entorno Producción
```env
FLASK_ENV=production
SECRET_KEY=clave-super-secreta-produccion
DEBUG=False
```

### Servidor Web
- **Gunicorn**: Para servir la aplicación
- **Nginx**: Como proxy reverso
- **MySQL**: Base de datos en producción

### Comandos de Despliegue
```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar con Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## 🐛 Solución de Problemas

### Error de Conexión a MySQL
```bash
# Verificar servicio MySQL
net start mysql

# Verificar conexión
mysql -u root -p -e "SHOW DATABASES;"
```

### Error de Importación
```bash
# Verificar entorno virtual activado
where python

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de ImgBB API
1. Verificar API key en `.env`
2. Comprobar límites de la cuenta
3. Revisar formato de imagen (JPG, PNG)

## 📈 Próximas Mejoras

- [ ] Sistema de cupones y descuentos
- [ ] Notificaciones push
- [ ] Chat en vivo
- [ ] Sistema de reviews y calificaciones
- [ ] Integración con pasarelas de pago
- [ ] API REST completa
- [ ] App móvil
- [ ] Sistema de inventario automático
- [ ] Reportes avanzados con gráficos

## 👥 Contribuir

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- 📧 Email: support@minimarket.com
- 💬 GitHub Issues: [Crear issue](https://github.com/usuario/minimarket/issues)

---

**¡Gracias por usar MiniMarket Online!** 🛒✨