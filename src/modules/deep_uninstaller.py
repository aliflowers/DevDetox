import os
import winreg
import shutil
import subprocess
from pathlib import Path
from core.security import SecurityCore
from core.cmd_engine import CommandEngine

class DeepUninstaller:
    def __init__(self):
        # Claves de Registro del sistema donde Windows guarda la lista de programas instalados
        self.uninstall_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        # Zonas donde los programas suelen dejar basura después de desinstalarse
        self.roaming = Path(os.environ.get('APPDATA', ''))
        self.local = Path(os.environ.get('LOCALAPPDATA', ''))
        self.program_data = Path(os.environ.get('PROGRAMDATA', 'C:/ProgramData'))

    def get_installed_software(self) -> list:
        """Lee el Registro de Windows y devuelve una lista de diccionarios con el software instalado y sus strings de desinstalacion."""
        software_list = []
        
        for root_key, sub_key in self.uninstall_keys:
            try:
                # Abrimos la llave principal de desinstalacion
                key = winreg.OpenKey(root_key, sub_key)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        # Iteramos sobre cada sub-llave (cada programa)
                        sub_key_name = winreg.EnumKey(key, i)
                        sub_key_handle = winreg.OpenKey(key, sub_key_name)
                        
                        try:
                            # Sacamos el nombre legible y el comando silencioso de desinstalacion
                            display_name = winreg.QueryValueEx(sub_key_handle, "DisplayName")[0]
                            uninstall_string = winreg.QueryValueEx(sub_key_handle, "UninstallString")[0]
                            
                            # Filtramos actualizaciones del sistema y componentes menores sin nombre
                            if display_name and uninstall_string and not "KB" in display_name:
                                # Extracción de metadatos adicionales (UX visual)
                                try:
                                    estimated_size = winreg.QueryValueEx(sub_key_handle, "EstimatedSize")[0]
                                    size_raw = estimated_size
                                    size_mb = round(estimated_size / 1024, 2)
                                    size_str = f"{size_mb} MB" if size_mb < 1024 else f"{round(size_mb/1024, 2)} GB"
                                except OSError:
                                    size_str = "Desconocido"
                                    size_raw = 0

                                try:
                                    display_icon = winreg.QueryValueEx(sub_key_handle, "DisplayIcon")[0]
                                    # Limpiar la ruta, usualmente viene "ruta.exe,0"
                                    if "," in display_icon:
                                        display_icon = display_icon.split(",")[0].strip('"')
                                    else:
                                        display_icon = display_icon.strip(' "')
                                except OSError:
                                    display_icon = ""

                                try:
                                    install_date = winreg.QueryValueEx(sub_key_handle, "InstallDate")[0]
                                except OSError:
                                    install_date = "00000000"

                                software_list.append({
                                    "name": display_name,
                                    "uninstall_command": uninstall_string,
                                    "size": size_str,
                                    "size_raw": size_raw,
                                    "icon_path": display_icon,
                                    "install_date": install_date
                                })
                        except OSError:
                            pass # Ciertas llaves no tienen DisplayName
                        finally:
                            winreg.CloseKey(sub_key_handle)
                    except OSError:
                        pass
                winreg.CloseKey(key)
            except OSError:
                continue
                
        # Retornamos ordenado alfabeticamente para la interfaz grafica
        return sorted(software_list, key=lambda x: str(x.get("name")).lower())

    def run_official_uninstaller(self, uninstall_command: str) -> bool:
        """Invoca al desinstalador original del autor del programa."""
        # Requiere Administrador para desinstalar de HKLM
        if not SecurityCore.is_admin():
            return False
            
        try:
            # Separar el binario de los argumentos (ej: "msiexec.exe /X{GUID}")
            CommandEngine.run_ps(f"Start-Process -Wait -NoNewWindow -FilePath cmd.exe -ArgumentList '/c {uninstall_command}'")
            return True
        except Exception:
            return False

    def hunt_leftovers(self, software_name: str) -> dict:
        """
        Rastreador Heurístico Post-Desinstalación.
        Busca carpetas que coincidan con el nombre del software o desarrollador en directorios de datos.
        Devuelve el peso y una simulacion de lo que va a borrar antes de hacerlo.
        """
        results = {"found_bytes": 0, "target_folders": []}
        
        # Convertir nombre a una "raiz" limpia (Ej: "Google Chrome" -> ["Google", "Chrome"])
        keywords = [word for word in software_name.replace("-", " ").split() if len(word) > 2]
        if not keywords:
            return results
            
        search_paths = [self.roaming, self.local, self.program_data]
        
        for base_path in search_paths:
            if not base_path.exists(): continue
            
            try:
                for item in os.listdir(base_path):
                    item_path = base_path / item
                    # Verificación Heurística: Si la carpeta contiene alguna palabra clave principal del software
                    if item_path.is_dir():
                        match = False
                        for kw in keywords:
                            if kw.lower() in item.lower():
                                match = True
                                break
                        
                        if match and SecurityCore.is_path_safe(item_path):
                            results["target_folders"].append(item_path)
                            results["found_bytes"] += self._get_dir_size(item_path)
            except Exception:
                pass
                
        # Retornamos megabytes flotantes
        results["found_mb"] = round(results["found_bytes"] / (1024 * 1024), 2)
        return results

    def destroy_leftovers(self, target_folders_list: list) -> bool:
        """Fuerza la eliminacion de la lista de carpetas huerfanas encontradas por el cazador."""
        success = True
        for path in target_folders_list:
            if Path(path).exists() and SecurityCore.is_path_safe(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                except Exception:
                    success = False
        return success

    def _get_dir_size(self, start_path: Path) -> int:
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except Exception:
            pass
        return total_size
