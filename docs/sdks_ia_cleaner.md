# Documentación de Módulo: Mobile SDKs & Assistant AI Logs (sdks_ia_cleaner.py)

## 📌 Objetivo del Módulo
Los entornos modernos de desarrollo móvil (Android, React Native) y el surgimiento de nuevos editores de Código basados en Inteligencia Artificial (Cursor, Gemini CLI, Copilot) han traído consigo un problema masivo: el secuestro silencioso del directorio base del usuario `C:\Users\[TuNombre]`. 
Este módulo apunta específicamente a las carpetas globales ocultas (prefijadas con puntos `.`) que acumulan gigabytes sin que Windows o los discos duros puedan mapearlas fácilmente.

## ⚙️ Árbol de Rutas Atacadas (White-list Validation)
El módulo iterará sobre el ecosistema nativo invisible de las raíces `.app`:
1. **Gradle / Java / Android:** Ataca `~/.gradle/caches` y `~/.gradle/daemon`. Estas son copias descargadas completas de librerías Java y demonios de Memoria RAM que no desaparecen ni con `clean build`. También ataca la subcarpeta `~/.android/cache`.
2. **Yarn:** El gestor de paquetes Yarn de JavaScript es notorio por acumular basura en `~/.yarn/cache`.
3. **Cursor AI:** El editor superpone caché de comandos y telemetría algorítmica pesada en `~/.cursor/telemetry-cache`.
4. **Google Gemini (Antigravity):** Rastrea y purga logs de conversación y telemetría inútiles subyacentes en el disco, usualmente alojados en `~/.gemini/cache` y `~/.gemini/logs`.

## 🛡️ Algoritmo Heurístico y Flujo Defensivo
1. **Borrado Seguro por Átomos:** Al igual que en Módulos de VSCode, herramientas como Gradle Server siempre mantienen demonios en background de Windows (`daemon.exe`). El script usa un ciclo destructivo con `ignore_errors=True` apoyado por una recreación instantánea de los directorios (`os.makedirs`). Esto permite borrar el 98% de la caché desconectada, perdonándole la vida al 2% de archivos que están ejecutándose para evitar "Kernell Panics" e interrupciones del trabajo actual del desarrollador.
2. **Sandboxing Local:** No se tocan archivos de configuración primordiales de las IAs como tokens Oauth2 o sesiones SSH `.ssh`. El foco del código es **única y estrictamente la subcarpeta final etiquetada como caché o log.**
