import customtkinter as ctk
import tkinter.messagebox as msg
import threading
from tkinter import ttk

# Importacion de todos los modulos desarrollados
import os
from PIL import Image
from core.security import SecurityCore
from modules.npm_cleaner import NodeCleaner
from modules.docker_cleaner import DockerCleaner
from modules.editors_cleaner import EditorsCleaner
from modules.browsers_cleaner import BrowsersCleaner
from modules.deep_uninstaller import DeepUninstaller
from modules.node_zombie_hunter import NodeZombieHunter
from modules.windows_core_cleaner import WindowsCoreCleaner
from modules.sdks_ia_cleaner import SDKsIACleaner

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DevDetoxApp(ctk.CTk):
    def __init__(self, is_admin: bool):
        super().__init__()

        self.is_admin = is_admin
        self.title("DevDetox - Ultimate Cleaner")
        self.geometry("950x650")
        self.resizable(False, False)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # -- Instancias de Modulos --
        self.mod_npm = NodeCleaner()
        self.mod_docker = DockerCleaner()
        self.mod_editors = EditorsCleaner()
        self.mod_browsers = BrowsersCleaner()
        self.mod_uninstaller = DeepUninstaller()
        self.mod_zombies = NodeZombieHunter()
        self.mod_win_core = WindowsCoreCleaner()
        self.mod_sdks = SDKsIACleaner()

        # -- Barra Lateral --
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="DevDetox 🛡️", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        self.btn_core = ctk.CTkButton(self.sidebar_frame, text="Windows Core", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: self.select_frame("core"))
        self.btn_core.grid(row=1, column=0, padx=20, pady=10)

        self.btn_dev = ctk.CTkButton(self.sidebar_frame, text="Node & Docker", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: self.select_frame("dev"))
        self.btn_dev.grid(row=2, column=0, padx=20, pady=10)

        self.btn_ide = ctk.CTkButton(self.sidebar_frame, text="IDE & Browsers", fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command=lambda: self.select_frame("ide"))
        self.btn_ide.grid(row=3, column=0, padx=20, pady=10)

        admin_text = "🟢 Root" if self.is_admin else "🔴 User (Limitado)"
        self.admin_label = ctk.CTkLabel(self.sidebar_frame, text=admin_text, font=ctk.CTkFont(size=12))
        self.admin_label.grid(row=6, column=0, padx=20, pady=(10, 20))

        # -- Contenedor Principal Multipestaña --
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Diccionario de frames
        self.frames = {}
        self.setup_frames()

        # Alerta Admin Global
        if not self.is_admin:
            self.warning_frame = ctk.CTkFrame(self.main_container, fg_color="#3E2723")
            self.warning_frame.grid(row=1, column=0, sticky="ew", pady=(10,0))
            lbl = ctk.CTkLabel(self.warning_frame, text="⚠️ Atención: Módulos como Uninstaller y Windows Core requieren Administrador.", text_color="#FFB300")
            lbl.pack(side="left", padx=10, pady=5)
            btn = ctk.CTkButton(self.warning_frame, text="Elevate", width=80, fg_color="#b71c1c", hover_color="#c62828", command=self.request_elevation)
            btn.pack(side="right", padx=10, pady=5)

        # Seleccion inicial
        self.select_frame("core")

    def setup_frames(self):
        # Frame: Windows Core
        f_core = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.frames["core"] = f_core
        self.build_win_core_ui(f_core)

        # Frame: Node & Docker
        f_dev = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.frames["dev"] = f_dev
        self.build_dev_ui(f_dev)

        # Frame: IDE & Browsers
        f_ide = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.frames["ide"] = f_ide
        self.build_ide_ui(f_ide)

    def select_frame(self, name):
        # Resetear botones
        self.btn_core.configure(fg_color="transparent")
        self.btn_dev.configure(fg_color="transparent")
        self.btn_ide.configure(fg_color="transparent")

        # Pintar activo
        if name == "core": self.btn_core.configure(fg_color=("gray75", "gray25"))
        elif name == "dev": self.btn_dev.configure(fg_color=("gray75", "gray25"))
        elif name == "ide": self.btn_ide.configure(fg_color=("gray75", "gray25"))

        # Ocultar todos, mostrar el seleccionado
        for f in self.frames.values():
            f.grid_remove()
        self.frames[name].grid(row=0, column=0, sticky="nsew")

    # ==========================
    # CONSTRUCTORES DE SECCIONES
    # ==========================
    
    def build_win_core_ui(self, parent):
        ctk.CTkLabel(parent, text="Sistema & Desinstalador", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 20))

        # Modulo 7: Win Core
        frame_win = ctk.CTkFrame(parent)
        frame_win.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(frame_win, text="🧹 Limpieza de Bajo Nivel (Temp, Prefetch, Papelera)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10,0))
        
        self.lbl_win_size = ctk.CTkLabel(frame_win, text="Haz clic en Escanear para analizar...")
        self.lbl_win_size.pack(anchor="w", padx=15, pady=5)
        
        btn_scan_win = ctk.CTkButton(frame_win, text="Escanear", width=100, command=self.scan_win_core)
        btn_scan_win.pack(side="left", padx=15, pady=10)
        
        self.btn_clean_win = ctk.CTkButton(frame_win, text="Purgar Sistema", width=100, fg_color="#b71c1c", hover_color="#c62828", state="disabled", command=self.clean_win_core)
        self.btn_clean_win.pack(side="left", padx=5, pady=10)
        self.btn_details_win = ctk.CTkButton(frame_win, text="Ver Detalles", width=100, fg_color="transparent", border_width=1, command=lambda: self.show_details_modal("Temporales y Basura", getattr(self, "last_win_paths", [])))
        
        self.prog_win = ctk.CTkProgressBar(frame_win, mode="indeterminate", width=200)

        # Modulo 5: Uninstaller (Solo visualizacion basica por ahora)
        frame_uninst = ctk.CTkFrame(parent)
        frame_uninst.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(frame_uninst, text="🔪 Desinstalador Heurístico", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10,0))
        ctk.CTkLabel(frame_uninst, text="Este módulo audita software instalado y limpia basura residual post-desinstalación.", text_color="gray").pack(anchor="w", padx=15)
        
        self.btn_open_uninst = ctk.CTkButton(frame_uninst, text="Abrir Gestor", width=100, command=self.open_uninstaller_modal)
        self.btn_open_uninst.pack(anchor="w", padx=15, pady=10)

    def build_dev_ui(self, parent):
        ctk.CTkLabel(parent, text="Node.js & Docker", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        # Modulo 1: NPM/PNPM
        f_npm = ctk.CTkFrame(parent)
        f_npm.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(f_npm, text="📦 Caché Global de Gestores (NPM / PNPM)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10,0))
        self.lbl_npm_size = ctk.CTkLabel(f_npm, text="Haz clic en Escanear para analizar...")
        self.lbl_npm_size.pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkButton(f_npm, text="Escanear", width=100, command=self.scan_npm).pack(side="left", padx=15, pady=10)
        self.btn_clean_npm = ctk.CTkButton(f_npm, text="Vaciar Caché", width=100, fg_color="#b71c1c", state="disabled", command=self.clean_npm)
        self.btn_clean_npm.pack(side="left", padx=5, pady=10)
        self.btn_details_npm = ctk.CTkButton(f_npm, text="Ver Detalles", width=100, fg_color="transparent", border_width=1, command=lambda: self.show_details_modal("Cachés NPM/PNPM", getattr(self, "last_npm_paths", [])))
        
        self.prog_npm = ctk.CTkProgressBar(f_npm, mode="indeterminate", width=200)

        # Modulo 2: Docker
        f_dock = ctk.CTkFrame(parent)
        f_dock.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(f_dock, text="🐳 Docker VHDX Compactor (WSL)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10,0))
        
        dock_txt = "Detectado. Esperando análisis." if self.mod_docker.is_docker_installed() else "Docker Desktop no detectado en VHDX WSL local."
        self.lbl_dock_size = ctk.CTkLabel(f_dock, text=dock_txt)
        self.lbl_dock_size.pack(anchor="w", padx=15, pady=5)
        
        btn_scan_dock = ctk.CTkButton(f_dock, text="Escanear VHDX", width=100, command=self.scan_docker)
        btn_scan_dock.pack(side="left", padx=15, pady=10)
        self.btn_clean_dock = ctk.CTkButton(f_dock, text="Compactar Disco", width=120, fg_color="#b71c1c", state="disabled", command=self.clean_docker)
        self.btn_clean_dock.pack(side="left", padx=5, pady=10)
        
        self.prog_dock = ctk.CTkProgressBar(f_dock, mode="indeterminate", width=200)

        # Modulo 6: Zombie Hunter
        f_zom = ctk.CTkFrame(parent)
        f_zom.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(f_zom, text="🧟 Caza Zombis (node_modules inactivos)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10,0))
        
        self.lbl_zom_stat = ctk.CTkLabel(f_zom, text="Busca directorios abandonados por más de 3 meses.")
        self.lbl_zom_stat.pack(anchor="w", padx=15, pady=5)
        
        btn_scan_zom = ctk.CTkButton(f_zom, text="Escanear Discos", width=120, command=self.scan_zombies)
        btn_scan_zom.pack(side="left", padx=15, pady=10)
        self.btn_clean_zom = ctk.CTkButton(f_zom, text="PURGAR ZOMBIS", width=120, fg_color="#b71c1c", command=self.clean_zombies)
        self.btn_details_zom = ctk.CTkButton(f_zom, text="Ver Detalles", width=100, fg_color="transparent", border_width=1, command=lambda: self.show_details_modal("Proyectos Node Zombis", getattr(self, "last_zom_paths", [])))
        
        self.prog_zom = ctk.CTkProgressBar(f_zom, mode="indeterminate", width=200)

    def build_ide_ui(self, parent):
        ctk.CTkLabel(parent, text="Editores, SDKs & Navegadores", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        # Modulo 4: Navegadores Multi-motor
        f_bro = ctk.CTkFrame(parent)
        f_bro.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(f_bro, text="🌍 Caché Acelerada de Navegadores (Chromium & Firefox)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10,0))
        self.lbl_bro_size = ctk.CTkLabel(f_bro, text="Haz clic en Escanear para analizar...")
        self.lbl_bro_size.pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkButton(f_bro, text="Escanear", width=100, command=self.scan_browsers).pack(side="left", padx=15, pady=10)
        self.btn_clean_bro = ctk.CTkButton(f_bro, text="Limpiar Cachés", width=120, fg_color="#b71c1c", state="disabled", command=self.clean_browsers)
        self.btn_clean_bro.pack(side="left", padx=5, pady=10)
        self.btn_details_bro = ctk.CTkButton(f_bro, text="Ver Detalles", width=100, fg_color="transparent", border_width=1, command=lambda: self.show_details_modal("Cachés de Navegadores", getattr(self, "last_bro_paths", [])))
        self.prog_bro = ctk.CTkProgressBar(f_bro, mode="indeterminate", width=200)

        # Modulo 3: IDEs
        f_ide = ctk.CTkFrame(parent)
        f_ide.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(f_ide, text="💻 Code Editors (VS Code, Trae, Cursor)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10,0))
        self.lbl_ide_size = ctk.CTkLabel(f_ide, text="Haz clic en Escanear para analizar...")
        self.lbl_ide_size.pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkButton(f_ide, text="Escanear", width=100, command=self.scan_editors).pack(side="left", padx=15, pady=10)
        self.btn_clean_ide = ctk.CTkButton(f_ide, text="Limpiar Basura", width=120, fg_color="#b71c1c", state="disabled", command=self.clean_editors)
        self.btn_clean_ide.pack(side="left", padx=5, pady=10)
        self.btn_details_ide = ctk.CTkButton(f_ide, text="Ver Detalles", width=100, fg_color="transparent", border_width=1, command=lambda: self.show_details_modal("Carpetas de Editores", getattr(self, "last_ide_paths", [])))
        self.prog_ide = ctk.CTkProgressBar(f_ide, mode="indeterminate", width=200)

        # Modulo 8: SDKs & IAs
        f_sdk = ctk.CTkFrame(parent)
        f_sdk.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(f_sdk, text="🤖 Caches Ocultas (Gemini, Cursor AI, Android SDK)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=(10,0))
        self.lbl_sdk_size = ctk.CTkLabel(f_sdk, text="Haz clic en Escanear para analizar...")
        self.lbl_sdk_size.pack(anchor="w", padx=15, pady=5)
        
        ctk.CTkButton(f_sdk, text="Escanear", width=100, command=self.scan_sdks).pack(side="left", padx=15, pady=10)
        self.btn_clean_sdk = ctk.CTkButton(f_sdk, text="Purgar IAs & SDKs", width=140, fg_color="#b71c1c", state="disabled", command=self.clean_sdks)
        self.btn_clean_sdk.pack(side="left", padx=5, pady=10)
        self.btn_details_sdk = ctk.CTkButton(f_sdk, text="Ver Detalles", width=100, fg_color="transparent", border_width=1, command=lambda: self.show_details_modal("Logs de SDKs e IAs", getattr(self, "last_sdk_paths", [])))
        self.prog_sdk = ctk.CTkProgressBar(f_sdk, mode="indeterminate", width=200)

    # ==========================
    # LOGICA DE HILOS Y EVENTOS
    # ==========================
    def show_details_modal(self, title, paths_list):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry("650x450")
        win.attributes('-topmost', 1)
        win.grab_set()
        
        lbl = ctk.CTkLabel(win, text=f"📂 Rutas Detectadas: {title}", font=ctk.CTkFont(weight="bold", size=14))
        lbl.pack(pady=10, padx=20, anchor="w")
        
        txt = ctk.CTkTextbox(win, wrap="none")
        txt.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        content = "\n".join(paths_list) if paths_list else "No se detectaron directorios ocultos."
        txt.insert("0.0", content)
        txt.configure(state="disabled")

    def request_elevation(self):
        if hasattr(self, 'elevation_callback') and self.elevation_callback:
            self.elevation_callback()

    # --- Windows Core (Temp & Papelera) ---
    def scan_win_core(self):
        self.lbl_win_size.configure(text="Escaneando el kernel y directorios maestros...")
        self.prog_win.pack(side="left", padx=10, pady=10)
        self.prog_win.start()
        def worker():
            sizes = self.mod_win_core.get_sizes()
            tot = sizes["total"]
            self.last_win_paths = sizes.get("paths_found", [])
            self.lbl_win_size.configure(text=f"Total acumulado: {tot} MB (Papelera: {sizes['recycle_bin']} MB, Temp: {sizes['user_temp']} MB)")
            if tot > 0: 
                self.btn_clean_win.configure(state="normal")
                self.btn_details_win.pack(side="left", padx=5, pady=10)
            self.prog_win.stop()
            self.prog_win.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    def clean_win_core(self):
        if not msg.askyesno("Confirmar", "Se vaciará la papelera en TODAS las unidades y se limpiarán temporales. ¿Continuar?"): return
        self.btn_clean_win.configure(state="disabled")
        self.prog_win.pack(side="left", padx=10, pady=10)
        self.prog_win.start()
        def worker():
            res = self.mod_win_core.clean()
            t = "Limpieza exitosa." if res["success"] else f"Limpieza parcial. {len(res['failed_paths'])} archivos del sistema temporal bloqueados por programas en uso."
            if res["recycle_bin_cleared"]: t += " Papelera vaciada correctamente."
            self.lbl_win_size.configure(text=t)
            self.prog_win.stop()
            self.prog_win.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    # --- NPM ---
    def scan_npm(self):
        self.lbl_npm_size.configure(text="Buscando cachés globales de Yarn/NPM/PNPM...")
        self.prog_npm.pack(side="left", padx=10, pady=10)
        self.prog_npm.start()
        def worker():
            s = self.mod_npm.get_sizes()
            tot = s.get("total", s.get("total_mb", 0))
            self.last_npm_paths = s.get("paths_found", [])
            self.lbl_npm_size.configure(text=f"Encontrado: {tot} MB en cachés de paquetes Node.")
            if tot > 0: 
                self.btn_clean_npm.configure(state="normal")
                self.btn_details_npm.pack(side="left", padx=5, pady=10)
            self.prog_npm.stop()
            self.prog_npm.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    def clean_npm(self):
        if not msg.askyesno("Confirmar", "¿Forzar purga de NPM y PNPM caches globales?"): return
        self.btn_clean_npm.configure(state="disabled")
        self.prog_npm.pack(side="left", padx=10, pady=10)
        self.prog_npm.start()
        def worker():
            succ = self.mod_npm.clean()
            txt = "Purga nativa ejecutada con éxito." if succ else "Errores parciales reportados (archivos bloqueados)."
            self.lbl_npm_size.configure(text=txt)
            self.prog_npm.stop()
            self.prog_npm.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    # --- Docker ---
    def scan_docker(self):
        if not self.mod_docker.is_docker_installed():
            msg.showwarning("Docker", "No se detectó el VHDX de Docker Desktop WSL o no existe la ruta.")
            return
        self.lbl_dock_size.configure(text="Analizando VHDX (Esto puede tardar unos segundos)...")
        self.prog_dock.pack(side="left", padx=10, pady=10)
        self.prog_dock.start()
        def worker():
            s = self.mod_docker.get_vhdx_size()
            self.lbl_dock_size.configure(text=f"Peso virtual del Disco: {s} GB\n(La compactación recupera el espacio 'vacío' interno).")
            if s > 0 and self.is_admin: 
                self.btn_clean_dock.configure(state="normal")
            elif s > 0 and not self.is_admin:
                self.lbl_dock_size.configure(text=f"Peso: {s} MB. REQUIERE SER ADMINISTRADOR PARA COMPACTAR.", text_color="orange")
            self.prog_dock.stop()
            self.prog_dock.pack_forget()
        threading.Thread(target=worker, daemon=True).start()
        
    def clean_docker(self):
        if not msg.askyesno("¡Cuidado!", "Se apagará la maquina WSL. Docker Desktop se detendrá por unos instantes. ¿Autorizas?"): return
        self.btn_clean_dock.configure(state="disabled")
        self.lbl_dock_size.configure(text="Compactando disco con Diskpart. Por favor espera...")
        self.prog_dock.pack(side="left", padx=10, pady=10)
        self.prog_dock.start()
        def worker():
            succ = self.mod_docker.compact_vhdx()
            txt = "Compactación Exitosamente Completada." if succ else "Fallo crítico al correr Diskpart. Revisa consola."
            self.lbl_dock_size.configure(text=txt)
            self.prog_dock.stop()
            self.prog_dock.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    # --- Zombis ---
    def scan_zombies(self):
        self.lbl_zom_stat.configure(text="Escaneando el disco en busca de agujeros negros (node_modules inactivos). Esto tomará un tiempo...")
        self.prog_zom.pack(side="left", padx=10, pady=10)
        self.prog_zom.start()
        def worker():
            res = self.mod_zombies.scan_for_zombies(months_inactive=3)
            tot_mb = res["total_mb"]
            tot_count = len(res["zombies_found"])
            if tot_count == 0:
                self.lbl_zom_stat.configure(text="¡Felicidades! No posees carpetas zombies.")
            else:
                self.lbl_zom_stat.configure(text=f"🚨 ¡Peligro! {tot_count} proyectos abandonados encontrados absorbiendo {tot_mb} MB.")
                self.cached_zombies = [z["node_modules_path"] for z in res["zombies_found"]]
                self.last_zom_paths = self.cached_zombies
                self.btn_clean_zom.pack(side="left", padx=5, pady=10)
                self.btn_details_zom.pack(side="left", padx=5, pady=10)
            self.prog_zom.stop()
            self.prog_zom.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    def clean_zombies(self):
        if not hasattr(self, 'cached_zombies') or not self.cached_zombies: return
        if not msg.askyesno("Destrucción Masiva", f"Se borrarán fsícamente {len(self.cached_zombies)} directorios 'node_modules'. ¡Esta acción es irreversible! ¿Matar a los zombis?"): return
        self.lbl_zom_stat.configure(text="Aniquilando...")
        self.prog_zom.pack(side="left", padx=10, pady=10)
        self.prog_zom.start()
        def worker():
            res = self.mod_zombies.kill_zombies(self.cached_zombies)
            self.lbl_zom_stat.configure(text=f"Genocidio exitoso. Liberados {res['freed_mb']} MB (Fallaron: {len(res['failed_paths'])})")
            self.cached_zombies = []
            self.prog_zom.stop()
            self.prog_zom.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    # --- Browsers ---
    def scan_browsers(self):
        self.lbl_bro_size.configure(text="Penetrando perfiles de Chromium & Gecko...")
        self.prog_bro.pack(side="left", padx=10, pady=10)
        self.prog_bro.start()
        def worker():
            sizes = self.mod_browsers.get_sizes()
            tot = sizes["total_size_mb"]
            self.last_bro_paths = sizes.get("paths_found", [])
            self.lbl_bro_size.configure(text=f"Caché de Navegadores: {tot} MB distribuidos en {sizes.get('profiles_found', '?')} perfiles.")
            if tot > 0: 
                self.btn_clean_bro.configure(state="normal")
                self.btn_details_bro.pack(side="left", padx=5, pady=10)
            self.prog_bro.stop()
            self.prog_bro.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    def clean_browsers(self):
        if not msg.askyesno("Confirmar", "Se vaciará estrictamente V8 Code Cache y GPU Shaders. Contraseñas seguras. ¿Proceder?"): return
        self.btn_clean_bro.configure(state="disabled")
        self.prog_bro.pack(side="left", padx=10, pady=10)
        self.prog_bro.start()
        def worker():
            res = self.mod_browsers.clean()
            txt = "Purga de Navegadores completada." if res["success"] else "Se saltaron algunos archivos por Locks de Navegador."
            self.lbl_bro_size.configure(text=txt)
            self.prog_bro.stop()
            self.prog_bro.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    # --- Editors ---
    def scan_editors(self):
        self.lbl_ide_size.configure(text="Analizando Workspaces de VSCode, Trae, Cursor...")
        self.prog_ide.pack(side="left", padx=10, pady=10)
        self.prog_ide.start()
        def worker():
            sizes = self.mod_editors.get_sizes()
            tot = sizes["total"]
            self.last_ide_paths = sizes.get("paths_found", [])
            self.lbl_ide_size.configure(text=f"Workspace, Crashpads y Data retenida: {tot} MB.")
            if tot > 0: 
                self.btn_clean_ide.configure(state="normal")
                self.btn_details_ide.pack(side="left", padx=5, pady=10)
            self.prog_ide.stop()
            self.prog_ide.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    def clean_editors(self):
        self.btn_clean_ide.configure(state="disabled")
        self.prog_ide.pack(side="left", padx=10, pady=10)
        self.prog_ide.start()
        def worker():
            res = self.mod_editors.clean()
            txt = "Limpieza de Entornos finalizada." if res["success"] else "Fallaron carpetas en uso (Cierra el editor primero)."
            self.lbl_ide_size.configure(text=txt)
            self.prog_ide.stop()
            self.prog_ide.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    # --- SDKs e IA ---
    def scan_sdks(self):
        self.lbl_sdk_size.configure(text="Analizando telemetria de Google Gemini y Cursor AI...")
        self.prog_sdk.pack(side="left", padx=10, pady=10)
        self.prog_sdk.start()
        def worker():
            s = self.mod_sdks.get_sizes()
            tot = s["total_size_mb"]
            self.last_sdk_paths = s.get("paths_found", [])
            self.lbl_sdk_size.configure(text=f"Data fantasma encontrada: {tot} MB.")
            if tot > 0: 
                self.btn_clean_sdk.configure(state="normal")
                self.btn_details_sdk.pack(side="left", padx=5, pady=10)
            self.prog_sdk.stop()
            self.prog_sdk.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    def clean_sdks(self):
        self.btn_clean_sdk.configure(state="disabled")
        self.prog_sdk.pack(side="left", padx=10, pady=10)
        self.prog_sdk.start()
        def worker():
            r = self.mod_sdks.clean()
            txt = "Extirpación de Logs de IAs y SDKs exitosa." if r["success"] else "Advertencia: Archivos protegidos saltados."
            self.lbl_sdk_size.configure(text=txt)
            self.prog_sdk.stop()
            self.prog_sdk.pack_forget()
        threading.Thread(target=worker, daemon=True).start()

    # --- Uninstaller (Placeholder interactivo) ---
    def open_uninstaller_modal(self):
        if not self.is_admin:
            msg.showwarning("Atención", "Necesitas permisos de Administrador Root para leer la raiz del sistema HKLM del Registro.")
            return
        # Render a new quick Toplevel window for uninstaller
        win = ctk.CTkToplevel(self)
        win.title("Deep Uninstaller")
        win.geometry("700x550")
        win.attributes('-topmost', 1) # Por encima
        win.grab_set() # Modal focus
        
        lbl = ctk.CTkLabel(win, text="Cargando base de datos WMI (Registry)... Por favor espera.")
        lbl.pack(pady=(15, 5))
        
        # Controles
        ctrl_frame = ctk.CTkFrame(win, fg_color="transparent")
        ctrl_frame.pack(fill="x", padx=20, pady=5)
        
        entry_search = ctk.CTkEntry(ctrl_frame, placeholder_text="Buscar programa...")
        entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        combo_sort = ctk.CTkComboBox(ctrl_frame, values=[
            "Nombre (A-Z)", "Nombre (Z-A)", 
            "Más Pesados", "Más Ligeros", 
            "Instalación (Reciente)", "Instalación (Antiguo)"
        ], state="readonly")
        combo_sort.set("Nombre (A-Z)")
        combo_sort.pack(side="right")
        
        list_frame = ctk.CTkScrollableFrame(win)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        win.apps_db = []

        def extract_icon_from_exe(path: str):
            try:
                import win32ui, win32gui, win32con, win32api
                large, small = win32gui.ExtractIconEx(path, 0)
                hicon = large[0] if large else small[0] if small else None
                if not hicon: return None
                ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
                ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
                hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                hdc = hdc.CreateCompatibleDC()
                hdc.SelectObject(hbmp)
                win32gui.DrawIconEx(hdc.GetSafeHdc(), 0, 0, hicon, ico_x, ico_y, 0, None, win32con.DI_NORMAL)
                bmpinfo = hbmp.GetInfo()
                bmpstr = hbmp.GetBitmapBits(True)
                img = Image.frombuffer('RGBA', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRA', 0, 1)
                win32gui.DestroyIcon(hicon)
                return img
            except Exception:
                return None

        def render_list(*args):
            for widget in list_frame.winfo_children():
                widget.destroy()
                
            q = entry_search.get().lower()
            sort_val = combo_sort.get()
            
            filtered = [a for a in win.apps_db if q in str(a["name"]).lower()]
            
            if sort_val == "Nombre (A-Z)":
                filtered.sort(key=lambda x: str(x["name"]).lower())
            elif sort_val == "Nombre (Z-A)":
                filtered.sort(key=lambda x: str(x["name"]).lower(), reverse=True)
            elif sort_val == "Más Pesados":
                filtered.sort(key=lambda x: float(x.get("size_raw", 0)), reverse=True)
            elif sort_val == "Más Ligeros":
                filtered.sort(key=lambda x: float(x.get("size_raw", 0)))
            elif sort_val == "Instalación (Reciente)":
                filtered.sort(key=lambda x: str(x.get("install_date", "00000000")), reverse=True)
            elif sort_val == "Instalación (Antiguo)":
                filtered.sort(key=lambda x: str(x.get("install_date", "99999999")))
                
            lbl.configure(text=f"Mostrando {len(filtered)} de {len(win.apps_db)} apps. (Orden: {sort_val})")
            
            for app in filtered:
                display_text = f"{app['name']}   [{app['size']}]"
                button_kwargs = {
                    "text": display_text,
                    "anchor": "w",
                    "fg_color": "transparent",
                    "text_color": ("gray10", "#DCE4EE"),
                    "border_width": 1,
                    "command": lambda a=app: self.fire_uninstaller(a, win)
                }
                
                if app.get("ctk_img"):
                    button_kwargs["image"] = app["ctk_img"]
                else:
                    button_kwargs["text"] = f"📦 {display_text}"
                
                b = ctk.CTkButton(list_frame, **button_kwargs)
                b.pack(fill="x", pady=2)

        entry_search.bind("<KeyRelease>", render_list)
        combo_sort.configure(command=render_list)

        def load_reg():
            raw_apps = self.mod_uninstaller.get_installed_software()
            
            for app in raw_apps:
                ctk_img = None
                icon_path = app["icon_path"]
                if icon_path and os.path.exists(icon_path):
                    try:
                        if icon_path.lower().endswith(('.ico', '.png', '.jpg')):
                            pil_img = Image.open(icon_path).resize((24, 24))
                            ctk_img = ctk.CTkImage(pil_img, size=(24, 24))
                        elif icon_path.lower().endswith('.exe'):
                            pil_img = extract_icon_from_exe(icon_path)
                            if pil_img:
                                ctk_img = ctk.CTkImage(pil_img, size=(24, 24))
                    except Exception:
                        pass
                app["ctk_img"] = ctk_img
                win.apps_db.append(app)
                
            win.after(0, render_list)

        threading.Thread(target=load_reg, daemon=True).start()

    def fire_uninstaller(self, app_obj, window):
        name = app_obj["name"]
        cmd = app_obj["uninstall_command"]
        if msg.askyesno("Ejecutar MSIs", f"¿Invocar al desinstalador maestro de: {name}?\nComando: {cmd}"):
            # Primero llamamos al oficial
            self.mod_uninstaller.run_official_uninstaller(cmd)
            # Segundo: Rastrear huerfanos post-desinstalacion
            window.title(f"Aguardando... Rastreando Archivos Basura de {name}")
            leftovers = self.mod_uninstaller.hunt_leftovers(name)
            if leftovers["found_mb"] > 0:
                if msg.askyesno("☢️ BASURA ENCONTRADA", f"¡El desinstalador de {name} dejó {leftovers['found_mb']} MB de directorios huérfanos localizados heurísticamente!\n\n¿Deseas purgarlos permanentemente?"):
                    self.mod_uninstaller.destroy_leftovers(leftovers["target_folders"])
                    msg.showinfo("Purga", "Basura erradicada con éxito.")
            else:
                msg.showinfo("Limpieza", "Desinstalador oficial ejecutado. No se localizaron rastros adicionales sucios.")

if __name__ == "__main__":
    app = DevDetoxApp(is_admin=True)
    app.mainloop()
