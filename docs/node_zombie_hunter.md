# Documentación de Módulo: Node.js Zombie Hunter (node_zombie_hunter.py)

## 📌 Objetivo del Módulo
La peor pesadilla de un desarrollador web es el Disco Local C. Las carpetas `node_modules` son agujeros negros que descargan cientos de megabytes de miles de dependencias por CADA proyecto Javascript/Typescript creado. Si un usuario tiene 50 mini-proyectos abandonados de hace meses, fácilmente está perdiendo **20 a 50 Gigabytes de espacio muerto**.
El objetivo de este módulo es escanear los discos duros, indexar todos los proyectos Javascript, y discriminar matemáticamente por "Tiempo de Vida Activa". Aquellos que pasen el Threshold (por defecto 3 meses inactivos) son marcados como Zombis para su ejecución.

## ⚙️ Arquitectura de Caza
El modulo no iterará sobre el disco `C:\` base o carpetas protegidas `Windows` porque colapsaría la memoria de Python (Directory Search Timeout). Se mapean Roots altamente productivos:
- `%USERPROFILE%/Documents`
- `%USERPROFILE%/Desktop`
- `%USERPROFILE%/Downloads`
- `C:/Proyectos`

Al conseguir una capeta `node_modules` dentro de su recursión (`os.walk`), la IA extrae instantáneamente el Archivo Raíz padre (ej. `package.json` o la carpeta del repositorio en sí) para leer su meta-data de última modificación en sistema (`os.path.getmtime`). 

## 🛡️ Algoritmo Heurístico y Flujo Defensivo
1. **Blindaje de Proyectos Vivos:** El calculo cronológico de "Abandono" del Proyecto jamás se realiza comprobando fechas de los archivos DENTRO de `node_modules`. Muchas veces un framework se instala hoy y los archivos dicen ser del año 2018. El hunter comprueba exclusivamente las acciones del Usuario leyendo el `package.json` exterior. Si lo tocaste hace un mes, está vivo y seguro.
2. **Validación Nominal (Zero Trust):** En el ciclo de borrado físico final (`kill_zombies()`), el código inyecta una condicional Hardcodeada: `nm_path.name == 'node_modules'`. Incluso si un atacante engañara a la lista virtual para que el borrado apunte a `C:/Users/Jesus/Desktop`, el bot se negaría a actuar si la carpeta no se nombra textualmente "node_modules".
