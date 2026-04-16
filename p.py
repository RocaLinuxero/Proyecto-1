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

    # Menú principal (solo cliente + factura)
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

    # Generar factura PDF
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

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "EMPRESA ELÉCTRICA", ln=True, align="C")

        pdf.ln(10)

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Correlativo: {self.correlativo.get()}", ln=True)
        pdf.cell(0, 10, f"Nombre: {self.nombre.get()}", ln=True)
        pdf.cell(0, 10, f"NIT: {self.nit.get()}", ln=True)
        pdf.cell(0, 10, f"Contador: {self.contador.get()}", ln=True)
        pdf.cell(0, 10, f"Consumo: {consumo} kWh", ln=True)

        pdf.ln(10)

        pdf.cell(0, 10, f"Precio por kWh: Q{precio_kwh}", ln=True)
        pdf.cell(0, 10, f"TOTAL A PAGAR: Q{total:.2f}", ln=True)

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