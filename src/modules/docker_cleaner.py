import os
import shutil
import time
from pathlib import Path
from core.security import SecurityCore
from core.cmd_engine import CommandEngine

class DockerCleaner:
    def __init__(self):
        # La ruta típica del VHDX de Docker Desktop en WSL2
        self.wsl_docker_path = Path(os.environ.get('LOCALAPPDATA', '')) / 'Docker' / 'wsl' / 'disk' / 'docker_data.vhdx'
        
    def is_docker_installed(self) -> bool:
        """Verifica si el disco duro virtual de Docker WSL2 existe"""
        return self.wsl_docker_path.exists() and SecurityCore.is_path_safe(self.wsl_docker_path)

    def get_vhdx_size(self) -> float:
        """Devuelve el tamaño actual del disco virtual en GB"""
        if self.is_docker_installed():
            size_bytes = os.path.getsize(self.wsl_docker_path)
            return round(size_bytes / (1024 * 1024 * 1024), 2)
        return 0.0

    def compact_vhdx(self) -> bool:
        """
        Ejecuta la rutina letal de compactación.
        1. Apaga el subsistema de Windows para Linux (WSL).
        2. Genera un script temporal de diskpart.
        3. Ejecuta la compactación nativa para recuperar espacio vacío.
        """
        success = True
        if not self.is_docker_installed():
            return False

        try:
            # 1. Forzar el apagado seguro de WSL para liberar el candado del archivo
            CommandEngine.run_ps("wsl --shutdown")
            time.sleep(2) # Dar tiempo a que el servicio se detenga

            # 2. Escribir el script temporal de Diskpart en Windows Temp
            temp_script = SecurityCore.get_windows_temp_path() / "dock_compact.txt"
            with open(temp_script, "w") as f:
                f.write(f'select vdisk file="{self.wsl_docker_path}"\n')
                f.write('attach vdisk readonly\n')
                f.write('compact vdisk\n')
                f.write('detach vdisk\n')

            # 3. Ejecutar diskpart silenciosamente con el script generado
            # NOTA: Diskpart requiere permisos de Administrador nativos por defecto
            cmd_diskpart = f"diskpart /s {temp_script}"
            cmd_success, output = CommandEngine.run_ps(cmd_diskpart)

            if not cmd_success:
                success = False

            # Limpiar script residual
            if temp_script.exists():
                os.remove(temp_script)

        except Exception as e:
            print(f"[!] Error crítico en DockerCleaner: {e}")
            success = False

        return success
