import os
import shutil
from pathlib import Path
from core.security import SecurityCore

class EditorsCleaner:
    def __init__(self):
        appdata_roaming = Path(os.environ.get('APPDATA', ''))
        
        # Diccionario contenedor de rutas objetivo por editor
        self.editors = {
            "vscode": appdata_roaming / "Code",
            "trae": appdata_roaming / "trae",
            "cursor": appdata_roaming / "Cursor"
        }
        
        # Subcarpetas estrictas de basura que podemos borrar de un editor
        self.target_subfolders = [
            Path("User") / "workspaceStorage",
            Path("Crashpad"),
            Path("CachedExtensionVSIXs"),
            Path("Code Cache")
        ]

    def get_sizes(self) -> dict:
        """Calcula el tamaño retenido por los editores de código instalados"""
        sizes = {"vscode": 0.0, "trae": 0.0, "cursor": 0.0, "total": 0.0, "paths_found": []}
        
        for editor_name, editor_path in self.editors.items():
            if editor_path.exists():
                for subfolder in self.target_subfolders:
                    target_path = editor_path / subfolder
                    if target_path.exists() and SecurityCore.is_path_safe(target_path):
                        size = self._get_dir_size(target_path)
                        sizes[editor_name] += size
                        if size > 0:
                            sizes["paths_found"].append(f"[{editor_name}] {target_path}")
                        
        sizes["total"] = round(sum([sizes["vscode"], sizes["trae"], sizes["cursor"]]), 2)
        return sizes

    def clean(self) -> dict:
        """Borra exactamente las subcarpetas autorizadas de cada editor"""
        results = {"success": True, "failed_paths": []}
        
        for editor_name, editor_path in self.editors.items():
            if editor_path.exists():
                for subfolder in self.target_subfolders:
                    target_path = editor_path / subfolder
                    if target_path.exists() and SecurityCore.is_path_safe(target_path):
                        try:
                            # Remueve y recrea la carpeta vacia para evitar crashes del editor
                            shutil.rmtree(target_path, ignore_errors=True)
                            os.makedirs(target_path, exist_ok=True)
                        except Exception:
                            results["success"] = False
                            results["failed_paths"].append(str(target_path))
                            
        return results

    def _get_dir_size(self, start_path: Path) -> float:
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(start_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except Exception:
            pass
        return round(total_size / (1024 * 1024), 2)
