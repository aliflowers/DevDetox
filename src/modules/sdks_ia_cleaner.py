import os
import shutil
from pathlib import Path
from core.security import SecurityCore

class SDKsIACleaner:
    def __init__(self):
        user_profile = Path(os.environ.get('USERPROFILE', ''))
        
        # Diccionario de subcarpetas basura agrupadas por Software / Tecnología
        self.targets = {
            "Gradle": [
                user_profile / ".gradle" / "caches",
                user_profile / ".gradle" / "daemon"
            ],
            "Android SDK": [
                user_profile / ".android" / "cache"
            ],
            "Cursor AI": [
                user_profile / ".cursor" / "telemetry-cache"
            ],
            "Gemini (Antigravity)": [
                # Rutas probables basadas en telemetría de asistentes en disco
                user_profile / ".gemini" / "cache",
                user_profile / ".gemini" / "logs",
                user_profile / ".gemini" / "antigravity" / "telemetry"
            ],
            "Yarn": [
                user_profile / ".yarn" / "cache"
            ]
        }

    def get_sizes(self) -> dict:
        """Calcula el tamaño (MB) retenido por Caches de SDKs locales y logs de IAs."""
        sizes_by_app = {name: 0.0 for name in self.targets.keys()}
        total_size = 0.0
        paths_found = []
        
        for app_name, path_list in self.targets.items():
            app_size = 0.0
            for target_path in path_list:
                if target_path.exists() and SecurityCore.is_path_safe(target_path):
                    size = self._get_dir_size(target_path)
                    app_size += size
                    if size > 0:
                        paths_found.append(f"[{app_name}] {target_path}")
            
            sizes_by_app[app_name] = app_size
            total_size += app_size
            
        return {
            "details": sizes_by_app,
            "total_size_mb": round(total_size, 2),
            "paths_found": paths_found
        }

    def clean(self) -> dict:
        """Borra recursivamente y de forma segura las subcarpetas de telemetria y cache"""
        results = {"success": True, "failed_paths": []}
        
        for app_name, path_list in self.targets.items():
            for target_path in path_list:
                if target_path.exists() and SecurityCore.is_path_safe(target_path):
                    try:
                        # Recreación atómica para evitar colgar procesos locales (ej daemon de gradle)
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
