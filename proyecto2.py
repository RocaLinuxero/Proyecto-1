import os
from tkinter import *
from tkinter import messagebox
from datetime import datetime

# Crear carpetas
def crear_directorios():
    carpetas = [
        "Configuracion",
        "Clientes",
        "Registros_Consumo",
        "Auditoria_Sistema",
        "Reportes"
    ]
    
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

# Cliente
class Cliente:
    def __init__(self, dpi, nombre, direccion, tipo, tarifa):
        self.dpi = dpi
        self.nombre = nombre
        self.direccion = direccion
        self.tipo = tipo
        self.tarifa = tarifa

    def guardar(self):
        ruta = f"Clientes/{self.dpi}_perfil.txt"

        if os.path.exists(ruta):
            return False

        with open(ruta, "w") as f:
            f.write(f"Nombre:{self.nombre}\n")
            f.write(f"Direccion:{self.direccion}\n")
            f.write(f"Tipo:{self.tipo}\n")
            f.write(f"Tarifa:{self.tarifa}\n")

        return True

# Consumo
class Consumo:
    def __init__(self, dpi, consumo):
        self.dpi = dpi
        self.consumo = consumo
        self.fecha = datetime.now()

    def guardar(self):
        ruta = f"Registros_Consumo/{self.dpi}_consumo.txt"
        alerta = ""

        if self.consumo > 300:
            alerta = "[ALERTA]"

        with open(ruta, "a") as f:
            f.write(f"{self.fecha} - {self.consumo} kWh {alerta}\n")

        return alerta

# Bitácora
def registrar_bitacora(mensaje):
    with open("Auditoria_Sistema/bitacora.txt", "a") as f:
        f.write(f"[{datetime.now()}] {mensaje}\n")

