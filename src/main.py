import sys
from pathlib import Path

# Añadir el propio directorio src al PATH de Python para importar modulos facil
sys.path.append(str(Path(__file__).parent.resolve()))

from core.security import SecurityCore
from gui.app import DevDetoxApp

def main():
    """
    Punto de entrada de DevDetox. 
    Verifica seguridad de permisos antes de dibujar la ventana gráfica.
    """
    is_admin = SecurityCore.is_admin()
    print(f"[*] Iniciando DevDetox. Permisos Admin: {is_admin}")

    # Inicializar la interfaz gráfica de CustomTkinter
    app = DevDetoxApp(is_admin=is_admin)

    # Inyectar la logica de elevacion del core al boton de la GUI
    app.elevation_callback = SecurityCore.run_as_admin

    # Lanzar el bucle infinito de Ventana de Windows
    app.mainloop()

if __name__ == "__main__":
    main()
