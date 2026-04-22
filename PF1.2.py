import os
import hashlib
from tkinter import *
from tkinter import messagebox, ttk
from datetime import datetime
from fpdf import FPDF

# COLORES 
COLOR_BG = "#ecf0f1"
COLOR_SECUNDARIO = "#2c3e50"

# HASH 
def encriptar(password):
    return hashlib.sha256(password.encode()).hexdigest()

# DIRECTORIOS 
def crear_directorios():
    for carpeta in ["Configuracion", "Facturas"]:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

# BITÁCORA 
def registrar_bitacora(accion, usuario="Sistema"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("Configuracion/bitacora.txt", "a") as f:
        f.write(f"[{fecha}] ({usuario}) {accion}\n")

# INTENTOS 
def obtener_intentos():
    intentos = {}
    if os.path.exists("Configuracion/intentos.txt"):
        with open("Configuracion/intentos.txt") as f:
            for linea in f:
                u, i = linea.strip().split(",")
                intentos[u] = int(i)
    return intentos

def guardar_intentos(intentos):
    with open("Configuracion/intentos.txt", "w") as f:
        for u, i in intentos.items():
            f.write(f"{u},{i}\n")

# APP 
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Empresa Eléctrica")
        self.root.geometry("700x700")
        self.root.configure(bg=COLOR_BG)
        self.usuario_actual = None
        self.login()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def header(self, texto):
        Label(self.root, text=texto, bg=COLOR_SECUNDARIO,
              fg="white", font=("Arial", 16, "bold")).pack(fill="x", pady=10)

    def eliminar_usuario(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un usuario")
            return

        usuario = self.tabla.item(seleccion[0])["values"][0]

        if usuario == "admin":
            messagebox.showerror("Error", "No puedes eliminar el usuario admin")
            return

        confirm = messagebox.askyesno("Confirmar", f"¿Eliminar usuario {usuario}?")
        if not confirm:
            return

        usuarios = self.obtener_usuarios()

        if usuario in usuarios:
            del usuarios[usuario]

        with open("Configuracion/usuarios.txt", "w") as f:
            for u, p in usuarios.items():
                f.write(f"{u},{p}\n")

        registrar_bitacora(f"Usuario eliminado: {usuario}", self.usuario_actual)

        self.actualizar_tabla()
        messagebox.showinfo("Éxito", "Usuario eliminado")

    # LOGIN 
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
            messagebox.showerror("Bloqueado", "Usuario bloqueado")
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

    # ADMIN
    def modo_administrador(self):
        self.clear()
        self.header("Administrador")

        f = Frame(self.root, bg="white", padx=20, pady=20)
        f.pack()

        Label(f, text="Usuario", bg="white").grid(row=0, column=0)
        self.new_u = Entry(f)
        self.new_u.grid(row=0, column=1)

        Label(f, text="Contraseña", bg="white").grid(row=1, column=0)
        self.new_p = Entry(f, show="*")
        self.new_p.grid(row=1, column=1)

        Label(f, text="Confirmar", bg="white").grid(row=2, column=0)
        self.confirm_p = Entry(f, show="*")
        self.confirm_p.grid(row=2, column=1)

        Button(f, text="Registrar", command=self.guardar_usuario).grid(row=3, columnspan=2)
        Button(f, text="Eliminar Usuario", command=self.eliminar_usuario).grid(row=4, columnspan=2, pady=5)

        self.tabla = ttk.Treeview(self.root, columns=("User", "Hash"), show="headings")
        self.tabla.heading("User", text="Usuario")
        self.tabla.heading("Hash", text="Hash")
        self.tabla.pack(pady=10)

        self.actualizar_tabla()

        Button(self.root, text="Facturación", command=self.menu_facturacion).pack()
        Button(self.root, text="Bitácora", command=self.ver_bitacora).pack()
        Button(self.root, text="Cerrar sesión", command=self.login).pack()

    def guardar_usuario(self):
        u = self.new_u.get()
        p = self.new_p.get()
        cp = self.confirm_p.get()

        if p != cp:
            messagebox.showerror("Error", "Contraseñas no coinciden")
            return

        with open("Configuracion/usuarios.txt", "a") as f:
            f.write(f"{u},{encriptar(p)}\n")

        registrar_bitacora(f"Usuario creado: {u}", self.usuario_actual)
        self.actualizar_tabla()

    def actualizar_tabla(self):
        for i in self.tabla.get_children():
            self.tabla.delete(i)
        for u, p in self.obtener_usuarios().items():
            self.tabla.insert("", END, values=(u, p))

    # FACTURACIÓN 
    def menu_facturacion(self):
        self.clear()
        self.header("Facturación")

        f = Frame(self.root, bg="white", padx=20, pady=20)
        f.pack(pady=20)

        campos = [
            ("Correlativo", "correlativo"),
            ("Nombre", "nombre"),
            ("NIT", "nit"),
            ("Contador", "contador"),
            ("Consumo (kWh)", "consumo")
        ]

        self.entries = {}

        for i, (texto, var) in enumerate(campos):
            Label(f, text=texto, bg="white").grid(row=i, column=0, padx=10, pady=5, sticky="e")
            e = Entry(f, width=30)
            e.grid(row=i, column=1, pady=5)
            self.entries[var] = e

        Button(f, text="Generar Factura", command=self.generar_factura)\
            .grid(row=len(campos), columnspan=2, pady=10)

        Button(self.root, text="Volver", command=self.login)\
            .pack(pady=5)

    # FACTURA
    
    def generar_factura(self):
        import re  # Importante: Asegúrate de que 'import re' esté al inicio de tu archivo

        # 1. Obtener datos de los entries
        correlativo = self.entries["correlativo"].get().strip()
        nombre = self.entries["nombre"].get().strip()
        nit = self.entries["nit"].get().strip()
        contador = self.entries["contador"].get().strip()
        consumo_raw = self.entries["consumo"].get().strip()

        # --- VALIDACIONES ---

        # Correlativo: Solo números enteros positivos incluyendo el 0
        if not re.match(r"^\d+$", correlativo):
            messagebox.showerror("Error", "El Correlativo debe ser un número entero (0 o más).")
            return

        # Nombre: Solo Letras (incluye espacios y tildes)
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre):
            messagebox.showerror("Error", "El Nombre solo permite letras y espacios.")
            return

        # NIT: solo 'cf', 'CF' o números enteros positivos
        if not re.match(r"^(cf|CF|\d+)$", nit):
            messagebox.showerror("Error", "El NIT debe ser un número o 'CF'.")
            return

        # Contador: Letras y números (alfanumérico)
        if not re.match(r"^[a-zA-Z0-9]+$", contador):
            messagebox.showerror("Error", "El Contador solo permite letras y números (sin símbolos).")
            return

        # Consumo: Solo números enteros positivos
        if not re.match(r"^\d+$", consumo_raw):
            messagebox.showerror("Error", "El Consumo debe ser un número entero positivo.")
            return

        # --- PROCESAMIENTO ---
        try:
            consumo = float(consumo_raw)
            precio_kwh = 1.42
            subtotal = consumo * precio_kwh
            iva = subtotal * 0.12
            total = subtotal + iva

            # (El resto de tu código para generar el PDF se mantiene igual...)
            pdf = FPDF()
            pdf.add_page()
            
            
            # --- CÓDIGO DE GUARDADO ---
            pdf.set_font("Arial", "B", 18)
            pdf.cell(0, 10, "EMPRESA ELÉCTRICA", 0, 1, "C")
            
    
            
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, f"Factura No: {correlativo}", 0, 1, "C")
            pdf.cell(0, 8, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, "C")
            pdf.ln(10)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "DATOS DEL CLIENTE", 0, 1)
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 6, f"Nombre: {nombre}", 0, 1)
            pdf.cell(0, 6, f"NIT: {nit}", 0, 1)
            pdf.cell(0, 6, f"Contador: {contador}", 0, 1)
            pdf.ln(10)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(60, 8, "Descripción", 1)
            pdf.cell(40, 8, "Consumo (kWh)", 1)
            pdf.cell(40, 8, "Precio Unit.", 1)
            pdf.cell(40, 8, "Subtotal", 1)
            pdf.ln()
            pdf.set_font("Arial", "", 11)
            pdf.cell(60, 8, "Energía consumida", 1)
            pdf.cell(40, 8, f"{consumo:.2f}", 1)
            pdf.cell(40, 8, f"Q{precio_kwh:.2f}", 1)
            pdf.cell(40, 8, f"Q{subtotal:.2f}", 1)
            pdf.ln()
            pdf.ln(10)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(140, 8, "Subtotal:", 0, 0, "R")
            pdf.cell(40, 8, f"Q{subtotal:.2f}", 0, 1, "R")
            pdf.cell(140, 8, "IVA (12%):", 0, 0, "R")
            pdf.cell(40, 8, f"Q{iva:.2f}", 0, 1, "R")
            pdf.set_font("Arial", "B", 13)
            pdf.cell(140, 10, "TOTAL A PAGAR:", 0, 0, "R")
            pdf.cell(40, 10, f"Q{total:.2f}", 0, 1, "R")
            pdf.ln(10)
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 6, "Gracias por su preferencia", 0, 1, "C")

            ruta = f"Facturas/factura_{correlativo}.pdf"
            pdf.output(ruta)

            registrar_bitacora(
                f"Factura {correlativo} generada | Cliente: {nombre} | Total: Q{total:.2f}",
                self.usuario_actual
            )
            messagebox.showinfo("Éxito", f"Factura generada\nTotal: Q{total:.2f}")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

    def ver_bitacora(self):
        win = Toplevel(self.root)
        t = Text(win)
        t.pack()

        if os.path.exists("Configuracion/bitacora.txt"):
            with open("Configuracion/bitacora.txt") as f:
                t.insert(END, f.read())

#INICIO 
crear_directorios()

if not os.path.exists("Configuracion/usuarios.txt"):
    with open("Configuracion/usuarios.txt", "w") as f:
        f.write(f"admin,{encriptar('1234')}\n")
        f.write(f"admin23,{encriptar('2525')}\n")

root = Tk()
app = App(root)
root.mainloop()