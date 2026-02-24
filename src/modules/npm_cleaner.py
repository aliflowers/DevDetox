import os
import shutil
from pathlib import Path
from core.security import SecurityCore
from core.cmd_engine import CommandEngine

class NodeCleaner:
    def __init__(self):
        self.npm_cache = Path(os.environ.get('LOCALAPPDATA', '')) / 'npm-cache'
        self.pnpm_store = Path(os.environ.get('LOCALAPPDATA', '')) / 'pnpm' / 'store' / 'v3'

    def get_sizes(self) -> dict:
        """Calcula el tamaño (en MB) de las cachés de NPM y PNPM simulando su borrado"""
        sizes = {"npm": 0.0, "pnpm": 0.0, "total": 0.0, "paths_found": []}
        
        # Tamaño NPM
        if self.npm_cache.exists() and SecurityCore.is_path_safe(self.npm_cache):
            sizes["npm"] = self._get_dir_size(self.npm_cache)
            if sizes["npm"] > 0: sizes["paths_found"].append(f"[NPM Cache] {self.npm_cache}")
            
        # Tamaño PNPM
        if self.pnpm_store.exists() and SecurityCore.is_path_safe(self.pnpm_store):
            sizes["pnpm"] = self._get_dir_size(self.pnpm_store)
            if sizes["pnpm"] > 0: sizes["paths_found"].append(f"[PNPM Store] {self.pnpm_store}")
            
        sizes["total"] = round(sizes["npm"] + sizes["pnpm"], 2)
        return sizes

    def clean(self) -> bool:
        """Ejecuta los comandos de purga nativos y borra los remanentes seguros."""
        success = True
        
        # Intentar comando nativo primero
        CommandEngine.run_ps("npm cache clean --force")
        CommandEngine.run_ps("pnpm store prune")
        
        # Purga forzosa bajo white-list
        if self.npm_cache.exists() and SecurityCore.is_path_safe(self.npm_cache):
            try:
                shutil.rmtree(self.npm_cache, ignore_errors=True)
            except Exception:
                success = False
                
        if self.pnpm_store.exists() and SecurityCore.is_path_safe(self.pnpm_store):
            try:
                shutil.rmtree(self.pnpm_store, ignore_errors=True)
            except Exception:
                success = False
                
        return success

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
        # Retornamos en Megabytes
        return round(total_size / (1024 * 1024), 2)
