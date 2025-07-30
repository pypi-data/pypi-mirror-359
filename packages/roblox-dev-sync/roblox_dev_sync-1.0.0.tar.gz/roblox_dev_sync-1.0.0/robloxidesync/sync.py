#!/usr/bin/env python3
"""
Servidor de sincronización Roblox-IDE
Maneja la comunicación entre Roblox Studio y el IDE externo
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)
CORS(app)  # Permitir requests desde Roblox Studio

# Configuración
PROJECTS_DIR = "./roblox_projects"
SYNC_PORT = 3000
DEBUG_MODE = True

# Variables globales
projects = {}
file_updates = {}
last_update_time = {}

class ProjectFileHandler(FileSystemEventHandler):
    """Maneja cambios en los archivos del proyecto"""
    
    def __init__(self, project_name):
        self.project_name = project_name
        super().__init__()
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        
        # Solo procesar archivos .lua
        if file_path.suffix == '.lua':
            self.handle_file_change(file_path)
    
    def handle_file_change(self, file_path):
        """Procesa un cambio de archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Obtener ruta relativa
            project_dir = Path(PROJECTS_DIR) / self.project_name
            relative_path = file_path.relative_to(project_dir)
            
            # Convertir path del sistema a path de Roblox
            roblox_path = str(relative_path).replace('\\', '/').replace('.lua', '')
            
            # Determinar tipo de script basado en la carpeta
            script_type = self.determine_script_type(relative_path)
            
            update_data = {
                'name': file_path.stem,
                'path': roblox_path,
                'type': script_type,
                'source': content,
                'timestamp': time.time()
            }
            
            # Almacenar actualización
            if self.project_name not in file_updates:
                file_updates[self.project_name] = []
            
            file_updates[self.project_name].append(update_data)
            last_update_time[self.project_name] = time.time()
            
            print(f"File updated: {roblox_path} in project {self.project_name}")
            
        except Exception as e:
            print(f"Error handling file change: {e}")
    
    def determine_script_type(self, relative_path):
        """Determina el tipo de script basado en la ruta"""
        path_str = str(relative_path).lower()
        
        if 'serverscriptservice' in path_str or 'server' in path_str:
            return 'Script'
        elif 'starterplayerscripts' in path_str or 'client' in path_str:
            return 'LocalScript'
        else:
            return 'ModuleScript'

def setup_project_directory(project_name):
    """Configura la estructura de directorios para un proyecto"""
    project_dir = Path(PROJECTS_DIR) / project_name
    
    # Crear directorios principales
    dirs_to_create = [
        'ServerScriptService',
        'ReplicatedStorage',
        'StarterPlayer/StarterPlayerScripts',
        'StarterPack',
        'Workspace'
    ]
    
    for dir_path in dirs_to_create:
        full_path = project_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
    
    return project_dir

def start_file_watcher(project_name):
    """Inicia el observador de archivos para un proyecto"""
    project_dir = setup_project_directory(project_name)
    
    if project_name in projects:
        # Detener observador anterior si existe
        projects[project_name]['observer'].stop()
    
    # Crear nuevo observador
    event_handler = ProjectFileHandler(project_name)
    observer = Observer()
    observer.schedule(event_handler, str(project_dir), recursive=True)
    observer.start()
    
    projects[project_name] = {
        'observer': observer,
        'handler': event_handler,
        'directory': project_dir
    }
    
    print(f"File watcher started for project: {project_name}")
    return project_dir

@app.route('/status', methods=['GET'])
def get_status():
    """Endpoint para verificar estado del servidor"""
    return jsonify({
        'status': 'ok',
        'timestamp': time.time(),
        'projects': list(projects.keys())
    })

@app.route('/update-script', methods=['POST'])
def update_script():
    """Recibe actualizaciones de scripts desde Roblox"""
    try:
        data = request.get_json()
        
        project_name = data.get('project', 'DefaultProject')
        script_name = data.get('name')
        script_path = data.get('path')
        script_type = data.get('type')
        script_source = data.get('source', '')
        
        # Configurar proyecto si no existe
        if project_name not in projects:
            start_file_watcher(project_name)
        
        project_dir = projects[project_name]['directory']
        
        # Convertir path de Roblox a path del sistema
        file_path = project_dir / f"{script_path}.lua"
        
        # Crear directorios si no existen
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escribir archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(script_source)
        
        print(f"Script saved: {script_path} in {project_name}")
        
        return jsonify({
            'status': 'success',
            'message': f'Script {script_name} updated successfully'
        })
        
    except Exception as e:
        print(f"Error updating script: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/get-updates', methods=['GET'])
def get_updates():
    """Devuelve actualizaciones pendientes para Roblox"""
    try:
        project_name = request.args.get('project', 'DefaultProject')
        since_timestamp = float(request.args.get('since', 0))
        
        updates = []
        
        if project_name in file_updates:
            # Filtrar actualizaciones más recientes que el timestamp
            for update in file_updates[project_name]:
                if update['timestamp'] > since_timestamp:
                    updates.append(update)
            
            # Limpiar actualizaciones ya enviadas
            file_updates[project_name] = [
                u for u in file_updates[project_name] 
                if u['timestamp'] > since_timestamp
            ]
        
        return jsonify({
            'status': 'success',
            'updates': updates,
            'timestamp': time.time()
        })
        
    except Exception as e:
        print(f"Error getting updates: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/list-projects', methods=['GET'])
def list_projects():
    """Lista todos los proyectos disponibles"""
    try:
        projects_list = []
        projects_dir = Path(PROJECTS_DIR)
        
        if projects_dir.exists():
            for project_dir in projects_dir.iterdir():
                if project_dir.is_dir():
                    projects_list.append({
                        'name': project_dir.name,
                        'path': str(project_dir),
                        'active': project_dir.name in projects
                    })
        
        return jsonify({
            'status': 'success',
            'projects': projects_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/create-project', methods=['POST'])
def create_project():
    """Crea un nuevo proyecto"""
    try:
        data = request.get_json()
        project_name = data.get('name')
        
        if not project_name:
            return jsonify({
                'status': 'error',
                'message': 'Project name is required'
            }), 400
        
        project_dir = start_file_watcher(project_name)
        
        return jsonify({
            'status': 'success',
            'message': f'Project {project_name} created successfully',
            'path': str(project_dir)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def cleanup_on_exit():
    """Limpia recursos al cerrar el servidor"""
    print("Stopping file watchers...")
    for project_name, project_data in projects.items():
        try:
            project_data['observer'].stop()
            project_data['observer'].join()
        except:
            pass

def main():
    """Función principal para iniciar el servidor de sincronización"""
    print(f"Starting Roblox-IDE Sync Server on port {SYNC_PORT}")
    print(f"Projects directory: {os.path.abspath(PROJECTS_DIR)}")
    
    # Crear directorio de proyectos si no existe
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    
    # Iniciar servidor Flask
    app.run(host='0.0.0.0', port=SYNC_PORT, debug=DEBUG_MODE)

if __name__ == '__main__':
    main()