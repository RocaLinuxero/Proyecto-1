import os
import hashlib
import re
from tkinter import *
from tkinter import messagebox, ttk
from datetime import datetime
from fpdf import FPDF

# --- CONFIGURACIÓN Y COLORES ---
COLOR_BG = "#ecf0f1"
COLOR_SECUNDARIO = "#2c3e50"

# --- FUNCIONES DE SEGURIDAD ---
def encriptar(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validar_password_segura(password):
    """Verifica que la contraseña cumpla con estándares de seguridad."""
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "Debe incluir al menos una letra mayúscula."
    if not re.search(r"[a-z]", password):
        return False, "Debe incluir al menos una letra minúscula."
    if not re.search(r"\d", password):
        return False, "Debe incluir al menos un número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Debe incluir al menos un carácter especial (@, #, $, etc.)."
    return True, ""

# --- GESTIÓN DE ARCHIVOS ---
def crear_directorios():
    for carpeta in ["Configuracion", "Facturas"]:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

def registrar_bitacora(accion, usuario="Sistema"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("Configuracion/bitacora.txt", "a") as f:
        f.write(f"[{fecha}] ({usuario}) {accion}\n")

def obtener_intentos():
    intentos = {}
    if os.path.exists("Configuracion/intentos.txt"):
        with open("Configuracion/intentos.txt") as f:
            for linea in f:
                try:
                    u, i = linea.strip().split(",")
                    intentos[u] = int(i)
                except: continue
    return intentos

def guardar_intentos(intentos):
    with open("Configuracion/intentos.txt", "w") as f:
        for u, i in intentos.items():
            f.write(f"{u},{i}\n")

# --- CLASE PRINCIPAL ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Empresa Eléctrica")
        self.root.geometry("700x750")
        self.root.configure(bg=COLOR_BG)
        self.usuario_actual = None
        self.login()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

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
        Button(f, text="Ingresar", command=self.validar_acceso).pack(pady=10)

    def obtener_usuarios(self):
        usuarios = {}
        if os.path.exists("Configuracion/usuarios.txt"):
            with open("Configuracion/usuarios.txt") as f:
                for linea in f:
                    u, p = linea.strip().split(",")
                    usuarios[u] = p
        return usuarios

    def validar_acceso(self):
        user = self.ent_user.get()
        pas = self.ent_pass.get()
        db = self.obtener_usuarios()
        intentos = obtener_intentos()

        if user in intentos and intentos[user] >= 3:
            messagebox.showerror("Bloqueado", "Usuario bloqueado por intentos fallidos")
            return

        if user in db and (db[user] == encriptar(pas) or db[user] == pas):
            self.usuario_actual = user
            registrar_bitacora("Inicio de sesión", user)
            intentos[user] = 0
            guardar_intentos(intentos)
            if user in ["admin", "admin23"]:
                self.modo_administrador()
            else:
                self.menu_facturacion()
            return

        intentos[user] = intentos.get(user, 0) + 1
        guardar_intentos(intentos)
        messagebox.showerror("Error", "Datos incorrectos")

    # --- ADMINISTRACIÓN ---
    def modo_administrador(self):
        self.clear()
        self.header("Panel Administrador")
        f = Frame(self.root, bg="white", padx=20, pady=20)
        f.pack()
        Label(f, text="Nuevo Usuario", bg="white").grid(row=0, column=0)
        self.new_u = Entry(f)
        self.new_u.grid(row=0, column=1)
        Label(f, text="Contraseña", bg="white").grid(row=1, column=0)
        self.new_p = Entry(f, show="*")
        self.new_p.grid(row=1, column=1)
        Label(f, text="Confirmar", bg="white").grid(row=2, column=0)
        self.confirm_p = Entry(f, show="*")
        self.confirm_p.grid(row=2, column=1)
        Button(f, text="Registrar Usuario", command=self.guardar_usuario).grid(row=3, columnspan=2, pady=10)
        
        self.tabla = ttk.Treeview(self.root, columns=("User", "Hash"), show="headings")
        self.tabla.heading("User", text="Usuario")
        self.tabla.heading("Hash", text="Hash (Seguridad)")
        self.tabla.pack(pady=10)
        self.actualizar_tabla()

        Button(self.root, text="Eliminar Usuario Seleccionado", command=self.eliminar_usuario).pack()
        Button(self.root, text="Ir a Facturación", command=self.menu_facturacion).pack(pady=5)
        Button(self.root, text="Cerrar sesión", command=self.login).pack()

    def guardar_usuario(self):
        u = self.new_u.get()
        p = self.new_p.get()
        cp = self.confirm_p.get()
        if p != cp:
            messagebox.showerror("Error", "Contraseñas no coinciden")
            return
        es_segura, mensaje = validar_password_segura(p)
        if not es_segura:
            messagebox.showwarning("Seguridad", mensaje)
            return
        with open("Configuracion/usuarios.txt", "a") as f:
            f.write(f"{u},{encriptar(p)}\n")
        registrar_bitacora(f"Usuario creado: {u}", self.usuario_actual)
        self.actualizar_tabla()
        messagebox.showinfo("Éxito", "Usuario registrado")

    def actualizar_tabla(self):
        for i in self.tabla.get_children(): self.tabla.delete(i)
        for u, p in self.obtener_usuarios().items():
            self.tabla.insert("", END, values=(u, p))

    def eliminar_usuario(self):
        seleccion = self.tabla.selection()
        if not seleccion: return
        usuario = self.tabla.item(seleccion[0])["values"][0]
        if usuario == "admin": 
            messagebox.showerror("Error", "No se puede eliminar al admin")
            return
        usuarios = self.obtener_usuarios()
        del usuarios[usuario]
        with open("Configuracion/usuarios.txt", "w") as f:
            for u, p in usuarios.items(): f.write(f"{u},{p}\n")
        self.actualizar_tabla()

    # --- FACTURACIÓN ---
    def menu_facturacion(self):
        self.clear()
        # Barra de herramientas superior
        nav = Frame(self.root, bg=COLOR_BG)
        nav.pack(fill="x", padx=10, pady=5)
        Button(nav, text="⚙️ Configuración de Usuario", command=self.cambiar_password_window).pack(side="left")
        
        self.header("Módulo de Facturación")
        f = Frame(self.root, bg="white", padx=20, pady=20)
        f.pack(pady=20)

        campos = [("Correlativo", "correlativo"), ("Nombre", "nombre"), 
                  ("NIT", "nit"), ("Contador", "contador"), ("Consumo (kWh)", "consumo")]
        self.entries = {}
        for i, (texto, var) in enumerate(campos):
            Label(f, text=texto, bg="white").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            e = Entry(f, width=30)
            e.grid(row=i, column=1, pady=5)
            self.entries[var] = e

        Button(f, text="Generar Factura PDF", command=self.generar_factura, 
               bg="#27ae60", fg="white", font=("Arial", 10, "bold")).grid(row=len(campos), columnspan=2, pady=20)
        Button(self.root, text="Cerrar Sesión / Volver", command=self.login).pack()

    # --- CONFIGURACIÓN DE USUARIO (CAMBIAR PASS) ---
    def cambiar_password_window(self):
        win = Toplevel(self.root)
        win.title("Cambiar Contraseña")
        win.geometry("400x400")
        win.grab_set()
        
        Label(win, text="Actualizar Seguridad", font=("Arial", 12, "bold")).pack(pady=10)
        
        Label(win, text="Contraseña Actual").pack()
        ent_act = Entry(win, show="*")
        ent_act.pack()
        
        Label(win, text="Nueva Contraseña").pack(pady=(10,0))
        ent_n1 = Entry(win, show="*")
        ent_n1.pack()
        
        Label(win, text="Confirmar Nueva Contraseña").pack()
        ent_n2 = Entry(win, show="*")
        ent_n2.pack()

        def confirmar_cambio():
            usuarios = self.obtener_usuarios()
            if encriptar(ent_act.get()) != usuarios[self.usuario_actual]:
                messagebox.showerror("Error", "La contraseña actual no es correcta")
                return
            if ent_n1.get() != ent_n2.get():
                messagebox.showerror("Error", "Las nuevas contraseñas no coinciden")
                return
            
            es_segura, mensaje = validar_password_segura(ent_n1.get())
            if not es_segura:
                messagebox.showwarning("Seguridad", mensaje)
                return

            usuarios[self.usuario_actual] = encriptar(ent_n1.get())
            with open("Configuracion/usuarios.txt", "w") as f:
                for u, p in usuarios.items(): f.write(f"{u},{p}\n")
            
            registrar_bitacora("Cambio de contraseña", self.usuario_actual)
            messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
            win.destroy()

        Button(win, text="Guardar Cambios", command=confirmar_cambio, bg=COLOR_SECUNDARIO, fg="white").pack(pady=20)

    # --- GENERACIÓN DE FACTURA ---
    def generar_factura(self):
        # Obtener datos
        corr = self.entries["correlativo"].get().strip()
        nom = self.entries["nombre"].get().strip()
        nit = self.entries["nit"].get().strip()
        cont = self.entries["contador"].get().strip()
        cons_raw = self.entries["consumo"].get().strip()

        # Validaciones con Regex
        if not re.match(r"^\d+$", corr):
            messagebox.showerror("Error", "Correlativo: solo números enteros positivos")
            return
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nom):
            messagebox.showerror("Error", "Nombre: solo letras y espacios")
            return
        if not re.match(r"^(cf|CF|\d+)$", nit):
            messagebox.showerror("Error", "NIT: solo números o 'CF'")
            return
        if not re.match(r"^[a-zA-Z0-9]+$", cont):
            messagebox.showerror("Error", "Contador: solo letras y números")
            return
        if not re.match(r"^\d+$", cons_raw):
            messagebox.showerror("Error", "Consumo: solo números enteros")
            return

        # Cálculos
        consumo = float(cons_raw)
        precio_kwh = 1.42
        subtotal = consumo * precio_kwh
        iva = subtotal * 0.12
        total = subtotal + iva

        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 18)
        pdf.cell(0, 10, "EMPRESA ELÉCTRICA S.A.", 0, 1, "C")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"Factura No: {corr}", 0, 1, "C")
        pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "C")
        pdf.ln(10)
        
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "DATOS DEL CLIENTE", 0, 1)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 6, f"Nombre: {nom}", 0, 1)
        pdf.cell(0, 6, f"NIT: {nit}", 0, 1)
        pdf.cell(0, 6, f"ID Contador: {cont}", 0, 1)
        pdf.ln(10)

        # Tabla
        pdf.set_font("Arial", "B", 11)
        pdf.cell(60, 8, "Descripción", 1); pdf.cell(40, 8, "Consumo", 1); 
        pdf.cell(40, 8, "Precio U.", 1); pdf.cell(40, 8, "Subtotal", 1); pdf.ln()
        pdf.set_font("Arial", "", 11)
        pdf.cell(60, 8, "Servicio Eléctrico", 1); pdf.cell(40, 8, f"{consumo} kWh", 1); 
        pdf.cell(40, 8, f"Q{precio_kwh}", 1); pdf.cell(40, 8, f"Q{subtotal:.2f}", 1); pdf.ln()
        
        pdf.ln(5)
        pdf.cell(140, 8, "IVA (12%):", 0, 0, "R"); pdf.cell(40, 8, f"Q{iva:.2f}", 0, 1, "R")
        pdf.set_font("Arial", "B", 14)
        pdf.cell(140, 10, "TOTAL:", 0, 0, "R"); pdf.cell(40, 10, f"Q{total:.2f}", 0, 1, "R")

        ruta = f"Facturas/factura_{corr}.pdf"
        pdf.output(ruta)
        registrar_bitacora(f"Factura {corr} creada para {nom}", self.usuario_actual)
        messagebox.showinfo("Éxito", f"Factura generada en {ruta}")

# --- INICIO DE LA APLICACIÓN ---
crear_directorios()
if not os.path.exists("Configuracion/usuarios.txt"):
    with open("Configuracion/usuarios.txt", "w") as f:
        f.write(f"admin,{encriptar('Admin.2026')}\n") # Password inicial segura

root = Tk()
app = App(root)
root.mainloop()