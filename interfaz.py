import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
from exportar import exportar_reporte_pdf
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

try:
    from graficas import grafica_asignaciones_bytes, grafica_asignaciones
    from modelos import ProblemaTransporte
    from transporte import resolver_problema
    from validaciones import convertir_numero, validar_balance, validar_matriz
except ImportError:
    def grafica_oferta(*a): pass
    def grafica_demanda(*a): pass
    def validar_balance(o, d): return "BALANCEADO" if sum(o) == sum(d) else "NO BALANCEADO"
    def validar_matriz(*a): pass
    def convertir_numero(v, *a, **kw):
        try: return float(v)
        except: raise ValueError(f"Valor invalido: '{v}'")
    class ProblemaTransporte:
        def __init__(self, **kw): self.__dict__.update(kw)
    def resolver_problema(p): return p


# ── Paleta ────────────────────────────────────────────────────
C = {
    "bg":       "#0B1628",
    "sidebar":  "#0C1A2E",
    "panel":    "#111F35",
    "panel2":   "#162540",
    "border":   "#1E3A5F",
    "blue":     "#3B82F6",
    "blue2":    "#1D4ED8",
    "teal":     "#14B8A6",
    "green":    "#22C55E",
    "amber":    "#F59E0B",
    "texto":    "#F1F5F9",
    "sub":      "#64748B",
    "kpi_bg":   "#162540",
    "res_bg":   "#0C1F14",
    "res_brd":  "#1a4a2a",
    "res_txt":  "#A7F3D0",
    "mat_hi":   "#1a3a6e",
    "mat_txt":  "#93C5FD",
}


