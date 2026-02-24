import os
import shutil
from pathlib import Path
from core.security import SecurityCore

class BrowsersCleaner:
    def __init__(self):
        local_appdata = Path(os.environ.get('LOCALAPPDATA', ''))
        roaming_appdata = Path(os.environ.get('APPDATA', ''))
        
        # Diccionario Universal Chromium (Rutas base donde residen los perfiles)
        self.browser_data_paths = {
            "Chrome": local_appdata / 'Google' / 'Chrome' / 'User Data',
            "Edge": local_appdata / 'Microsoft' / 'Edge' / 'User Data',
            "Brave": local_appdata / 'BraveSoftware' / 'Brave-Browser' / 'User Data',
            "Vivaldi": local_appdata / 'Vivaldi' / 'User Data',
            "Opera": roaming_appdata / 'Opera Software' / 'Opera Stable',
            "Opera GX": roaming_appdata / 'Opera Software' / 'Opera GX Stable',
            "Perplexity": local_appdata / 'Perplexity' / 'Comet' / 'User Data' 
        }
        
        # Patrones estrictos de Cache a limpiar *dentro* de cada perfil Chromium
        self.chromium_cache_targets = [
            Path("Cache") / "Cache_Data",
            Path("Code Cache"),
            Path("GPUCache"),
            Path("Service Worker") / "CacheStorage",
            Path("Media Cache")
        ]

        # Configuración exclusiva para Mozilla Firefox (Arquitectura diferente a Chromium)
        self.firefox_profiles_path = local_appdata / 'Mozilla' / 'Firefox' / 'Profiles'
        self.firefox_cache_targets = [
            Path("cache2"),
            Path("startupCache")
        ]

    def _get_chromium_profiles(self) -> dict:
        """Devuelve un diccionario clasificando perfiles válidos por nombre de navegador Chromium"""
        active_profiles = {name: [] for name in self.browser_data_paths.keys()}
        
        for browser_name, user_data_path in self.browser_data_paths.items():
            if not user_data_path.exists() or not SecurityCore.is_path_safe(user_data_path):
                continue
                
            try:
                if "Opera" in browser_name:
                    active_profiles[browser_name].append(user_data_path)
                else:
                    for item in os.listdir(user_data_path):
                        item_path = user_data_path / item
                        if item_path.is_dir() and (item == "Default" or item.startswith("Profile") or item == "Guest Profile"):
                            active_profiles[browser_name].append(item_path)
            except Exception:
                pass
                
        return active_profiles

    def _get_firefox_profiles(self) -> list:
        """Devuelve una lista de todos los perfiles instalados de Firefox (Ej: randomstring.default-release)"""
        profiles = []
        if self.firefox_profiles_path.exists() and SecurityCore.is_path_safe(self.firefox_profiles_path):
            try:
                for item in os.listdir(self.firefox_profiles_path):
                    item_path = self.firefox_profiles_path / item
                    if item_path.is_dir():
                        profiles.append(item_path)
            except Exception:
                pass
        return profiles

    def get_sizes(self) -> dict:
        """Calcula el peso total ocupado cruzando todos los navegadores (Chromium + Mozilla)"""
        total_size = 0.0
        details = {name: 0.0 for name in self.browser_data_paths.keys()}
        details["Firefox"] = 0.0
        paths_found = []
        
        # 1. Medir Ecosistema Chromium
        profiles_by_chromium = self._get_chromium_profiles()
        for browser_name, profiles in profiles_by_chromium.items():
            browser_size = 0.0
            for profile_path in profiles:
                for target in self.chromium_cache_targets:
                    full_target = profile_path / target
                    if full_target.exists() and SecurityCore.is_path_safe(full_target):
                        size = self._get_dir_size(full_target)
                        browser_size += size
                        if size > 0:
                            paths_found.append(f"[{browser_name}] {full_target}")
            details[browser_name] = browser_size
            total_size += browser_size

        # 2. Medir Mozilla Firefox
        firefox_size = 0.0
        for profile_path in self._get_firefox_profiles():
            for target in self.firefox_cache_targets:
                full_target = profile_path / target
                if full_target.exists() and SecurityCore.is_path_safe(full_target):
                    size = self._get_dir_size(full_target)
                    firefox_size += size
                    if size > 0:
                        paths_found.append(f"[Firefox] {full_target}")
        details["Firefox"] = firefox_size
        total_size += firefox_size
            
        return {
            "browser_details": details,
            "total_size_mb": round(total_size, 2),
            "paths_found": paths_found
        }

    def clean(self) -> dict:
        """Aniquila las subcarpetas de Cache de forma unificada (Chromium + Mozilla)"""
        results = {"success": True, "failed_paths": [], "cleared_browsers": 0}
        
        # 1. Limpiar Ecosistema Chromium
        profiles_by_chromium = self._get_chromium_profiles()
        for browser_name, profiles in profiles_by_chromium.items():
            browser_cleaned = False
            for profile_path in profiles:
                for target in self.chromium_cache_targets:
                    full_target = profile_path / target
                    if full_target.exists() and SecurityCore.is_path_safe(full_target):
                        try:
                            shutil.rmtree(full_target, ignore_errors=True)
                            os.makedirs(full_target, exist_ok=True)
                            browser_cleaned = True
                        except Exception:
                            results["success"] = False
                            results["failed_paths"].append(str(full_target))
            if browser_cleaned:
                results["cleared_browsers"] += 1

        # 2. Limpiar Mozilla Firefox
        firefox_cleaned = False
        for profile_path in self._get_firefox_profiles():
            for target in self.firefox_cache_targets:
                full_target = profile_path / target
                if full_target.exists() and SecurityCore.is_path_safe(full_target):
                    try:
                        shutil.rmtree(full_target, ignore_errors=True)
                        os.makedirs(full_target, exist_ok=True)
                        firefox_cleaned = True
                    except Exception:
                        results["success"] = False
                        results["failed_paths"].append(str(full_target))
        if firefox_cleaned:
            results["cleared_browsers"] += 1
                        
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
