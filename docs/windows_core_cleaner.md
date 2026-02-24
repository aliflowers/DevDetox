# Documentación de Módulo: Windows Core Cleaner (windows_core_cleaner.py)

## 📌 Objetivo del Módulo
Windows es notorio por acumular cientos de miles de pequeños archivos en sus directorios de paso (Temporales), al igual que su carpeta de aceleración de aplicaciones (`Prefetch`). Muchas herramientas de instalación dejan residuos allí por años. Adicionalmente, los desarrolladores suelen olvidar vaciar la Papelera de Reciclaje, conservando gigabytes muertos.
Este módulo provee la interfaz para exterminar de manera segura pero agresiva la basura del sistema inferior a nivel de Kernel y Shell.

## ⚙️ Árbol de Rutas Atacadas (White-list Validation)
1. **User Temp** (`%LOCALAPPDATA%\Temp`): Archivos creados momentáneamente por apps del perfil de usuario actual.
2. **System Root Temp** (`C:\Windows\Temp`): Archivos generados directamente por procesos en el ring del Sistema (Requiere UAC Admin).
3. **Prefetch** (`C:\Windows\Prefetch`): Aceleradores binarios. Se ensucia rápidamente con apps que ya no existen. (Requiere UAC Admin).
4. **Recycle Bin**: Inyectado por PowerShell de forma universal a todas las unidades montadas en la máquina.

## 🛡️ Algoritmo Heurístico y Flujo Defensivo
1. **Preservación de Estructura Padre:** Algunos virus o scripts mal hechos borran `C:\Windows\Temp` en lugar de borrar *el contenido* de Temp. Esto rompe la matriz de ACL de Windows de por vida. El módulo DevDetox hace un `os.listdir()` iterativo de forma tal que solo destruye los hijos inyectados temporalmente y preserva las carpetas del sistema sagradas y su configuración de permisos.
2. **Tolerancia a Bloqueos (Lock Tolerance):** Es estadísticamente imposible borrar un directorio `Temp` por completo porque Windows siempre tiene algo recién abierto en memoria (I/O). El ciclo está envidiado en sub-excepciones con silenciadores de error en `os.remove` para borrar el 99% y dejar intacto el 1% estrictamente en uso, evadiendo fallos de I/O en la app.
3. **Vaciado Com-Shell Seguro:** Para la Papelera, en vez de atacar `$Recycle.Bin` recursivamente con Python (Lo cual a menudo causa violaciones de acceso de System), se delega el comando al kernel de PowerShell `Clear-RecycleBin`.
