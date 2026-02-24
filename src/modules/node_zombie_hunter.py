import os
import shutil
import time
from pathlib import Path
from core.security import SecurityCore

class NodeZombieHunter:
    def __init__(self):
        # 3 meses en segundos por defecto para considerar un repositorio "Zombi" (Muerto y Abandonado)
        self.zombie_threshold_seconds = 90 * 24 * 60 * 60 
        
        # Donde buscar: El hunter escanea el directorio principal de Usuario, Documentos, Desktop, etc.
        # Evitamos buscar en C:\ plano y C:\Windows para no perder tiempo computacional.
        user_profile = Path(os.environ.get('USERPROFILE', ''))
        self.search_roots = [
            user_profile / "Documents",
            user_profile / "Desktop",
            user_profile / "Downloads",
            Path("C:/Proyectos") # Ruta especifica del usuario actual reportada
        ]

    def scan_for_zombies(self, months_inactive: int = 3) -> dict:
        """
        Escanea recursivamente los directorios raíz definidos buscando carpetas 'node_modules'
        que pertenezcan a proyectos modificados por última vez hace X meses.
        """
        self.zombie_threshold_seconds = months_inactive * 30 * 24 * 60 * 60
        current_time = time.time()
        
        results = {"zombies_found": [], "total_zombi_bytes": 0}
        
        for root_path in self.search_roots:
            if not root_path.exists() or not SecurityCore.is_path_safe(root_path):
                continue
                
            for dirpath, dirnames, _ in os.walk(root_path):
                # Evitamos entrar a buscar node_modules DENTRO de un node_modules
                if 'node_modules' in dirpath:
                    continue
                    
                if 'node_modules' in dirnames:
                    full_nm_path = Path(dirpath) / 'node_modules'
                    
                    # Para saber la edad del proyecto, revisamos la fecha de modificacion del package.json
                    # o del propio folder padre, no del node_modules en si.
                    project_root = Path(dirpath)
                    package_json = project_root / 'package.json'
                    
                    try:
                        time_ref = os.path.getmtime(package_json) if package_json.exists() else os.path.getmtime(project_root)
                        age_seconds = current_time - time_ref
                        
                        if age_seconds >= self.zombie_threshold_seconds:
                            # ¡Zombi detectado!
                            zombi_size = self._get_dir_size(full_nm_path)
                            results["zombies_found"].append({
                                "project_path": str(project_root),
                                "node_modules_path": str(full_nm_path),
                                "age_days": int(age_seconds / (24 * 60 * 60)),
                                "size_mb": round(zombi_size / (1024 * 1024), 2)
                            })
                            results["total_zombi_bytes"] += zombi_size
                    except Exception:
                        pass
                        
        results["total_mb"] = round(results["total_zombi_bytes"] / (1024 * 1024), 2)
        return results

    def kill_zombies(self, target_node_modules: list) -> dict:
        """
        Borra físicamente del disco las carpetas node_modules especificadas en la lista.
        """
        results = {"success": True, "failed_paths": [], "freed_mb": 0.0}
        
        for nm_path_str in target_node_modules:
            nm_path = Path(nm_path_str)
            if nm_path.exists() and nm_path.name == 'node_modules' and SecurityCore.is_path_safe(nm_path):
                try:
                    size_before = self._get_dir_size(nm_path)
                    shutil.rmtree(nm_path, ignore_errors=True)
                    results["freed_mb"] += round(size_before / (1024 * 1024), 2)
                except Exception:
                    results["success"] = False
                    results["failed_paths"].append(str(nm_path))
                    
        return results

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
