import os
import shutil
from pathlib import Path
from core.security import SecurityCore
from core.cmd_engine import CommandEngine

class WindowsCoreCleaner:
    def __init__(self):
        # Temp local del usuario (%LOCALAPPDATA%\Temp)
        self.user_temp = Path(os.environ.get('TEMP', ''))
        
        # Temp maestro de Windows (C:\Windows\Temp)
        self.system_temp = SecurityCore.get_windows_temp_path()
        
        # Prefetch (Mejora el arranque, pero acumula basura de programas borrados)
        self.prefetch = Path(os.environ.get('WINDIR', 'C:/Windows')) / "Prefetch"

    def get_sizes(self) -> dict:
        """Calcula el peso combinado de las carpetas temporales principales y la Papelera de Windows"""
        sizes = {
            "user_temp": 0.0,
            "system_temp": 0.0,
            "prefetch": 0.0,
            "recycle_bin": 0.0,
            "total": 0.0,
            "paths_found": []
        }
        
        # 1. Temporales
        if self.user_temp.exists() and SecurityCore.is_path_safe(self.user_temp):
            sizes["user_temp"] = self._get_dir_size(self.user_temp)
            if sizes["user_temp"] > 0: sizes["paths_found"].append(f"[Temp Usuario] {self.user_temp}")
            
        if self.system_temp.exists() and SecurityCore.is_path_safe(self.system_temp):
            sizes["system_temp"] = self._get_dir_size(self.system_temp)
            if sizes["system_temp"] > 0: sizes["paths_found"].append(f"[Temp Sistema] {self.system_temp}")
            
        if self.prefetch.exists() and SecurityCore.is_path_safe(self.prefetch):
            # Prefetch usualmente requiere ADMIN para ser contada
            sizes["prefetch"] = self._get_dir_size(self.prefetch)
            if sizes["prefetch"] > 0: sizes["paths_found"].append(f"[Prefetch] {self.prefetch}")

        # 2. Papelera de Reciclaje (Estimación via Com Obj de Windows)
        try:
            # Reclama el tamaño de la papelera usando un objeto COM de Shell
            import win32com.client
            shell = win32com.client.Dispatch("Shell.Application")
            recycle_bin = shell.NameSpace(10) # 10 es el ID del Recycle Bin
            bin_size = 0
            for item in recycle_bin.Items():
                bin_size += item.Size
            sizes["recycle_bin"] = round(bin_size / (1024 * 1024), 2)
            if sizes["recycle_bin"] > 0: sizes["paths_found"].append("[Papelera de Reciclaje]")
        except Exception:
            # Fallback en caso de que pywin32 falle o falten privilegios
            pass
            
        sizes["total"] = sizes["user_temp"] + sizes["system_temp"] + sizes["prefetch"] + sizes["recycle_bin"]
        sizes["total"] = round(sizes["total"], 2)
        return sizes

    def clean(self) -> dict:
        """Fuerza la eliminación recursiva en subcarpetas de Temp, Prefetch y vaciado de Papelera"""
        results = {"success": True, "failed_paths": [], "recycle_bin_cleared": False}
        
        targets = [self.user_temp, self.system_temp, self.prefetch]
        
        for target_dir in targets:
            if target_dir.exists() and SecurityCore.is_path_safe(target_dir):
                # En lugar de borrar la carpeta TEMP (Peligroso), borramos el CONTENIDO
                for item in os.listdir(target_dir):
                    item_path = target_dir / item
                    try:
                        if item_path.is_dir():
                            shutil.rmtree(item_path, ignore_errors=True)
                        else:
                            os.remove(item_path)
                    except Exception:
                        results["success"] = False
                        if str(target_dir) not in results["failed_paths"]:
                            results["failed_paths"].append(str(target_dir))

        # Vaciar Papelera de reciclaje nativamente via PowerShell
        # Esto previene tener que adivinar las letras de las unidades de disco
        cmd_success, _ = CommandEngine.run_ps("Clear-RecycleBin -Force -ErrorAction SilentlyContinue")
        results["recycle_bin_cleared"] = cmd_success
        
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
