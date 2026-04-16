import os
from tkinter import *
from tkinter import messagebox
from datetime import datetime

# funcion para crear carpetas
def crear_directorios():
    # carpetas necesarias para el sistema
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


# usuario 

class Usuario:
    def __init__(self, user, password):
        self.user = user
        self.password = password

    #guarda usuario en archivo
    def guardar(self):
        with open("Configuracion/usuarios.txt", "a") as f:
            f.write(f"{self.user},{self.password}\n")

# datos del cliente
class Cliente:
    def __init__(self, dpi, nombre, direccion, tipo, tarifa):
        self.dpi = dpi
        self.nombre = nombre
        self.direccion = direccion
        self.tipo = tipo
        self.tarifa = tarifa

    # guarda los datos del cliente en archivo
    def guardar(self):
        ruta = f"Clientes/{self.dpi}_perfil.txt"

        # evita duplicar clientes
        if os.path.exists(ruta):
            return False

        # escribe los datos en el archivo
        with open(ruta, "w") as f:
            f.write(f"Nombre:{self.nombre}\n")
            f.write(f"Direccion:{self.direccion}\n")
            f.write(f"Tipo:{self.tipo}\n")
            f.write(f"Tarifa:{self.tarifa}\n")

        return True


# clase de consumo

class Consumo:
    def __init__(self, dpi, consumo):
        self.dpi = dpi
        self.consumo = consumo
        self.fecha = datetime.now()  # Fecha actual automática

    # guarda el consumo del cliente
    def guardar(self):
        ruta = f"Registros_Consumo/{self.dpi}_consumo.txt"
        alerta = ""

        # si el consumo es alto, se marca alerta
        if self.consumo > 300:
            alerta = "[ALERTA]"

        # se guarda el registro
        with open(ruta, "a") as f:
            f.write(f"{self.fecha} - {self.consumo} kWh {alerta}\n")

        return alerta


# bitacora

def registrar_bitacora(mensaje):
    # Guarda acciones importantes del sistema
    with open("Auditoria_Sistema/bitacora.txt", "a") as f:
        f.write(f"[{datetime.now()}] {mensaje}\n")

# verificacion de LOGIN

def verificar_login(user, password):
    # Si no existe archivo, no hay usuarios
    if not os.path.exists("Configuracion/usuarios.txt"):
        return False

    # Se revisan los usuarios guardados
    with open("Configuracion/usuarios.txt", "r") as f:
        for linea in f:
            u, p = linea.strip().split(",")
            if u == user and p == password:
                return True
    return False


# INTERFAZ

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Empresa Eléctrica")

        # Inicia con pantalla de login
        self.login()

    
    # pantalla de LOGIN
    
    def login(self):
        self.clear()

        Label(self.root, text="Usuario").pack()
        self.user = Entry(self.root)
        self.user.pack()

        Label(self.root, text="Contraseña").pack()
        self.password = Entry(self.root, show="*")
        self.password.pack()

        Button(self.root, text="Login", command=self.ingresar).pack()

    # verifica acceso
    def ingresar(self):
        if verificar_login(self.user.get(), self.password.get()):
            registrar_bitacora(f"{self.user.get()} inició sesión")
            self.menu()
        else:
            messagebox.showerror("Error", "Credenciales inválidas")

    
    # MENU PRINCIPAL
   
    def menu(self):
        self.clear()

        Button(self.root, text="Registrar Cliente", command=self.registrar_cliente).pack()
        Button(self.root, text="Registrar Consumo", command=self.registrar_consumo).pack()
        Button(self.root, text="Generar Reporte", command=self.reporte).pack()

    
    # REGISTRAR CLIENTE

    def registrar_cliente(self):
        self.clear()

        Label(text="DPI").pack()
        dpi = Entry(self.root)
        dpi.pack()

        Label(text="Nombre").pack()
        nombre = Entry(self.root)
        nombre.pack()

        Label(text="Dirección").pack()
        direccion = Entry(self.root)
        direccion.pack()

        Label(text="Tipo").pack()
        tipo = Entry(self.root)
        tipo.pack()

        Label(text="Tarifa").pack()
        tarifa = Entry(self.root)
        tarifa.pack()

        def guardar():
            # Validación de DPI
            if len(dpi.get()) != 13:
                messagebox.showerror("Error", "DPI inválido")
                return

            cliente = Cliente(dpi.get(), nombre.get(), direccion.get(), tipo.get(), tarifa.get())

            if cliente.guardar():
                registrar_bitacora(f"Cliente {dpi.get()} registrado")
                messagebox.showinfo("Éxito", "Cliente guardado")
            else:
                messagebox.showerror("Error", "Cliente ya existe")

        Button(self.root, text="Guardar", command=guardar).pack()
        Button(self.root, text="Volver", command=self.menu).pack()

    
    # REGISTRO DE CONSUMO
   
    def registrar_consumo(self):
        self.clear()

        Label(text="DPI").pack()
        dpi = Entry(self.root)
        dpi.pack()

        Label(text="Consumo kWh").pack()
        consumo = Entry(self.root)
        consumo.pack()

        def guardar():
            try:
                c = float(consumo.get())
            except:
                messagebox.showerror("Error", "Dato inválido")
                return

            cons = Consumo(dpi.get(), c)
            alerta = cons.guardar()

            registrar_bitacora(f"Consumo registrado para {dpi.get()}")

            if alerta:
                messagebox.showwarning("Alerta", "Consumo alto detectado")
            else:
                messagebox.showinfo("Éxito", "Consumo guardado")

        Button(self.root, text="Guardar", command=guardar).pack()
        Button(self.root, text="Volver", command=self.menu).pack()

   
    # GENERAR EL REPORTE
    
    def reporte(self):
        self.clear()

        Label(text="DPI").pack()
        dpi = Entry(self.root)
        dpi.pack()

        def generar():
            ruta_cliente = f"Clientes/{dpi.get()}_perfil.txt"
            ruta_consumo = f"Registros_Consumo/{dpi.get()}_consumo.txt"

            # verifica existencia del cliente
            if not os.path.exists(ruta_cliente):
                messagebox.showerror("Error", "Cliente no existe")
                return

            # lee datos del cliente
            with open(ruta_cliente, "r") as f:
                datos = f.read()

            # obtiene último consumo
            ultimo = "Sin datos"
            if os.path.exists(ruta_consumo):
                with open(ruta_consumo, "r") as f:
                    lineas = f.readlines()
                    if lineas:
                        ultimo = lineas[-1]

            # construye reporte
            reporte = f"""
EMPRESA ELÉCTRICA

{datos}

Último consumo:
{ultimo}
Fecha: {datetime.now()}
"""

            # guarda reporte
            with open(f"Reportes/{dpi.get()}_reporte.txt", "w") as f:
                f.write(reporte)

            messagebox.showinfo("Éxito", "Reporte generado")

        Button(self.root, text="Generar", command=generar).pack()
        Button(self.root, text="Volver", command=self.menu).pack()

    # limpia la pantalla
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# INICIO DEL PROGRAMA
crear_directorios()


if not os.path.exists("Configuracion/usuarios.txt"):
    admin = Usuario("admin", "1234")
    admin.guardar()

# Ejecuta interfaz gráfica
root = Tk()
app = App(root)
root.mainloop()