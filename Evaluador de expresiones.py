# =====================================================
#  EVALUADOR DE EXPRESIONES POSFIJAS Y PREFIJAS (con pila)
#  Versión con INTERFAZ GRÁFICA (tkinter)
# =====================================================
import tkinter as tk
from tkinter import ttk


# ---------- 1. La clase Pila ----------
# Una pila es como una pila de platos: solo puedes poner
# o quitar el plato de ARRIBA (el último que entró).
class Pila:
    def __init__(self):
        self.items = []            # aquí se guardan los datos

    def push(self, x):             # poner un dato arriba
        self.items.append(x)

    def pop(self):                 # quitar y devolver el de arriba
        return self.items.pop()

    def peek(self):                # ver el de arriba sin quitarlo
        return self.items[-1]

    def esta_vacia(self):          # ¿no hay nada?
        return len(self.items) == 0

    def tamano(self):              # ¿cuántos datos hay?
        return len(self.items)


# ---------- 2. Funciones de ayuda ----------
OPERADORES = ["+", "-", "*", "/", "^"]

def calcular(a, operador, b):
    # Hace la operación "a operador b"
    if operador == "+":
        return a + b
    if operador == "-":
        return a - b
    if operador == "*":
        return a * b
    if operador == "/":
        return a / b               # si b es 0, Python da error ZeroDivisionError
    if operador == "^":
        return a ** b

def limpiar(numero):
    # Para que se vea 14 en vez de 14.0
    if isinstance(numero, float) and numero.is_integer():
        return int(numero)
    return numero


# ---------- 3. Notación POSFIJA ----------
# Ejemplo: 3 4 +   (el operador va DESPUÉS de los números)
# Se lee de IZQUIERDA a DERECHA.
# "pasos" es una lista donde guardamos cada paso: (texto, copia de la pila)
def evaluar_posfija(expresion, pasos):
    pila = Pila()
    for token in expresion.split():
        if token in OPERADORES:
            b = pila.pop()                     # el primero que sale es el de la derecha
            a = pila.pop()                     # el segundo es el de la izquierda
            resultado = limpiar(calcular(a, token, b))
            pila.push(resultado)
            pasos.append((f"{a} {token} {b} = {resultado}", list(pila.items)))
        else:
            pila.push(limpiar(float(token)))
            pasos.append((f"Entra {token}", list(pila.items)))

    if pila.tamano() != 1:                     # al final debe quedar UN solo dato
        raise ValueError("expresión mal formada")
    return pila.pop()


# ---------- 4. Notación PREFIJA ----------
# Ejemplo: + 3 4   (el operador va ANTES de los números)
# Se lee de DERECHA a IZQUIERDA (por eso usamos reversed).
def evaluar_prefija(expresion, pasos):
    pila = Pila()
    for token in reversed(expresion.split()):
        if token in OPERADORES:
            a = pila.pop()                     # aquí el primero que sale es el IZQUIERDO
            b = pila.pop()                     # y el segundo es el derecho
            resultado = limpiar(calcular(a, token, b))
            pila.push(resultado)
            pasos.append((f"{a} {token} {b} = {resultado}", list(pila.items)))
        else:
            pila.push(limpiar(float(token)))
            pasos.append((f"Entra {token}", list(pila.items)))

    if pila.tamano() != 1:
        raise ValueError("expresión mal formada")
    return pila.pop()


# ---------- 5. Interfaz gráfica ----------
EJEMPLOS = {"posfija": "3 4 + 2 *", "prefija": "* + 3 4 2"}

