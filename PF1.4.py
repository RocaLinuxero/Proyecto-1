import os
import hashlib
import re
import smtplib
import json
from tkinter import *
from tkinter import messagebox, ttk
from datetime import datetime
from fpdf import FPDF
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# --- CONFIGURACIÓN Y COLORES ---
COLOR_BG = "#ecf0f1"
COLOR_SECUNDARIO = "#2c3e50"

# --- FUNCIONES DE SEGURIDAD Y CONFIG ---
def encriptar(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validar_password_segura(password):
    if len(password) < 8: return False, "Mínimo 8 caracteres."
    if not re.search(r"[A-Z]", password): return False, "Falta una Mayúscula."
    if not re.search(r"\d", password): return False, "Falta un Número."
    if not re.search(r"[!@#$%^&*]", password): return False, "Falta un Símbolo."
    return True, ""

def guardar_config_correo(datos):
    with open("Configuracion/correo.json", "w") as f:
        json.dump(datos, f)

def cargar_config_correo():
    if os.path.exists("Configuracion/correo.json"):
        with open("Configuracion/correo.json", "r") as f:
            return json.load(f)
    return {"remitente": "", "password": ""}

# --- GESTIÓN DE ARCHIVOS ---
def crear_directorios():
    for carpeta in ["Configuracion", "Facturas"]:
        if not os.path.exists(carpeta): os.makedirs(carpeta)

def registrar_bitacora(accion, usuario="Sistema"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("Configuracion/bitacora.txt", "a") as f:
        f.write(f"[{fecha}] ({usuario}) {accion}\n")

# --- CLASE PRINCIPAL ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Empresa Eléctrica")
        self.root.geometry("750x800")
        self.root.configure(bg=COLOR_BG)
        self.usuario_actual = None
        self.login()

    def clear(self):
        for w in self.root.winfo_children(): w.destroy()

    def header(self, texto):
        Label(self.root, text=texto, bg=COLOR_SECUNDARIO,
              fg="white", font=("Arial", 16, "bold")).pack(fill="x", pady=10)

    # --- LOGIN ---
    def login(self):
        self.clear()
        self.header("Sistema Empresa Eléctrica")
        f = Frame(self.root, bg="white", padx=30, pady=30)
        f.pack(pady=50)
        Label(f, text="Usuario", bg="white").pack()
        self.ent_user = Entry(f)
        self.ent_user.pack()
        Label(f, text="Contraseña", bg="white").pack()
        self.ent_pass = Entry(f, show="*")
        self.ent_pass.pack()
        Button(f, text="Ingresar", command=self.validar_acceso, bg=COLOR_SECUNDARIO, fg="white").pack(pady=10)

    def obtener_usuarios(self):
        usuarios = {}
        if os.path.exists("Configuracion/usuarios.txt"):
            with open("Configuracion/usuarios.txt") as f:
                for linea in f:
                    u, p = linea.strip().split(",")
                    usuarios[u] = p
        return usuarios

    def validar_acceso(self):
        user, pas = self.ent_user.get(), self.ent_pass.get()
        db = self.obtener_usuarios()
        if user in db and (db[user] == encriptar(pas) or db[user] == pas):
            self.usuario_actual = user
            registrar_bitacora("Inicio de sesión", user)
            if user in ["admin", "admin23"]: self.modo_administrador()
            else: self.menu_facturacion()
        else:
            messagebox.showerror("Error", "Datos incorrectos")

    # --- ADMINISTRACIÓN ---
    def modo_administrador(self):
        self.clear()
        self.header("Panel Administrador")
        
        # Botón Configuración de Correo
        Button(self.root, text="📧 Configurar Servidor de Correo", 
               command=self.config_correo_window, bg="#e67e22", fg="white").pack(pady=5)

        f = Frame(self.root, bg="white", padx=20, pady=20)
        f.pack()
        Label(f, text="Nuevo Usuario", bg="white").grid(row=0, column=0)
        self.new_u = Entry(f); self.new_u.grid(row=0, column=1)
        Label(f, text="Contraseña", bg="white").grid(row=1, column=0)
        self.new_p = Entry(f, show="*"); self.new_p.grid(row=1, column=1)
        Label(f, text="Confirmar", bg="white").grid(row=2, column=0)
        self.confirm_p = Entry(f, show="*"); self.confirm_p.grid(row=2, column=1)
        
        Button(f, text="Registrar Usuario", command=self.guardar_usuario).grid(row=3, columnspan=2, pady=10)
        
        self.tabla = ttk.Treeview(self.root, columns=("User", "Hash"), show="headings")
        self.tabla.heading("User", text="Usuario"); self.tabla.heading("Hash", text="Hash"); self.tabla.pack(pady=10)
        self.actualizar_tabla()

        Button(self.root, text="Ir a Facturación", command=self.menu_facturacion).pack(pady=5)
        Button(self.root, text="Cerrar sesión", command=self.login).pack()

    def config_correo_window(self):
        win = Toplevel(self.root)
        win.title("Configuración SMTP")
        win.geometry("400x300")
        
        config = cargar_config_correo()
        
        Label(win, text="Correo Remitente (Gmail):").pack(pady=5)
        ent_rem = Entry(win, width=40); ent_rem.insert(0, config['remitente']); ent_rem.pack()
        
        Label(win, text="Contraseña de Aplicación (16 caracteres):").pack(pady=5)
        ent_pass = Entry(win, show="*", width=40); ent_pass.insert(0, config['password']); ent_pass.pack()
        
        def guardar():
            guardar_config_correo({"remitente": ent_rem.get(), "password": ent_pass.get()})
            messagebox.showinfo("Éxito", "Configuración de correo guardada")
            win.destroy()
            
        Button(win, text="Guardar Configuración", command=guardar, bg="#27ae60", fg="white").pack(pady=20)

    def guardar_usuario(self):
        u, p, cp = self.new_u.get(), self.new_p.get(), self.confirm_p.get()
        if p != cp: messagebox.showerror("Error", "No coinciden"); return
        segura, msg = validar_password_segura(p)
        if not segura: messagebox.showwarning("Seguridad", msg); return
        with open("Configuracion/usuarios.txt", "a") as f: f.write(f"{u},{encriptar(p)}\n")
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        for u, p in self.obtener_usuarios().items(): self.tabla.insert("", END, values=(u, p))

    # --- FACTURACIÓN ---
    def menu_facturacion(self):
        self.clear()
        nav = Frame(self.root, bg=COLOR_BG)
        nav.pack(fill="x", padx=10, pady=5)
        Button(nav, text="⚙️ Configuración de Usuario", command=self.cambiar_password_window).pack(side="left")
        
        self.header("Módulo de Facturación")
        f = Frame(self.root, bg="white", padx=20, pady=20)
        f.pack(pady=20)

        campos = [("Correlativo", "correlativo"), ("Nombre", "nombre"), 
                  ("NIT", "nit"), ("Contador", "contador"), ("Consumo (kWh)", "consumo"),
                  ("Correo Cliente", "correo")]
        self.entries = {}
        for i, (texto, var) in enumerate(campos):
            Label(f, text=texto, bg="white").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            e = Entry(f, width=35); e.grid(row=i, column=1, pady=5)
            self.entries[var] = e

        Button(f, text="Generar y Enviar Factura", command=self.generar_factura, 
               bg="#2980b9", fg="white", font=("Arial", 10, "bold")).grid(row=len(campos), columnspan=2, pady=20)
        Button(self.root, text="Cerrar Sesión", command=self.login).pack()

    def cambiar_password_window(self):
        win = Toplevel(self.root); win.geometry("300x300")
        Label(win, text="Contraseña Actual").pack()
        ent_a = Entry(win, show="*"); ent_a.pack()
        Label(win, text="Nueva Contraseña").pack()
        ent_n = Entry(win, show="*"); ent_n.pack()
        
        def cambio():
            usuarios = self.obtener_usuarios()
            if encriptar(ent_a.get()) == usuarios[self.usuario_actual]:
                segura, msg = validar_password_segura(ent_n.get())
                if segura:
                    usuarios[self.usuario_actual] = encriptar(ent_n.get())
                    with open("Configuracion/usuarios.txt", "w") as f:
                        for u, p in usuarios.items(): f.write(f"{u},{p}\n")
                    messagebox.showinfo("OK", "Cambiado"); win.destroy()
                else: messagebox.showwarning("Error", msg)
            else: messagebox.showerror("Error", "Incorrecta")
        Button(win, text="Actualizar", command=cambio).pack()

    # --- ENVÍO DE CORREO ---
    def enviar_correo_pdf(self, destinatario, ruta_pdf, corr):
        config = cargar_config_correo()
        if not config["remitente"] or not config["password"]:
            messagebox.showwarning("Configuración Faltante", "El admin no ha configurado el correo remitente.")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = config["remitente"]
            msg['To'] = destinatario
            msg['Subject'] = f"Factura Eléctrica No. {corr}"
            msg.attach(MIMEText(f"Adjunto encontrará su factura No. {corr}. Saludos.", 'plain'))

            with open(ruta_pdf, "rb") as f:
                parte = MIMEBase('application', 'octet-stream')
                parte.set_payload(f.read())
                encoders.encode_base64(parte)
                parte.add_header('Content-Disposition', f"attachment; filename=Factura_{corr}.pdf")
                msg.attach(parte)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(config["remitente"], config["password"])
            server.sendmail(config["remitente"], destinatario, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    # --- GENERAR FACTURA ---
    def generar_factura(self):
        corr = self.entries["correlativo"].get().strip()
        nom = self.entries["nombre"].get().strip()
        nit = self.entries["nit"].get().strip()
        cont = self.entries["contador"].get().strip()
        cons_raw = self.entries["consumo"].get().strip()
        email_dest = self.entries["correo"].get().strip()

        # Regex Validaciones
        if not re.match(r"^\d+$", corr): messagebox.showerror("Error", "Correlativo inválido"); return
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nom): messagebox.showerror("Error", "Nombre inválido"); return
        if not re.match(r"^(cf|CF|\d+)$", nit): messagebox.showerror("Error", "NIT inválido"); return
        if not re.match(r"^\d+$", cons_raw): messagebox.showerror("Error", "Consumo inválido"); return

        consumo = float(cons_raw)
        total = (consumo * 1.42) * 1.12

        pdf = FPDF()
        pdf.add_page(); pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "FACTURA ELÉCTRICA", 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"No: {corr} | Cliente: {nom} | NIT: {nit}", 0, 1)
        pdf.cell(0, 10, f"Total a pagar: Q{total:.2f}", 0, 1)

        ruta = f"Facturas/factura_{corr}.pdf"
        pdf.output(ruta)
        
        messagebox.showinfo("PDF", "Factura creada localmente.")

        if email_dest and "@" in email_dest:
            if messagebox.askyesno("Enviar", f"¿Enviar a {email_dest}?"):
                if self.enviar_correo_pdf(email_dest, ruta, corr):
                    messagebox.showinfo("Correo", "Enviado exitosamente")
                else:
                    messagebox.showerror("Correo", "Fallo al enviar. Revise configuración SMTP.")

# --- INICIO ---
crear_directorios()
if not os.path.exists("Configuracion/usuarios.txt"):
    with open("Configuracion/usuarios.txt", "w") as f:
        f.write(f"admin,{encriptar('Admin.2026')}\n")

root = Tk()
app = App(root)
root.mainloop()