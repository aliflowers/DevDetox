import subprocess
from typing import Tuple

class CommandEngine:
    """Motor de ejecución de consola para DevDetox."""
    
    @staticmethod
    def run_ps(command: str) -> Tuple[bool, str]:
        """Ejecuta un comando de PowerShell silenciosamente y devuelve status/salida."""
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
