# Documentación de Módulo: Universal OS Browsers Cleaner (browsers_cleaner.py)

## 📌 Objetivo del Módulo
Google Chrome y los principales navegadores del mercado basados en el ecosistema mundial Chromium (Edge, Brave, Vivaldi, Opera y Perplexity) comparten una arquitectura base para guardar datos en carpetas `User Data`. Por otro lado, Firefox sigue una filosofía Mozilla completamente distinta.
Los desarrolladores no siempre tienen un único navegador o un solo perfil en Chrome, sino múltiples distribuidos ("Profile 1", "Work Profile").
El limpiador tradicional del propio navegador o de Windows suele centrarse en el perfil predeterminado o en la sesión activa exclusivamente.
Este módulo provee una solución de **limpieza concurrente, transversal y agnóstica.** Escanea todo el sistema operativo e indexa de forma dinámica las cachés gráficas y cachés de código pre-compilado de código de **[N] Perfiles Simultáneamente** a lo largo de **Múltiples Marcas de Navegadores y Motores (Chromium + Gecko de Mozilla)** sin desloguear ninguna cuenta.

## ⚙️ Árbol de Rutas Atacadas (White-list Validation)
El módulo tiene una arquitectura dividida en 2 flujos dependiendo del motor:

**Motor Chromium (Ej: Perplexity, Brave, Chrome):**
Investiga cuántas carpetas `Profile *`, `Guest Profile` y `Default` existen. Y ataca las subcarpetas de caché pesadas como `Code Cache`, `Cache_Data`, `Service Worker/CacheStorage` y `GPUCache`.

**Motor Mozilla (Firefox):**
Navega dinámicamente sobre la ruta `AppData/Local/Mozilla/Firefox/Profiles`. Al detectar perfiles crípticos (Ej. `xf45gds.default-release`), entra directo a cazar las subcarpetas infladas: `cache2` y `startupCache`.

## 🛡️ Algoritmo Heurístico y Flujo Defensivo
1. **Iterador de "User Data":** `_get_profiles()` es una máquina de estado segura que ignora configuraciones crudas y se enfoca solo en carpetas de sesión, limitando la visibilidad del módulo exclusivamente a perfiles activos.
2. **Blindaje contra Data Loss:** El módulo tiene un "Hardcode White List" `self.cache_targets`. No hay forma lógica ni condicional de inyectar variables en las rutas atacadas; el bot JAMÁS podrá borrar los archivos hermanos de los perfiles como `History` (Bases de datos SQLite), `Login Data` (Contraseñas), ni `Cookies`, asegurando un nivel de riesgo cero para el usuario.
3. **Bloqueo Silencioso:** Se emplea `ignore_errors=True`. Si Chrome está abierto y protegiendo ciertos archivos GPU en memoria por Windows I/O Locks, el script los salta limpiamente en lugar de colapsarse y fallar.
