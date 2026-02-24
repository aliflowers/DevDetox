# Documentación de Módulo: Editors Cache Cleaner (editors_cleaner.py)

## 📌 Objetivo del Módulo
Editores modernos construidos sobre Electron (como VS Code, Cursor y Trae) son célebres por acumular gigabytes de historiales de texto, indexación local e instaladores obsoletos en la carpeta `AppData/Roaming`. El objetivo es borrar estos registros históricos y volcados de fallos sin corromper la configuración UI del editor, las teclas sincronizadas (Keybindings) ni las extensiones instaladas.

## ⚙️ Árbol de Rutas Atacadas (White-list Validation)
El módulo rastrea de manera dinámica 3 posibles editores: `Code`, `trae`, y `Cursor`.
En cada uno de ellos ataca estrictamente 4 subcarpetas muertas:
1. `.../User/workspaceStorage`: Bases de datos SQLite que indexan proyectos que no abres hace años.
2. `.../Crashpad`: Reportes `.dmp` que el editor generó cuando se congeló, para enviarlos (o no) a telemetría.
3. `.../CachedExtensionVSIXs`: Los instaladores `.vsix` empaquetados pesados de extensiones que ya instalaste y no necesitan estar ahí.
4. `.../Code Cache`: Caché V8 engine del propio visor de Electron.

## 🛡️ Algoritmo Heurístico y Flujo Defensivo
1. **Borrado y Restauración Quirúrgica:** Borrar una carpeta como `workspaceStorage` de raíz mientras VS Code está abierto puede causar pérdida de autoguardado. El módulo emplea `shutil.rmtree` seguido inmediatamente de `os.makedirs`. Re-crea la carpeta vacía en milisegundos para que el editor no detecte el cambio de estructura.
2. **Path Scope Lock:** Sólo se ingresa a carpetas explícitas, bloqueando cualquier iteración destructiva en `User/Settings.json` o la carpeta superior de Extensiones de la que dependen tus plugins diarios.
