import os
from tkinter import *
from tkinter import messagebox
from datetime import datetime
from fpdf import FPDF

# Crear carpetas
def crear_directorios():
    carpetas = ["Configuracion", "Clientes", "Facturas"]
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

# Usuario
class Usuario:
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def guardar(self):
        with open("Configuracion/usuarios.txt", "a") as f:
            f.write(f"{self.user},{self.password}\n")

# Interfaz
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Empresa Eléctrica")
        self.root.geometry("500x600")
        self.root.configure(bg="#eaf2f8")

        self.login()

    def login(self):
        self.clear()

        frame = Frame(self.root, bg="white", padx=20, pady=20)
        frame.pack(pady=100)

        Label(frame, text="INICIO DE SESIÓN", font=("Arial", 14, "bold"), bg="white").pack(pady=10)

        Label(frame, text="Usuario", bg="white").pack()
        self.user = Entry(frame)
        self.user.pack()

        Label(frame, text="Contraseña", bg="white").pack()
        self.password = Entry(frame, show="*")
        self.password.pack()

        Button(frame, text="Ingresar", bg="#3498db", fg="white",
               command=self.menu).pack(pady=10)

    def menu(self):
        self.clear()

        Label(self.root, text="Ingrese datos del cliente",
              font=("Arial", 16, "bold"), bg="#eaf2f8").pack(pady=10)

        frame = Frame(self.root, bg="white", padx=10, pady=10)
        frame.pack(pady=10, padx=20)

        Label(frame, text="Correlativo").grid(row=0, column=0)
        self.correlativo = Entry(frame)
        self.correlativo.grid(row=0, column=1)

        Label(frame, text="Nombre").grid(row=1, column=0)
        self.nombre = Entry(frame)
        self.nombre.grid(row=1, column=1)

        Label(frame, text="NIT").grid(row=2, column=0)
        self.nit = Entry(frame)
        self.nit.grid(row=2, column=1)

        Label(frame, text="Contador").grid(row=3, column=0)
        self.contador = Entry(frame)
        self.contador.grid(row=3, column=1)

        Label(frame, text="Consumo (kWh)").grid(row=4, column=0)
        self.consumo = Entry(frame)
        self.consumo.grid(row=4, column=1)

        Button(frame, text="Generar Factura", bg="#27ae60", fg="white",
               command=self.generar_factura).grid(row=5, columnspan=2, pady=10)


    def generar_factura(self):
        try:
            consumo = float(self.consumo.get())
        except:
            messagebox.showerror("Error", "El consumo debe ser numérico")
            return

        precio_kwh = 1.42
        total = consumo * precio_kwh

        pdf = FPDF()
        pdf.add_page()

        # LOGO
        pdf.image("imagen1.png", x=10, y=8, w=30)

        # TÍTULO
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "EMPRESA ELÉCTRICA", 0, 1, "C")

        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 5, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", 0, 1, "R")

        pdf.ln(10)

        # DATOS CLIENTE
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "DATOS DEL CLIENTE", 1, 1, "C")

        pdf.set_font("Arial", "", 11)
        pdf.cell(50, 8, "Correlativo:", 1)
        pdf.cell(0, 8, self.correlativo.get(), 1, 1)

        pdf.cell(50, 8, "Nombre:", 1)
        pdf.cell(0, 8, self.nombre.get(), 1, 1)

        pdf.cell(50, 8, "NIT:", 1)
        pdf.cell(0, 8, self.nit.get(), 1, 1)

        pdf.cell(50, 8, "Contador:", 1)
        pdf.cell(0, 8, self.contador.get(), 1, 1)

        pdf.ln(5)

        # CONSUMO
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "DETALLE DE CONSUMO", 1, 1, "C")

        pdf.set_font("Arial", "", 11)
        pdf.cell(100, 8, "Consumo (kWh)", 1)
        pdf.cell(0, 8, f"{consumo}", 1, 1)

        pdf.ln(5)

        # FACTURACIÓN
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "FACTURACIÓN", 1, 1, "C")

        pdf.set_font("Arial", "B", 11)
        pdf.cell(90, 8, "Descripción", 1)
        pdf.cell(50, 8, "Precio Unitario", 1)
        pdf.cell(0, 8, "Total", 1, 1)

        pdf.set_font("Arial", "", 11)
        pdf.cell(90, 8, "Consumo de Energía", 1)
        pdf.cell(50, 8, f"Q{precio_kwh}", 1)
        pdf.cell(0, 8, f"Q{total:.2f}", 1, 1)

        pdf.set_font("Arial", "B", 12)
        pdf.cell(140, 10, "TOTAL A PAGAR", 1)
        pdf.cell(0, 10, f"Q{total:.2f}", 1, 1)

        ruta = f"Facturas/factura_{self.correlativo.get()}.pdf"
        pdf.output(ruta)

        messagebox.showinfo("Éxito", f"Factura generada\n{ruta}")

    
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Inicio
crear_directorios()

if not os.path.exists("Configuracion/usuarios.txt"):
    Usuario("admin", "1234").guardar()

root = Tk()
app = App(root)
root.mainloop()