class AplicacionTransporte(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Sistema de Transporte — Método de Costo Mínimo")
        self.geometry("1280x800")
        self.minsize(1000, 660)
        self.configure(fg_color=C["bg"])

        self.produccion_vars: list[ctk.StringVar] = []
        self.venta_vars:      list[ctk.StringVar] = []
        self.oferta_vars:     list[ctk.StringVar] = []
        self.demanda_vars:    list[ctk.StringVar] = []
        self.distancia_vars:  list[list[ctk.StringVar]] = []
        self.ultimo_problema  = None

        self._estilo_treeview()
        self._build()
        self.generar_formulario()

    # ── Treeview oscuro ──────────────────────────────────────
    def _estilo_treeview(self):
        s = ttk.Style()
        s.theme_use("clam")
        for name, bg, hbg in [
            ("Dark.Treeview",   C["panel"],  C["panel2"]),
            ("Green.Treeview",  C["res_bg"], "#0F2A1A"),
            ("Blue.Treeview",   C["mat_hi"], "#0e2a4d"),
        ]:
            s.configure(name,
                background=bg, fieldbackground=bg,
                foreground=C["texto"], rowheight=27,
                bordercolor=C["border"], font=("Segoe UI", 9))
            s.configure(f"{name}.Heading",
                background=hbg, foreground=C["sub"],
                bordercolor=C["border"], font=("Segoe UI", 9, "bold"))
            s.map(name, background=[("selected", C["teal"])],
                  foreground=[("selected", "#0B1628")])

    # ── Construcción principal ────────────────────────────────
    def _build(self):
        # ── Topbar ──
        top = ctk.CTkFrame(self, fg_color=C["sidebar"],
                            border_width=1, border_color=C["border"],
                            corner_radius=0)
        top.pack(fill="x", side="top")

        icon_lbl = ctk.CTkLabel(top, text="🚛",
                                 font=ctk.CTkFont("Segoe UI", 20),
                                 fg_color=C["blue"], width=44, height=44,
                                 corner_radius=10)
        icon_lbl.pack(side="left", padx=(14, 10), pady=10)

        ttl = ctk.CTkFrame(top, fg_color="transparent")
        ttl.pack(side="left")
        ctk.CTkLabel(ttl, text="Sistema de Transporte",
                     font=ctk.CTkFont("Segoe UI", 16, "bold"),
                     text_color=C["texto"]).pack(anchor="w")
        ctk.CTkLabel(ttl, text="Método de Costo Mínimo · Universidad de El Salvador · FMO",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=C["sub"]).pack(anchor="w")

        self.badge_var = ctk.StringVar(value="⬤  Listo")
        ctk.CTkLabel(top, textvariable=self.badge_var,
                     font=ctk.CTkFont("Segoe UI", 10, "bold"),
                     text_color=C["teal"],
                     fg_color=C["panel2"],
                     corner_radius=20,
                     padx=14, pady=4).pack(side="right", padx=16)

        # ── Cuerpo: sidebar + main ──
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)

        self._sidebar(body)
        self._main(body)

        # ── Status bar ──
        sb = ctk.CTkFrame(self, fg_color=C["sidebar"],
                           border_width=1, border_color=C["border"],
                           corner_radius=0, height=28)
        sb.pack(fill="x", side="bottom")
        sb.pack_propagate(False)
        self.status_var = ctk.StringVar(value="Ingrese los datos y presione  ▶ Resolver")
        ctk.CTkLabel(sb, textvariable=self.status_var,
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=C["sub"]).pack(side="left", padx=14)
        ctk.CTkLabel(sb, text="Universidad de El Salvador · FMO",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=C["sub"]).pack(side="right", padx=14)

    # ── Sidebar ───────────────────────────────────────────────
    def _sidebar(self, padre):
        sb = ctk.CTkFrame(padre, fg_color=C["sidebar"],
                           border_width=1, border_color=C["border"],
                           corner_radius=0, width=260)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        inner = ctk.CTkScrollableFrame(sb, fg_color="transparent",
                                        scrollbar_button_color=C["panel2"],
                                        scrollbar_button_hover_color=C["blue"])
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        def sec(texto):
            ctk.CTkLabel(inner, text=texto,
                         font=ctk.CTkFont("Segoe UI", 9, "bold"),
                         text_color=C["sub"]).pack(anchor="w", pady=(10, 3))

        def campo(label, var, ancho=220):
            f = ctk.CTkFrame(inner, fg_color=C["panel2"],
                              border_width=1, border_color=C["border"],
                              corner_radius=8)
            f.pack(fill="x", pady=3)
            ctk.CTkLabel(f, text=label,
                         font=ctk.CTkFont("Segoe UI", 9, "bold"),
                         text_color=C["sub"]).pack(anchor="w", padx=10, pady=(6, 1))
            ctk.CTkEntry(f, textvariable=var, width=ancho,
                          fg_color="transparent", border_width=0,
                          text_color=C["texto"],
                          font=ctk.CTkFont("Segoe UI", 11)).pack(padx=10, pady=(0, 6), fill="x")
            return f

        # Empresa
        sec("EMPRESA")
        self.empresa_var = ctk.StringVar(value="Distribuidora Nacional S.A.")
        campo("Nombre de empresa", self.empresa_var)

        # Configuración
        sec("CONFIGURACIÓN")
        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x", pady=3)
        grid.columnconfigure((0, 1), weight=1)

        self.num_produccion_var = ctk.IntVar(value=3)
        self.num_venta_var      = ctk.IntVar(value=4)
        self._spinbox(grid, "Producción", self.num_produccion_var, 0)
        self._spinbox(grid, "Ventas",     self.num_venta_var,      1)

        self.costo_km_var = ctk.StringVar(value="1.25")
        campo("Costo por km ($)", self.costo_km_var)

        # Botones
        sec("ACCIONES")
        self._btn(inner, "▶   Resolver",       self.resolver,          color=C["blue"],  hover=C["blue2"])
        self._btn(inner, "📋  Crear tablas",    self.generar_formulario, sec=True)
        self._btn(inner, "📊  Ver Grafico", self.graficar_asignaciones,    sec=True)
        self._btn(inner, "📈  Exportar PDF",self.exportar_pdf,   sec=True)

        # Estado
        sec("ESTADO DEL PROBLEMA")
        self._estado_frame = ctk.CTkFrame(inner, fg_color=C["panel2"],
                                           border_width=1, border_color=C["border"],
                                           corner_radius=8)
        self._estado_frame.pack(fill="x", pady=3)
        self.estado_tipo = ctk.StringVar(value="—")
        self.estado_info = ctk.StringVar(value="Sin datos aún")
        ctk.CTkLabel(self._estado_frame, text="Tipo de problema",
                     font=ctk.CTkFont("Segoe UI", 9, "bold"),
                     text_color=C["sub"]).pack(anchor="w", padx=10, pady=(7, 1))
        ctk.CTkLabel(self._estado_frame, textvariable=self.estado_tipo,
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=C["teal"]).pack(anchor="w", padx=10)
        ctk.CTkLabel(self._estado_frame, textvariable=self.estado_info,
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=C["sub"]).pack(anchor="w", padx=10, pady=(0, 7))

    def _btn(self, padre, texto, cmd, color=None, hover=None, sec=False):
        fc = C["panel2"] if sec else (color or C["blue"])
        hc = C["border"] if sec else (hover or C["blue2"])
        ctk.CTkButton(padre, text=texto, command=cmd,
                       fg_color=fc, hover_color=hc,
                       text_color=C["texto"],
                       font=ctk.CTkFont("Segoe UI", 11, "bold"),
                       corner_radius=8, height=34).pack(fill="x", pady=3)

    def _spinbox(self, padre, label, var, col):
        f = ctk.CTkFrame(padre, fg_color=C["panel2"],
                          border_width=1, border_color=C["border"],
                          corner_radius=8)
        f.grid(row=0, column=col, padx=3, sticky="ew")
        ctk.CTkLabel(f, text=label,
                     font=ctk.CTkFont("Segoe UI", 9, "bold"),
                     text_color=C["sub"]).pack(anchor="w", padx=8, pady=(6, 1))
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(padx=8, pady=(0, 6), anchor="w")
        val = ctk.CTkLabel(row, textvariable=var,
                            font=ctk.CTkFont("Segoe UI", 18, "bold"),
                            text_color=C["blue"], width=30)
        val.pack(side="left")
        btns = ctk.CTkFrame(row, fg_color="transparent")
        btns.pack(side="left", padx=4)
        ctk.CTkButton(btns, text="▲", width=22, height=16, corner_radius=4,
                       fg_color=C["border"], hover_color=C["blue"],
                       text_color=C["sub"], font=ctk.CTkFont("Segoe UI", 8),
                       command=lambda: var.set(min(var.get()+1, 10))).pack()
        ctk.CTkButton(btns, text="▼", width=22, height=16, corner_radius=4,
                       fg_color=C["border"], hover_color=C["blue"],
                       text_color=C["sub"], font=ctk.CTkFont("Segoe UI", 8),
                       command=lambda: var.set(max(var.get()-1, 1))).pack(pady=(1, 0))

    # ── Main area ─────────────────────────────────────────────
    def _main(self, padre):
        self.main_scroll = ctk.CTkScrollableFrame(padre, fg_color=C["bg"],
                                                   scrollbar_button_color=C["panel2"],
                                                   scrollbar_button_hover_color=C["blue"])
        self.main_scroll.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Placeholder formulario
        self._form_card = self._card(self.main_scroll, "📦  Datos de centros y distancias", C["blue2"])

        # KPIs + resultados
        res = self._card(self.main_scroll, "✅  Resultados del método", "#0D3D36")

        # KPI row
        kpi_row = ctk.CTkFrame(res, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 10))
        kpi_row.columnconfigure((0,1,2), weight=1)

        self.kpi_costo = self._kpi(kpi_row, "Costo mínimo", "—", C["green"], 0)
        self.kpi_oferta= self._kpi(kpi_row, "Oferta total", "—", C["blue"],  1)
        self.kpi_deman = self._kpi(kpi_row, "Demanda total","—", C["teal"],  2)
        

        # Tabla asignaciones
        ctk.CTkLabel(res, text="Detalle de asignaciones",
                     font=ctk.CTkFont("Segoe UI", 11, "bold"),
                     text_color=C["texto"]).pack(anchor="w", pady=(0, 4))
        
        self.asignaciones_frame = ctk.CTkFrame(
            res,
            fg_color="transparent"
        )

        self.asignaciones_frame.pack(fill="x", pady=(5,10))

        # Interpretación
        ctk.CTkLabel(res, text="Interpretación",
                     font=ctk.CTkFont("Segoe UI", 11, "bold"),
                     text_color=C["texto"]).pack(anchor="w", pady=(10, 4))
        self.interpbox = ctk.CTkTextbox(res, height=120, wrap="word",
                                         fg_color=C["res_bg"],
                                         border_color=C["res_brd"],
                                         border_width=1,
                                         text_color=C["res_txt"],
                                         font=ctk.CTkFont("Segoe UI", 10))
        self.interpbox.pack(fill="x")
        self.interpbox.insert("1.0", "Aquí aparecerá la interpretación detallada de la solución.")
        self.interpbox.configure(state="disabled")

        # Matriz
        mat = self._card(self.main_scroll, "📋  Matriz de costos", "#2D1F5A")
        self.tabla_costos = self._treeview(mat, ("dato",), ("Datos",), alto=5)

    def _card(self, padre, titulo, hdr_color=None):
        outer = ctk.CTkFrame(padre, fg_color=C["panel"],
                              border_width=1, border_color=C["border"],
                              corner_radius=12)
        outer.pack(fill="x", pady=6)

        hdr = ctk.CTkFrame(outer,
                            fg_color=hdr_color or C["panel2"],
                            corner_radius=0, height=38)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=titulo,
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=C["texto"]).pack(side="left", padx=14)

        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=12)
        return inner

    def _kpi(self, padre, label, valor, color, col):
            f = ctk.CTkFrame(
                padre,
                fg_color=C["kpi_bg"],
                border_width=1,
                border_color=C["border"],
                corner_radius=12
            )
            f.grid(row=0, column=col, padx=6, sticky="nsew", ipady=8)

            ctk.CTkLabel(
                f,
                text=label,
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                text_color=C["sub"]
            ).pack(anchor="w", padx=14, pady=(10, 4))

            var = ctk.StringVar(value=valor)

            ctk.CTkLabel(
                f,
                textvariable=var,
                font=ctk.CTkFont("Segoe UI", 30, "bold"),
                text_color=color
            ).pack(anchor="w", padx=14, pady=(0, 10))

            return var

    def _treeview(self, padre, cols, hdrs, alto=6, style="Dark.Treeview"):
        wrap = ctk.CTkFrame(padre, fg_color="transparent")
        wrap.pack(fill="x", pady=(0, 4))
        wrap.columnconfigure(0, weight=1)
        tv = ttk.Treeview(wrap, columns=cols, show="headings",
                           height=alto, style=style)
        for c, h in zip(cols, hdrs):
            tv.heading(c, text=h)
            tv.column(c, anchor="center", width=140, stretch=True)
        tv.grid(row=0, column=0, sticky="ew")
        sy = ttk.Scrollbar(wrap, orient="vertical",   command=tv.yview)
        sx = ttk.Scrollbar(wrap, orient="horizontal", command=tv.xview)
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        tv.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        return tv

    # ── Formulario dinámico ───────────────────────────────────
    def generar_formulario(self):
        for w in self._form_card.winfo_children():
            w.destroy()

        n_prod  = self.num_produccion_var.get()
        n_venta = self.num_venta_var.get()

        self.produccion_vars = [ctk.StringVar(value=f"Planta {i+1}") for i in range(n_prod)]
        self.venta_vars      = [ctk.StringVar(value=f"Venta {j+1}")  for j in range(n_venta)]
        self.oferta_vars     = [ctk.StringVar(value=str(v)) for v in self._demo_oferta(n_prod)]
        self.demanda_vars    = [ctk.StringVar(value=str(v)) for v in self._demo_demanda(n_venta)]
        self.distancia_vars  = [
            [ctk.StringVar(value=str(self._dist_demo(i,j))) for j in range(n_venta)]
            for i in range(n_prod)
        ]

        info = ctk.CTkLabel(self._form_card,
                             text=f"  {n_prod} orígenes  ·  {n_venta} destinos",
                             font=ctk.CTkFont("Segoe UI", 10),
                             text_color=C["sub"])
        info.pack(anchor="e", pady=(0, 6))

        # Canvas scroll horizontal
        canvas = tk.Canvas(self._form_card, bg=C["panel"],
                            highlightthickness=0)
        canvas.pack(fill="x")
        sx = ctk.CTkScrollbar(self._form_card, orientation="horizontal",
                               command=canvas.xview)
        sx.pack(fill="x")
        canvas.configure(xscrollcommand=sx.set)

        tabla = ctk.CTkFrame(canvas, fg_color=C["panel"])
        win   = canvas.create_window((0, 0), window=tabla, anchor="nw")

        def ajustar_canvas(_=None):
            canvas.update_idletasks()
            bbox = canvas.bbox("all")
            if bbox:
                canvas.configure(scrollregion=bbox, height=bbox[3] - bbox[1])

        tabla.bind("<Configure>", ajustar_canvas)

        EW = dict(padx=4, pady=3)

        def hdr_lbl(padre, texto, r, c, cs=1):
            ctk.CTkLabel(padre, text=texto,
                         font=ctk.CTkFont("Segoe UI", 9, "bold"),
                         fg_color=C["panel2"],
                         corner_radius=4,
                         text_color=C["sub"],
                         padx=6, pady=3).grid(row=r, column=c, columnspan=cs, **EW)

        def entrada(padre, var, r, c, color_borde=None, ancho=100, estado="normal"):
                    ctk.CTkEntry(
                            padre,
                            textvariable=var,
                            width=ancho,
                            fg_color=C["panel2"],
                            border_color=color_borde or C["border"],
                            text_color=C["texto"],
                            font=ctk.CTkFont("Segoe UI", 10),
                            state=estado
                    ).grid(row=r, column=c, **EW)

        hdr_lbl(tabla, "Centro / Oferta", 0, 0, 2)
        for j in range(n_venta):
            entrada(tabla, self.venta_vars[j], 0, j+2, C["blue"], 110, "readonly")
            hdr_lbl(tabla, "Demanda", 1, j+2)
            entrada(tabla, self.demanda_vars[j], 2, j+2, C["teal"])

        ctk.CTkLabel(tabla, text="── Distancias (km) ──",
                     font=ctk.CTkFont("Segoe UI", 9),
                     text_color=C["blue"],
                     fg_color="transparent").grid(
            row=3, column=2, columnspan=max(1,n_venta), sticky="w", **EW)

        for i in range(n_prod):
            fila = i + 4
            entrada(tabla, self.produccion_vars[i], fila, 0, C["blue"], 110, "readonly")
            entrada(tabla, self.oferta_vars[i],     fila, 1, C["teal"])
            for j in range(n_venta):
                entrada(tabla, self.distancia_vars[i][j], fila, j+2)

        ctk.CTkLabel(self._form_card,
                     text="ℹ  Si oferta ≠ demanda, el sistema agrega un nodo ficticio con costo $0.00 "
                           "para balancear automáticamente el modelo.",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color=C["sub"],
                     wraplength=900).pack(anchor="w", pady=(8, 0))

    # ── Lógica ────────────────────────────────────────────────
    def _leer(self):
        empresa      = self.empresa_var.get().strip() or "Empresa sin nombre"
        producciones = [v.get().strip() or f"Planta {i+1}" for i,v in enumerate(self.produccion_vars)]
        ventas       = [v.get().strip() or f"Venta {j+1}"  for j,v in enumerate(self.venta_vars)]
        oferta       = [convertir_numero(v.get(), f"oferta de {producciones[i]}", minimo=0)
                        for i,v in enumerate(self.oferta_vars)]
        demanda      = [convertir_numero(v.get(), f"demanda de {ventas[j]}", minimo=0)
                        for j,v in enumerate(self.demanda_vars)]
        costo_km     = convertir_numero(self.costo_km_var.get(), "costo por km", minimo=0)
        distancias   = [
            [convertir_numero(self.distancia_vars[i][j].get(),
                              f"dist {producciones[i]}→{ventas[j]}", minimo=0)
             for j in range(len(ventas))]
            for i in range(len(producciones))
        ]
        validar_matriz(distancias, oferta, demanda)
        return ProblemaTransporte(empresa=empresa, producciones=producciones,
                                   ventas=ventas, oferta=oferta, demanda=demanda,
                                   distancias=distancias, costo_km=costo_km)

    def resolver(self):
        try:
            p = self._leer()
            p.estado_balance = validar_balance(p.oferta, p.demanda)
            p = resolver_problema(p)
        except ValueError as e:
            messagebox.showerror("Datos inválidos", str(e))
            return
        self.ultimo_problema = p
        self._mostrar(p)

    def _mostrar(self, p):

        # Limpiar matriz de costos
        for item in self.tabla_costos.get_children():
            self.tabla_costos.delete(item)

        # Limpiar tarjetas anteriores
        for w in self.asignaciones_frame.winfo_children():
            w.destroy()

        self.asignaciones_frame.grid_columnconfigure(0, weight=1)
        self.asignaciones_frame.grid_columnconfigure(1, weight=1)

        # Crear tarjetas nuevas
        for i, a in enumerate(p.asignaciones):

            origen = a["origen"]
            destino = a["destino"]

            es_ficticio = (
                "ficticia" in origen.lower() or
                "ficticia" in destino.lower()
            )

            color_borde = C["amber"] if es_ficticio else C["blue"]

            card = ctk.CTkFrame(
                self.asignaciones_frame,
                fg_color=C["panel2"],
                border_width=1,
                border_color=color_borde,
                corner_radius=12
            )

            fila = i // 2
            columna = i % 2

            card.grid(
                row=fila,
                column=columna,
                padx=8,
                pady=8,
                sticky="nsew"
            )

            ctk.CTkLabel(
                card,
                text=f"🚚 {origen} ➜ {destino}",
                font=ctk.CTkFont("Segoe UI", 14, "bold"),
                text_color=C["texto"]
            ).pack(anchor="w", padx=15, pady=(12, 4))

            ctk.CTkLabel(
                card,
                text=f"📦 Cantidad transportada: {self._fmt(a['cantidad'])} unidades",
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=C["texto"]
            ).pack(anchor="w", padx=15)

            ctk.CTkLabel(
                card,
                text=f"💲 Costo unitario: {self._mon(a['costo_unitario'])}",
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=C["texto"]
            ).pack(anchor="w", padx=15)

            ctk.CTkLabel(
                card,
                text=f"💰 Costo total: {self._mon(a['costo'])}",
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                text_color=C["green"]
            ).pack(anchor="w", padx=15, pady=(0, 12))

            self._actualizar_matriz(p)

        # KPIs
        self.kpi_costo.set(self._mon(p.costo_total))
        self.kpi_oferta.set(self._fmt(sum(p.oferta)))
        self.kpi_deman.set(self._fmt(sum(p.demanda)))

        # Estado sidebar
        bal = p.estado_balance
        self.estado_tipo.set(f"✓ {bal}" if bal == "BALANCEADO" else f"⚠ {bal}")
        self.estado_info.set(
            f"Oferta = Demanda = {self._fmt(sum(p.oferta))} u"
            if bal == "BALANCEADO"
            else f"Oferta: {self._fmt(sum(p.oferta))} u  |  Demanda: {self._fmt(sum(p.demanda))} u"
        )

        # Status bar
        self.status_var.set(
            f"  {p.empresa}  ·  {bal}  ·  Costo mínimo: {self._mon(p.costo_total)}"
        )
        self.badge_var.set("⬤  Resuelto")

        # Interpretación
        lineas = [
            f"El costo mínimo de transporte para {p.empresa} es {self._mon(p.costo_total)}.\n",
            "Distribución recomendada:"
        ]
        for a in p.asignaciones:
            o, d = a["origen"], a["destino"]
            if "ficticia" in o.lower() or "ficticia" in d.lower():
                lineas.append(f"  • {o} → {d}: {self._fmt(a['cantidad'])} u  (nodo ficticio — solo balancea)")
            else:
                lineas.append(f"  • {o} → {d}: {self._fmt(a['cantidad'])} u  |  "
                               f"Costo unit. {self._mon(a['costo_unitario'])}  |  "
                               f"Total {self._mon(a['costo'])}")
        if bal != "BALANCEADO":
            lineas.append("\n⚠  Se agregó un nodo ficticio con costo $0.00 para balancear el modelo.")

        self.interpbox.configure(state="normal")
        self.interpbox.delete("1.0", "end")
        self.interpbox.insert("1.0", "\n".join(lineas))
        self.interpbox.configure(state="disabled")

    def _actualizar_matriz(self, p):
        ventas  = getattr(p, "ventas_balanceadas",       None) or p.ventas
        prods   = getattr(p, "producciones_balanceadas", None) or p.producciones
        costos  = getattr(p, "costos_balanceados",       None) or p.matriz_costos
        cols    = ["origen"] + [f"v{j}" for j in range(len(ventas))]
        self.tabla_costos.configure(columns=cols)
        for col in cols:
            hdr = "Origen" if col == "origen" else ventas[int(col[1:])]
            self.tabla_costos.heading(col, text=hdr)
            self.tabla_costos.column(col, anchor="center", width=125, stretch=True)
        for i, fila in enumerate(costos):
            vals = [prods[i]] + [self._mon(v) for v in fila]
            self.tabla_costos.insert("", "end", values=vals)

    def graficar_oferta(self):
        try: grafica_oferta(self._leer().producciones, self._leer().oferta)
        except ValueError as e: messagebox.showerror("Datos inválidos", str(e))

    def graficar_demanda(self):
        try: grafica_demanda(self._leer().ventas, self._leer().demanda)
        except ValueError as e: messagebox.showerror("Datos inválidos", str(e))

    # ── Demos ─────────────────────────────────────────────────
    def _demo_oferta(self, n):
        b = [120,100,80]; return [b[i] if i < len(b) else 50 for i in range(n)]

    def _demo_demanda(self, n):
        b = [70,90,80,60]; return [b[j] if j < len(b) else 50 for j in range(n)]

    def _dist_demo(self, i, j):
        d = [[12,18,25,16],[20,14,10,22],[15,24,17,13]]
        return d[i][j] if i < len(d) and j < len(d[i]) else 10+(i+1)*3+(j+1)*2

    # ── Formato ───────────────────────────────────────────────
    def _fmt(self, v): return str(int(v)) if float(v).is_integer() else f"{v:.2f}"
    def _mon(self, v): return f"${v:,.2f}"

    def exportar_pdf(self):
   
        if self.ultimo_problema is None:
            messagebox.showwarning(
                "Sin resultados",
                "Primero debes resolver el problema antes de exportar el PDF."
            )
            return
    
        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Archivo PDF", "*.pdf")],
            initialfile=f"reporte_{self.ultimo_problema.empresa.replace(' ', '_')}.pdf",
            title="Guardar reporte PDF"
        )
    
        if not ruta:
            return  # El usuario canceló el diálogo
    
        try:
            self.badge_var.set("⬤  Exportando...")
            self.status_var.set("  Generando PDF...")
            self.update_idletasks()  # Refresca la UI antes de generar
    
            ruta_generada = exportar_reporte_pdf(self.ultimo_problema, ruta)
    
            self.badge_var.set("⬤  Resuelto")
            self.status_var.set(f"  PDF exportado correctamente: {ruta_generada}")
            messagebox.showinfo("PDF generado", f"Reporte guardado en:\n{ruta_generada}")
    
        except Exception as e:
            self.badge_var.set("⬤  Error")
            messagebox.showerror("Error al exportar", f"No se pudo generar el PDF:\n{str(e)}")


    def graficar_asignaciones(self):
        if self.ultimo_problema is None:
            messagebox.showwarning(
                "Sin resultados",
                "Primero resolvé el problema para poder graficar."
            )
            return
        from graficas import grafica_asignaciones
        grafica_asignaciones(self.ultimo_problema)

def iniciar_app():
    app = AplicacionTransporte()
    app.mainloop()

