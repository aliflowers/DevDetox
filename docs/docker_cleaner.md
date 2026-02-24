# Documentación de Módulo: Docker VHDX Compact (docker_cleaner.py)

## 📌 Objetivo del Módulo
Docker Desktop en Windows no funciona igual que en Linux. En lugar de instalarse plano, secuestra una porción gigante de tu disco creando un Archivo de Disco Virtual (`.VHDX`). El problema estructural de Microsoft es que **el VHDX puede crecer dinámicamente, pero jamás se encoge por sí solo**, incluso si borras todas tus imágenes y contenedores.
Este módulo automatiza la técnica de administración de Storage para "Aplastarlo" y obligar a Windows a recuperar los Gigabytes en el aire (Espacio Muerto).

## ⚙️ Árbol de Rutas Atacadas (White-list Validation)
1. `C:\Users\[User]\AppData\Local\Docker\wsl\disk\docker_data.vhdx`
2. `C:\Windows\Temp\dock_compact.txt` (Para archivo script buffer)

## 🛡️ Algoritmo Heurístico y Flujo Defensivo
Para lograr compactar un bloque bloqueado por el kernel, el código asume el siguiente algoritmo hiper-seguro:
1. **Verificación de Candado (Lock Check):** No se puede compactar si Docker está enviando I/O.
2. **Apagado en Frío:** Ejecutamos `wsl --shutdown` en consola aislada, matando por completo el subsistema nativo de Linux subyacente de golpe y liberando el disco.
3. **Escritura Sanitizada:** Se graba un TXT temporal únicamente en el directorio mapeado de Alta Seguridad de Windows Temp mediante `SecurityCore.get_windows_temp_path()`.
4. **Sandboxing de API:** En lugar de manipular bytes binarios inestables manualmente en Python con el VHDX de Docker, Python le cede el comando a la CAPI Nativa de Windows Diskpart (`diskpart /s`), evadiendo 100% el riesgo de corrupción de clústeres a nivel SO.
