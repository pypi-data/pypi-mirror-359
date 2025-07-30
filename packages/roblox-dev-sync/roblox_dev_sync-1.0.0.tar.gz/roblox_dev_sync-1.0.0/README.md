# Roblox Dev Sync

Un servidor que te permite sincronizar archivos entre Roblox Studio y tu IDE preferido. Desarrolla tus juegos de Roblox usando tu editor de código favorito mientras mantienes la conexión con Roblox Studio.

## Instalación del Plugin en Roblox Studio

1. **Descarga e Instalación del Plugin**
   - Abre Roblox Studio
   - Ve a la pestaña de Plugins
   - Haz clic en `+` para agregar un nuevo plugin
   - Copia y pega este enlace en el buscador: [https://create.roblox.com/store/asset/137634224705881/ConnectYourIDE](https://create.roblox.com/store/asset/137634224705881/ConnectYourIDE)
   - Haz clic en `Instalar`

2. **Configuración del Plugin**
   - Una vez importado, el plugin aparecerá en la pestaña de Plugins
   - Haz clic en el plugin para abrir la configuración
   - Configura la dirección del servidor local (por defecto: http://localhost:3000)
   - Guarda los cambios

## Instalación del Servidor

### Requisitos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. **Instalar desde PyPI**
```bash
pip install roblox-dev-sync
```

2. **Instalar desde GitHub**
```bash
pip install git+https://github.com/janxhg/roblox-dev-sync
```

### Iniciar el Servidor

1. **Usando el comando CLI**
```bash
roblox-sync
```

2. **Usando Python directamente**
```bash
python -m robloxidesync
```

El servidor iniciará en http://localhost:3000 por defecto.

## Uso

1. **Iniciar el Servidor**
   - Abre una terminal
   - Ejecuta `roblox-sync`
   - El servidor iniciará y mostrará el directorio de proyectos

2. **Crear un Nuevo Proyecto**
   - Abre Roblox Studio
   - Crea un nuevo juego o abre uno existente
   - Usa el plugin para crear un nuevo proyecto
   - El proyecto se sincronizará automáticamente con tu IDE

3. **Editar Archivos**
   - Puedes editar archivos .lua directamente en tu IDE
   - Los cambios se sincronizarán automáticamente con Roblox Studio
   - Los cambios en Roblox Studio también se sincronizarán con tu IDE

## Configuración

### Directorio de Proyectos
- Por defecto: `./roblox_projects`
- Puedes cambiar esta ruta modificando la variable `PROJECTS_DIR` en el código

### Puerto del Servidor
- Por defecto: 3000
- Puedes cambiar este puerto modificando la variable `SYNC_PORT` en el código

## Características

- Sincronización bidireccional entre Roblox Studio y tu IDE
- Soporte para todos los tipos de scripts de Roblox
- Observador de archivos para cambios en tiempo real
- Manejo automático de estructura de directorios
- Interfaz REST para comunicación con Roblox Studio

## Soporte

- Reporta problemas en el repositorio de GitHub
- Contacta al autor: NetechAI@proton.me

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.
