import os
import ctypes
import sys
from pathlib import Path

class SecurityCore:
    """
    Motor Central de Seguridad para DevDetox.
    Asegura que las eliminaciones se hagan bajo white-listing y escalado de privilegios.
    """
    
    # White-list de rutas base autorizadas para ser tocadas por cualquier modulo
    # Bloquea inyecciones tipo 'C:\Windows'
    AUTHORIZED_PREFIXES = [
        str(Path(os.environ.get('APPDATA', ''))),          # Roaming
        str(Path(os.environ.get('LOCALAPPDATA', ''))),     # Local
        str(Path(os.environ.get('USERPROFILE', ''))),      # Home (ej: .gradle, .gemini)
        str(Path(os.environ.get('PROGRAMDATA', '')))       # ProgramData
    ]

    @staticmethod
    def is_admin() -> bool:
        """Chequea si el proceso actual tiene privilegios elevados (UAC)"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    @staticmethod
    def run_as_admin():
        """Relanza el script actual solicitando el prompt de Administrador UAC de Windows"""
        if not SecurityCore.is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit()

    @staticmethod
    def is_path_safe(target_path: str | Path) -> bool:
        """
        [Path Traversal Protection]
        Ningun módulo puede pedir borrar una ruta si no está en la 'White-list'.
        """
        try:
            target = Path(target_path).resolve() # Resuelve '..'
            
            # Impedir tocar el disco C plano o carpetas raiz críticas
            if len(target.parts) <= 2:
                return False
                
            for prefix in SecurityCore.AUTHORIZED_PREFIXES:
                if not prefix: 
                    continue
                safe_prefix = Path(prefix).resolve()
                if str(target).startswith(str(safe_prefix)):
                    return True
            return False
            
        except Exception:
            return False

    @staticmethod
    def get_windows_temp_path() -> Path:
        """
        Ruta segura mapeada en memoria.
        Las únicas excepciones hardcodeadas permitidas.
        """
        return Path("C:\\Windows\\Temp")

# Pruebas de seguridad si se ejecuta el módulo directo
if __name__ == "__main__":
    print("[DEV] Chequeo Admin:", SecurityCore.is_admin())
    print("[DEV] Test Seguridad Path ('C:\\Windows'):", SecurityCore.is_path_safe("C:\\Windows"))
    print("[DEV] Test Seguridad Path APPDATA:", SecurityCore.is_path_safe(os.environ.get('APPDATA')))