class App:
    ALTO_CAJA = 32          # alto de cada "plato" dibujado en la pila
    MAX_CAJAS = 11          # cuántos platos caben en el dibujo

    def __init__(self, root):
        self.root = root
        root.title("Evaluador de expresiones posfijas y prefijas")
        root.geometry("760x520")
        root.minsize(680, 460)

        self.modo = tk.StringVar(value="posfija")
        self.pasos = []                         # pasos de la última evaluación

        # --- Zona de arriba: tipo de notación + expresión ---
        arriba = ttk.Frame(root, padding=10)
        arriba.pack(fill="x")

        ttk.Radiobutton(arriba, text="Posfija (ej: 3 4 + 2 *)", variable=self.modo,
                        value="posfija").grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(arriba, text="Prefija (ej: * + 3 4 2)", variable=self.modo,
                        value="prefija").grid(row=0, column=1, sticky="w", padx=15)

        ttk.Label(arriba, text="Expresión (con espacios entre cada parte):").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(10, 2))

        self.entrada = ttk.Entry(arriba, font=("Consolas", 13))
        self.entrada.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.entrada.bind("<Return>", lambda e: self.evaluar())
        self.entrada.focus()

        ttk.Button(arriba, text="Evaluar", command=self.evaluar).grid(
            row=2, column=2, padx=(8, 0))
        ttk.Button(arriba, text="Ejemplo", command=self.poner_ejemplo).grid(
            row=2, column=3, padx=(4, 0))
        ttk.Button(arriba, text="Limpiar", command=self.limpiar_todo).grid(
            row=2, column=4, padx=(4, 0))
        arriba.columnconfigure(1, weight=1)

        # --- Zona de en medio: lista de pasos + dibujo de la pila ---
        medio = ttk.Frame(root, padding=(10, 0, 10, 0))
        medio.pack(fill="both", expand=True)

        izq = ttk.LabelFrame(medio, text="Paso a paso (haz clic en un paso)")
        izq.pack(side="left", fill="both", expand=True)

        self.lista = tk.Listbox(izq, font=("Consolas", 12), activestyle="none",
                                exportselection=False)
        barra = ttk.Scrollbar(izq, orient="vertical", command=self.lista.yview)
        self.lista.configure(yscrollcommand=barra.set)
        self.lista.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        barra.pack(side="right", fill="y", pady=6)
        self.lista.bind("<<ListboxSelect>>", self.al_elegir_paso)

        der = ttk.LabelFrame(medio, text="La pila en ese paso")
        der.pack(side="right", fill="y", padx=(10, 0))

        self.canvas = tk.Canvas(der, width=210, height=self.ALTO_CAJA * self.MAX_CAJAS + 50,
                                bg="white", highlightthickness=0)
        self.canvas.pack(padx=6, pady=6)

        # --- Zona de abajo: resultado ---
        self.resultado = ttk.Label(root, text="", font=("Segoe UI", 15, "bold"), padding=10)
        self.resultado.pack(fill="x")

        self.dibujar_pila([])

    # ----- Acciones de los botones -----
    def poner_ejemplo(self):
        self.entrada.delete(0, "end")
        self.entrada.insert(0, EJEMPLOS[self.modo.get()])

    def limpiar_todo(self):
        self.entrada.delete(0, "end")
        self.lista.delete(0, "end")
        self.pasos = []
        self.resultado.config(text="")
        self.dibujar_pila([])
        self.entrada.focus()

    def evaluar(self):
        expresion = self.entrada.get()
        self.pasos = []
        self.lista.delete(0, "end")

        error = None
        valor = None
        try:
            if self.modo.get() == "posfija":
                valor = evaluar_posfija(expresion, self.pasos)
            else:
                valor = evaluar_prefija(expresion, self.pasos)
        except ZeroDivisionError:
            error = "Error: no se puede dividir entre cero"
        except (ValueError, IndexError):
            error = "Error: la expresión está mal escrita"
        except OverflowError:
            error = "Error: el número es demasiado grande"

        # Mostrar los pasos (aunque haya error, se ven los que alcanzó a hacer)
        for i, (texto, _pila) in enumerate(self.pasos, start=1):
            self.lista.insert("end", f"{i:>2}. {texto}")

        if self.pasos:
            ultimo = len(self.pasos) - 1
            self.lista.selection_set(ultimo)
            self.lista.see(ultimo)
            self.dibujar_pila(self.pasos[ultimo][1])
        else:
            self.dibujar_pila([])

        if error:
            self.resultado.config(text=error, foreground="#c0392b")
        else:
            self.resultado.config(text=f"RESULTADO: {valor}", foreground="#1e8449")

    def al_elegir_paso(self, _evento):
        seleccion = self.lista.curselection()
        if seleccion:
            self.dibujar_pila(self.pasos[seleccion[0]][1])

    # ----- Dibujo de la pila -----
    def dibujar_pila(self, items):
        c = self.canvas
        c.delete("all")
        x1, x2 = 40, 170
        base = self.ALTO_CAJA * self.MAX_CAJAS + 30     # y del fondo de la pila

        # El "piso" de la pila
        c.create_line(x1 - 15, base, x2 + 15, base, width=3, fill="#444")

        visibles = items[-self.MAX_CAJAS:]              # si hay muchos, se ven los de arriba
        for i, valor in enumerate(visibles):
            y2 = base - i * self.ALTO_CAJA
            y1 = y2 - self.ALTO_CAJA + 4
            es_tope = (i == len(visibles) - 1)
            c.create_rectangle(x1, y1, x2, y2, fill="#f9e79f" if es_tope else "#d6eaf8",
                               outline="#2c3e50", width=2)
            c.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(valor),
                          font=("Consolas", 13, "bold"), fill="#1b2631")
            if es_tope:
                c.create_text(x2 + 8, (y1 + y2) // 2, text="← tope", anchor="w",
                              font=("Segoe UI", 9), fill="#7f8c8d")

        if not items:
            c.create_text((x1 + x2) // 2, base - 20, text="(pila vacía)",
                          font=("Segoe UI", 10, "italic"), fill="#7f8c8d")
        elif len(items) > self.MAX_CAJAS:
            c.create_text((x1 + x2) // 2, 12, text=f"... {len(items)} datos en total",
                          font=("Segoe UI", 9), fill="#7f8c8d")


if __name__ == "__main__":
    ventana = tk.Tk()
    App(ventana)
    ventana.mainloop()