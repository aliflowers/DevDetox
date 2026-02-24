# Documentación de Módulo: Heuristic Deep Uninstaller (deep_uninstaller.py)

## 📌 Objetivo del Módulo
La desinstalación predeterminada de Windows ("Panel de Control > Agregar o Quitar Programas") a menudo ejecuta scripts rotos que dejan miles de archivos de configuración persistentes o cachés residuales en los directorios de datos de la máquina (`AppData` y `ProgramData`). El objetivo de este módulo es ser el **Revo Uninstaller / IObit Uninstaller** de terminal.

Alimenta la interfaz gráfica interceptando las llamadas al kernel del sistema para obtener dos cosas:
1. Una lista transparente de todo el software instalado.
2. Un destructor post-hoc (Caza_Leftovers) que averigua heurísticamente qué carpetas sobrevivieron a la desinstalación y las aniquila.

## ⚙️ Arquitectura de Caza (Registry y Heurística)
El motor de desinstalaciones es 100% nativo mediante WinReg (`winreg`). Escanea tres puntos ciegos de Windows:
1. `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall` (Soft. 64-bit Sistema)
2. `HKLM\SOFTWARE\WOW6432Node\Microsoft\...` (Soft. 32-bit Legacy Sistema)
3. `HKCU\Software\...` (Soft. Instalado únicamente para el perfil del desarrollador)

El motor heurístico caza basura post-instalación inyectándose en:
- `%APPDATA%` (Roaming)
- `%LOCALAPPDATA%` (Local)
- `%PROGRAMDATA%` (Archivos maestros del sistema C:/ProgramData)

## 🛡️ Algoritmo Heurístico y Flujo Defensivo
1. **Delegación Oficial de la Instalación Secundaria:** DevDetox ***manda a llamar los desinstaladores originales*** (`UninstallString` del autor del Software) en primer lugar para que remuevan los Componentes de Windows y binarios pesados de forma natural, antes de meter mano a los gigabytes residuales escondidos.
2. **Evaluación de Daños Quirúrgica (`hunt_leftovers`):** En lugar de hacer un Regex general y borrar al azar, la IA extrae las "Roots" puras del nombre del autor del programa `(Ej: "Docker Desktop" -> ["Docker", "Desktop"])` y asume que cualquier subcarpeta hallada en *ProgramData* o *AppData* que coincida con dichas palabras después de finalizada la desinstalación original, es remanente ilícito ("Orphan Folder").
3. **Double Blind Sandbox (Zero Trust):** Por diseño, el Heurístico *nunca* borra de inmediato. La función de cacería solo devuelve una lista temporal segura de las supuestas carpetas infectadas a la UI. Es obligación matemática de la Aplicación y del motor Central `SecurityCore` confirmar una vez más el `is_path_safe` antes de inyectarlo recursivamente al `rmtree`.
