# Documentación de Módulo: Node & Web Managers (npm_cleaner.py)

## 📌 Objetivo del Módulo
Detectar y purificar las cachés globales de paquetes JavaScript creadas por gestores como `npm` (Node Package Manager) y `pnpm`. Estas herramientas suelen almacenar tarballs y versiones obsoletas de todas las dependencias jamás descargadas por el usuario, ocupando múltiples gigabytes de manera inactiva.

## ⚙️ Árbol de Rutas Atacadas (White-list Validation)
El módulo tiene acceso estricto a las siguientes rutas del usuario (previamente sanitizadas vía `%LOCALAPPDATA%`):
1. `C:\Users\[User]\AppData\Local\npm-cache`
2. `C:\Users\[User]\AppData\Local\pnpm\store\v3`

## 🛡️ Algoritmo Heurístico y Flujo Defensivo
1. **Verificación Estricta:** Antes de contabilizar un solo byte, `NodeCleaner.get_sizes()` pide autorización a `SecurityCore.is_path_safe()` para comprobar que las rutas apuntan a donde dicen apuntar (evitando symlinks maliciosos).
2. **Purga Grácil vs Agresiva:**
   - La función de borrado ejecuta en *primer nivel* los recoletores de basura oficiales de los propios lenguajes: `npm cache clean --force` y `pnpm store prune`. Esto asegura que los registros internos de Node no se rompan.
   - En *segundo nivel*, el módulo fuerza la eliminación física (`shutil.rmtree`) si la IA detecta remanentes persistentes (zombis lockeados).
3. **Sandbox Preservado:** NUNCA se tocarán archivos en el directorio del proyecto del desarrollador (`node_modules` locales), preservando en un 100% el progreso del código fuente actual. Sólo actúa sobre cachés globales.