# Login
def verificar_login(user, password):
    if not os.path.exists("Configuracion/usuarios.txt"):
        return False

    with open("Configuracion/usuarios.txt", "r") as f:
        for linea in f:
            u, p = linea.strip().split(",")
            if u == user and p == password:
                return True
    return False

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
        self.user.pack(pady=5)

        Label(frame, text="Contraseña", bg="white").pack()
        self.password = Entry(frame, show="*")
        self.password.pack(pady=5)

        Button(frame, text="Ingresar", bg="#3498db", fg="white",
               command=self.ingresar).pack(pady=10)

    def ingresar(self):
        if verificar_login(self.user.get(), self.password.get()):
            registrar_bitacora(f"{self.user.get()} inició sesión")
            self.menu()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")

    def menu(self):
        self.clear()

        Label(self.root, text="Sistema Empresa Eléctrica",
              font=("Arial", 16, "bold"), bg="#eaf2f8").pack(pady=10)

        # Frame cliente
        frame_cliente = Frame(self.root, bg="white", padx=10, pady=10)
        frame_cliente.pack(pady=5, fill="x", padx=20)

        Label(frame_cliente, text="Registrar Cliente",
              font=("Arial", 12, "bold"), bg="white").grid(row=0, columnspan=2)

        Label(frame_cliente, text="DPI", bg="white").grid(row=1, column=0)
        self.dpi_cliente = Entry(frame_cliente)
        self.dpi_cliente.grid(row=1, column=1)

        Label(frame_cliente, text="Nombre", bg="white").grid(row=2, column=0)
        self.nombre = Entry(frame_cliente)
        self.nombre.grid(row=2, column=1)

        Label(frame_cliente, text="Dirección", bg="white").grid(row=3, column=0)
        self.direccion = Entry(frame_cliente)
        self.direccion.grid(row=3, column=1)

        Label(frame_cliente, text="Tipo", bg="white").grid(row=4, column=0)
        self.tipo = Entry(frame_cliente)
        self.tipo.grid(row=4, column=1)

        Label(frame_cliente, text="Tarifa", bg="white").grid(row=5, column=0)
        self.tarifa = Entry(frame_cliente)
        self.tarifa.grid(row=5, column=1)

        Button(frame_cliente, text="Guardar Cliente", bg="#2ecc71", fg="white",
               command=self.guardar_cliente).grid(row=6, columnspan=2, pady=5)

        # Frame consumo
        frame_consumo = Frame(self.root, bg="white", padx=10, pady=10)
        frame_consumo.pack(pady=5, fill="x", padx=20)

        Label(frame_consumo, text="Registrar Consumo",
              font=("Arial", 12, "bold"), bg="white").grid(row=0, columnspan=2)

        Label(frame_consumo, text="DPI", bg="white").grid(row=1, column=0)
        self.dpi_consumo = Entry(frame_consumo)
        self.dpi_consumo.grid(row=1, column=1)

        Label(frame_consumo, text="Consumo kWh", bg="white").grid(row=2, column=0)
        self.consumo = Entry(frame_consumo)
        self.consumo.grid(row=2, column=1)

        Button(frame_consumo, text="Guardar Consumo", bg="#f39c12", fg="white",
               command=self.guardar_consumo).grid(row=3, columnspan=2, pady=5)

        # Botón reporte
        Button(self.root, text="Generar Reporte", bg="#9b59b6", fg="white",
               command=self.generar_reporte).pack(pady=10)

    def guardar_cliente(self):
        if len(self.dpi_cliente.get()) != 13:
            messagebox.showerror("Error", "DPI inválido")
            return

        try:
            float(self.tarifa.get())
        except:
            messagebox.showerror("Error", "Tarifa inválida")
            return

        cliente = Cliente(
            self.dpi_cliente.get(),
            self.nombre.get(),
            self.direccion.get(),
            self.tipo.get(),
            self.tarifa.get()
        )

        if cliente.guardar():
            registrar_bitacora(f"Cliente {self.dpi_cliente.get()} registrado")
            messagebox.showinfo("Éxito", "Cliente guardado")
        else:
            messagebox.showerror("Error", "Cliente ya existe")

    def guardar_consumo(self):
        try:
            c = float(self.consumo.get())
        except:
            messagebox.showerror("Error", "Dato inválido")
            return

        cons = Consumo(self.dpi_consumo.get(), c)
        alerta = cons.guardar()

        registrar_bitacora(f"Consumo registrado para {self.dpi_consumo.get()}")

        if alerta:
            messagebox.showwarning("Alerta", "Consumo alto detectado")
        else:
            messagebox.showinfo("Éxito", "Consumo guardado")

    def generar_reporte(self):
        dpi = self.dpi_consumo.get()

        ruta_cliente = f"Clientes/{dpi}_perfil.txt"
        ruta_consumo = f"Registros_Consumo/{dpi}_consumo.txt"

        if not os.path.exists(ruta_cliente):
            messagebox.showerror("Error", "Cliente no existe")
            return

        with open(ruta_cliente, "r") as f:
            datos = f.readlines()

        tarifa = 0
        for linea in datos:
            if "Tarifa:" in linea:
                tarifa = float(linea.split(":")[1])

        datos_texto = "".join(datos)

        ultimo_consumo = 0
        ultimo_texto = "Sin datos"

        if os.path.exists(ruta_consumo):
            with open(ruta_consumo, "r") as f:
                lineas = f.readlines()
                if lineas:
                    ultimo_texto = lineas[-1]
                    ultimo_consumo = float(lineas[-1].split("-")[1].split("kWh")[0])

        total = ultimo_consumo * tarifa

        reporte = f"""
EMPRESA ELÉCTRICA

{datos_texto}

Último consumo:
{ultimo_texto}

TOTAL A PAGAR: Q{total:.2f}

Fecha: {datetime.now()}
"""

        with open(f"Reportes/{dpi}_reporte.txt", "w") as f:
            f.write(reporte)

        messagebox.showinfo("Éxito", f"Reporte generado\nTotal: Q{total:.2f}")

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