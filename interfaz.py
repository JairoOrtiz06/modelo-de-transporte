import tkinter as tk
from tkinter import messagebox, ttk

from graficas import grafica_demanda, grafica_oferta
from modelos import ProblemaTransporte
from transporte import resolver_problema
from validaciones import convertir_numero, validar_balance, validar_matriz


class AplicacionTransporte:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema de Transporte - Metodo de Costo Minimo")
        self.ventana.geometry("1180x760")
        self.ventana.minsize(940, 640)
        self.ventana.configure(bg="#0F172A")

        self.produccion_vars = []
        self.venta_vars = []
        self.oferta_vars = []
        self.demanda_vars = []
        self.distancia_vars = []
        self.ultimo_problema = None

        self._configurar_estilos()
        self._crear_interfaz()
        self.generar_formulario()

    def _configurar_estilos(self):
        self.colores = {
            "fondo": "#0F172A",
            "panel": "#FFFFFF",
            "panel_suave": "#F8FAFC",
            "texto": "#0F172A",
            "texto_suave": "#475569",
            "primario": "#2563EB",
            "primario_oscuro": "#1D4ED8",
            "acento": "#14B8A6",
            "borde": "#CBD5E1",
            "tabla": "#EEF2FF",
        }

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("App.TFrame", background=self.colores["fondo"])
        estilo.configure("Scroll.TFrame", background=self.colores["fondo"])
        estilo.configure("Panel.TFrame", background=self.colores["panel"])
        estilo.configure("Soft.TFrame", background=self.colores["panel_suave"])
        estilo.configure(
            "Titulo.TLabel",
            background=self.colores["fondo"],
            foreground="#F8FAFC",
            font=("Segoe UI", 22, "bold")
        )
        estilo.configure(
            "Intro.TLabel",
            background=self.colores["fondo"],
            foreground="#CBD5E1",
            font=("Segoe UI", 10)
        )
        estilo.configure(
            "Subtitulo.TLabel",
            background=self.colores["panel"],
            foreground=self.colores["texto"],
            font=("Segoe UI", 13, "bold")
        )
        estilo.configure(
            "TLabel",
            background=self.colores["panel"],
            foreground=self.colores["texto_suave"],
            font=("Segoe UI", 10)
        )
        estilo.configure(
            "TEntry",
            fieldbackground="#FFFFFF",
            foreground=self.colores["texto"],
            bordercolor=self.colores["borde"],
            lightcolor=self.colores["borde"],
            darkcolor=self.colores["borde"],
            padding=5
        )
        estilo.configure(
            "TSpinbox",
            fieldbackground="#FFFFFF",
            foreground=self.colores["texto"],
            bordercolor=self.colores["borde"],
            padding=5
        )
        estilo.configure(
            "TButton",
            background=self.colores["primario"],
            foreground="#FFFFFF",
            bordercolor=self.colores["primario"],
            focusthickness=0,
            font=("Segoe UI", 10, "bold"),
            padding=(12, 7)
        )
        estilo.map(
            "TButton",
            background=[("active", self.colores["primario_oscuro"])],
            foreground=[("active", "#FFFFFF")]
        )
        estilo.configure(
            "Secondary.TButton",
            background="#E2E8F0",
            foreground=self.colores["texto"],
            bordercolor="#E2E8F0"
        )
        estilo.map("Secondary.TButton", background=[("active", "#CBD5E1")])
        estilo.configure(
            "Treeview",
            background="#FFFFFF",
            fieldbackground="#FFFFFF",
            foreground=self.colores["texto"],
            rowheight=28,
            bordercolor=self.colores["borde"],
            font=("Segoe UI", 9)
        )
        estilo.configure(
            "Treeview.Heading",
            background=self.colores["tabla"],
            foreground=self.colores["texto"],
            bordercolor=self.colores["borde"],
            font=("Segoe UI", 9, "bold")
        )
        estilo.map("Treeview", background=[("selected", self.colores["acento"])])

    def _crear_interfaz(self):
        raiz = ttk.Frame(self.ventana, style="App.TFrame")
        raiz.pack(fill="both", expand=True)

        encabezado = ttk.Frame(raiz, style="App.TFrame")
        encabezado.pack(fill="x", padx=24, pady=(20, 10))

        ttk.Label(
            encabezado,
            text="Modelo de Transporte",
            style="Titulo.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            encabezado,
            text="Metodo de costo minimo para oferta y demanda balanceadas o no balanceadas.",
            style="Intro.TLabel"
        ).pack(anchor="w", pady=(4, 0))

        contenedor = ttk.Frame(raiz, style="App.TFrame")
        contenedor.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.canvas = tk.Canvas(
            contenedor,
            bg=self.colores["fondo"],
            highlightthickness=0,
            borderwidth=0
        )
        scroll_y = ttk.Scrollbar(contenedor, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll_y.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.contenido = ttk.Frame(self.canvas, style="Scroll.TFrame")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.contenido, anchor="nw")
        self.contenido.bind("<Configure>", self._actualizar_scroll)
        self.canvas.bind("<Configure>", self._ajustar_ancho)
        self.canvas.bind_all("<MouseWheel>", self._rueda_mouse)

        self.controles = self._crear_panel(self.contenido, "Configuracion general")
        self._crear_controles()

        self.formulario = self._crear_panel(self.contenido, "Datos de centros y distancias")

        self.resultados = self._crear_panel(self.contenido, "Resultados del metodo")
        self.resultados.columnconfigure(0, weight=1)
        self.resumen_var = tk.StringVar(value="Ingrese los datos y presione Resolver.")
        ttk.Label(self.resultados, textvariable=self.resumen_var, wraplength=980).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(2, 10)
        )

        self.tabla_asignaciones = self._crear_tabla(
            self.resultados,
            ("origen", "destino", "cantidad", "costo_unitario", "costo"),
            ("Origen", "Destino", "Cantidad", "Costo unit.", "Costo"),
            2,
            alto=7
        )

        self.matriz_panel = self._crear_panel(self.contenido, "Matriz de costos")
        self.tabla_costos = self._crear_tabla(self.matriz_panel, ("dato",), ("Datos",), 1, alto=7)

    def _crear_panel(self, padre, titulo):
        panel = ttk.Frame(padre, style="Panel.TFrame", padding=18)
        panel.pack(fill="x", padx=6, pady=10)
        panel.columnconfigure(0, weight=1)
        ttk.Label(panel, text=titulo, style="Subtitulo.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        return panel

    def _crear_controles(self):
        self.controles.columnconfigure(0, weight=1)
        self.controles.columnconfigure(4, weight=1)

        campos = ttk.Frame(self.controles, style="Panel.TFrame")
        campos.grid(row=1, column=0, sticky="ew")

        ttk.Label(campos, text="Empresa").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        self.empresa_var = tk.StringVar(value="Empresa demo")
        ttk.Entry(campos, textvariable=self.empresa_var, width=28).grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=4)

        ttk.Label(campos, text="Produccion").grid(row=0, column=1, sticky="w", padx=8, pady=4)
        self.num_produccion_var = tk.IntVar(value=3)
        ttk.Spinbox(campos, from_=1, to=10, textvariable=self.num_produccion_var, width=10).grid(row=1, column=1, sticky="w", padx=8, pady=4)

        ttk.Label(campos, text="Ventas").grid(row=0, column=2, sticky="w", padx=8, pady=4)
        self.num_venta_var = tk.IntVar(value=4)
        ttk.Spinbox(campos, from_=1, to=10, textvariable=self.num_venta_var, width=10).grid(row=1, column=2, sticky="w", padx=8, pady=4)

        ttk.Label(campos, text="Costo por km").grid(row=0, column=3, sticky="w", padx=8, pady=4)
        self.costo_km_var = tk.StringVar(value="1.25")
        ttk.Entry(campos, textvariable=self.costo_km_var, width=14).grid(row=1, column=3, sticky="w", padx=8, pady=4)
        campos.columnconfigure(0, weight=1)

        acciones = ttk.Frame(self.controles, style="Panel.TFrame")
        acciones.grid(row=2, column=0, sticky="ew", pady=(14, 0))

        ttk.Button(acciones, text="Crear tablas", style="Secondary.TButton", command=self.generar_formulario).pack(side="left", padx=(0, 8))
        ttk.Button(acciones, text="Resolver", command=self.resolver).pack(side="left", padx=8)
        ttk.Button(acciones, text="Graficar oferta", style="Secondary.TButton", command=self.graficar_oferta).pack(side="left", padx=8)
        ttk.Button(acciones, text="Graficar demanda", style="Secondary.TButton", command=self.graficar_demanda).pack(side="left", padx=8)

    def _crear_tabla(self, padre, columnas, encabezados, fila, alto=8):
        marco = ttk.Frame(padre, style="Panel.TFrame")
        marco.grid(row=fila, column=0, sticky="ew")
        marco.columnconfigure(0, weight=1)

        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=alto)
        for columna, encabezado in zip(columnas, encabezados):
            tabla.heading(columna, text=encabezado)
            tabla.column(columna, anchor="center", width=130, stretch=True)
        tabla.grid(row=0, column=0, sticky="ew")

        scroll_y = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x = ttk.Scrollbar(marco, orient="horizontal", command=tabla.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        tabla.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        return tabla

    def _actualizar_scroll(self, _evento=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _ajustar_ancho(self, evento):
        self.canvas.itemconfigure(self.canvas_window, width=evento.width)

    def _rueda_mouse(self, evento):
        self.canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")

    def generar_formulario(self):
        for widget in self.formulario.winfo_children():
            widget.destroy()

        ttk.Label(self.formulario, text="Datos de centros y distancias", style="Subtitulo.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 10)
        )

        n_prod = self.num_produccion_var.get()
        n_venta = self.num_venta_var.get()

        self.produccion_vars = [tk.StringVar(value=f"Planta {i + 1}") for i in range(n_prod)]
        self.venta_vars = [tk.StringVar(value=f"Venta {j + 1}") for j in range(n_venta)]
        self.oferta_vars = [tk.StringVar(value=str(valor)) for valor in self._valores_demo([120, 100, 80], n_prod)]
        self.demanda_vars = [tk.StringVar(value=str(valor)) for valor in self._valores_demo([70, 90, 80, 60], n_venta)]
        self.distancia_vars = [
            [tk.StringVar(value=str(self._distancia_demo(i, j))) for j in range(n_venta)]
            for i in range(n_prod)
        ]

        lienzo = tk.Canvas(self.formulario, bg=self.colores["panel"], highlightthickness=0, height=270)
        lienzo.grid(row=1, column=0, sticky="ew")
        scroll_x = ttk.Scrollbar(self.formulario, orient="horizontal", command=lienzo.xview)
        scroll_x.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        lienzo.configure(xscrollcommand=scroll_x.set)

        tabla = ttk.Frame(lienzo, style="Panel.TFrame")
        ventana_tabla = lienzo.create_window((0, 0), window=tabla, anchor="nw")
        tabla.bind("<Configure>", lambda _evento: lienzo.configure(scrollregion=lienzo.bbox("all")))
        lienzo.bind("<Configure>", lambda evento: lienzo.itemconfigure(ventana_tabla, height=evento.height))

        ttk.Label(tabla, text="Centro").grid(row=0, column=0, padx=5, pady=(2, 8), sticky="w")
        ttk.Label(tabla, text="Oferta").grid(row=0, column=1, padx=5, pady=(2, 8), sticky="w")

        for j in range(n_venta):
            ttk.Entry(tabla, textvariable=self.venta_vars[j], width=14).grid(row=0, column=j + 2, padx=5, pady=(2, 4))
            ttk.Label(tabla, text="Demanda").grid(row=1, column=j + 2, padx=5, pady=2)
            ttk.Entry(tabla, textvariable=self.demanda_vars[j], width=12).grid(row=2, column=j + 2, padx=5, pady=(0, 8))

        ttk.Label(tabla, text="Distancias km").grid(row=3, column=2, columnspan=max(1, n_venta), sticky="w", padx=5, pady=(8, 6))

        for i in range(n_prod):
            fila = i + 4
            ttk.Entry(tabla, textvariable=self.produccion_vars[i], width=14).grid(row=fila, column=0, padx=5, pady=4)
            ttk.Entry(tabla, textvariable=self.oferta_vars[i], width=12).grid(row=fila, column=1, padx=5, pady=4)

            for j in range(n_venta):
                ttk.Entry(tabla, textvariable=self.distancia_vars[i][j], width=12).grid(row=fila, column=j + 2, padx=5, pady=4)

        nota = (
            "Si oferta y demanda no coinciden, el sistema agrega automaticamente "
            "un centro ficticio con costo cero para balancear el modelo."
        )
        ttk.Label(self.formulario, text=nota, wraplength=980).grid(row=3, column=0, sticky="ew", pady=(12, 0))
        self.formulario.columnconfigure(0, weight=1)

    def _valores_demo(self, valores, cantidad):
        salida = []
        for i in range(cantidad):
            salida.append(valores[i] if i < len(valores) else 50)
        return salida

    def _distancia_demo(self, i, j):
        datos = [
            [12, 18, 25, 16],
            [20, 14, 10, 22],
            [15, 24, 17, 13],
        ]
        if i < len(datos) and j < len(datos[i]):
            return datos[i][j]
        return 10 + (i + 1) * 3 + (j + 1) * 2

    def _leer_problema(self):
        empresa = self.empresa_var.get().strip() or "Empresa sin nombre"
        producciones = [var.get().strip() or f"Planta {i + 1}" for i, var in enumerate(self.produccion_vars)]
        ventas = [var.get().strip() or f"Venta {j + 1}" for j, var in enumerate(self.venta_vars)]
        oferta = [
            convertir_numero(var.get(), f"oferta de {producciones[i]}", minimo=0)
            for i, var in enumerate(self.oferta_vars)
        ]
        demanda = [
            convertir_numero(var.get(), f"demanda de {ventas[j]}", minimo=0)
            for j, var in enumerate(self.demanda_vars)
        ]
        costo_km = convertir_numero(self.costo_km_var.get(), "costo por kilometro", minimo=0)
        distancias = []

        for i, fila in enumerate(self.distancia_vars):
            distancias.append([
                convertir_numero(valor.get(), f"distancia {producciones[i]} a {ventas[j]}", minimo=0)
                for j, valor in enumerate(fila)
            ])

        validar_matriz(distancias, oferta, demanda)

        return ProblemaTransporte(
            empresa=empresa,
            producciones=producciones,
            ventas=ventas,
            oferta=oferta,
            demanda=demanda,
            distancias=distancias,
            costo_km=costo_km
        )

    def resolver(self):
        try:
            problema = self._leer_problema()
            problema.estado_balance = validar_balance(problema.oferta, problema.demanda)
            problema = resolver_problema(problema)
        except ValueError as error:
            messagebox.showerror("Datos invalidos", str(error))
            return

        self.ultimo_problema = problema
        self._mostrar_resultados(problema)

    def _mostrar_resultados(self, problema):
        for tabla in (self.tabla_asignaciones, self.tabla_costos):
            for item in tabla.get_children():
                tabla.delete(item)

        for asignacion in problema.asignaciones:
            self.tabla_asignaciones.insert("", "end", values=(
                asignacion["origen"],
                asignacion["destino"],
                self._formato(asignacion["cantidad"]),
                self._moneda(asignacion["costo_unitario"]),
                self._moneda(asignacion["costo"])
            ))

        self._actualizar_tabla_costos(problema)

        resumen = (
            f"Empresa: {problema.empresa}  |  Estado inicial: {problema.estado_balance}  |  "
            f"Oferta total: {self._formato(sum(problema.oferta))}  |  "
            f"Demanda total: {self._formato(sum(problema.demanda))}  |  "
            f"Costo minimo: {self._moneda(problema.costo_total)}"
        )
        self.resumen_var.set(resumen)

    def _actualizar_tabla_costos(self, problema):
        ventas = problema.ventas_balanceadas or problema.ventas
        producciones = problema.producciones_balanceadas or problema.producciones
        costos = problema.costos_balanceados or problema.matriz_costos
        columnas = ["origen"] + [f"v{j}" for j in range(len(ventas))]
        self.tabla_costos.configure(columns=columnas)

        for columna in columnas:
            encabezado = "Origen" if columna == "origen" else ventas[int(columna[1:])]
            self.tabla_costos.heading(columna, text=encabezado)
            self.tabla_costos.column(columna, anchor="center", width=125, stretch=True)

        for i, fila in enumerate(costos):
            valores = [producciones[i]] + [self._moneda(valor) for valor in fila]
            self.tabla_costos.insert("", "end", values=valores)

    def graficar_oferta(self):
        try:
            problema = self._leer_problema()
            grafica_oferta(problema.producciones, problema.oferta)
        except ValueError as error:
            messagebox.showerror("Datos invalidos", str(error))

    def graficar_demanda(self):
        try:
            problema = self._leer_problema()
            grafica_demanda(problema.ventas, problema.demanda)
        except ValueError as error:
            messagebox.showerror("Datos invalidos", str(error))

    def _formato(self, valor):
        if float(valor).is_integer():
            return str(int(valor))
        return f"{valor:.2f}"

    def _moneda(self, valor):
        return f"${valor:,.2f}"


def iniciar_app():
    ventana = tk.Tk()
    AplicacionTransporte(ventana)
    ventana.mainloop()
