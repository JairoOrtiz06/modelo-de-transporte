from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os
from graficas import grafica_asignaciones_bytes
from reportlab.platypus import Image as RLImage


# ── Paleta de colores (igual a la UI) ────────────────────────────────────────
AZUL        = colors.HexColor("#3B82F6")
AZUL_OSC    = colors.HexColor("#1D4ED8")
TEAL        = colors.HexColor("#14B8A6")
VERDE       = colors.HexColor("#22C55E")
AMBAR       = colors.HexColor("#F59E0B")
FONDO_OSC   = colors.HexColor("#0B1628")
PANEL       = colors.HexColor("#111F35")
PANEL2      = colors.HexColor("#162540")
BORDE       = colors.HexColor("#1E3A5F")
TEXTO       = colors.HexColor("#F1F5F9")
SUBTEXTO    = colors.HexColor("#64748B")
RES_BG      = colors.HexColor("#0C1F14")
RES_TXT     = colors.HexColor("#A7F3D0")
BLANCO      = colors.white
GRIS_CLARO  = colors.HexColor("#CBD5E1")


# ── Estilos tipográficos ──────────────────────────────────────────────────────
def _estilos():
    base = getSampleStyleSheet()

    estilos = {
        "titulo_portada": ParagraphStyle(
            "titulo_portada",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=BLANCO,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "subtitulo_portada": ParagraphStyle(
            "subtitulo_portada",
            fontName="Helvetica",
            fontSize=11,
            textColor=GRIS_CLARO,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "empresa": ParagraphStyle(
            "empresa",
            fontName="Helvetica-Bold",
            fontSize=15,
            textColor=TEAL,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "seccion": ParagraphStyle(
            "seccion",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=AZUL,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "normal": ParagraphStyle(
            "normal",
            fontName="Helvetica",
            fontSize=10,
            textColor=PANEL,
            spaceAfter=4,
        ),
        "normal_blanco": ParagraphStyle(
            "normal_blanco",
            fontName="Helvetica",
            fontSize=10,
            textColor=BLANCO,
            spaceAfter=4,
        ),
        "mono": ParagraphStyle(
            "mono",
            fontName="Courier",
            fontSize=9,
            textColor=PANEL,
            spaceAfter=3,
        ),
        "kpi_valor": ParagraphStyle(
            "kpi_valor",
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=VERDE,
            alignment=TA_CENTER,
        ),
        "kpi_label": ParagraphStyle(
            "kpi_label",
            fontName="Helvetica",
            fontSize=9,
            textColor=SUBTEXTO,
            alignment=TA_CENTER,
        ),
        "advertencia": ParagraphStyle(
            "advertencia",
            fontName="Helvetica-Oblique",
            fontSize=9,
            textColor=AMBAR,
            spaceAfter=4,
        ),
        "pie": ParagraphStyle(
            "pie",
            fontName="Helvetica",
            fontSize=8,
            textColor=SUBTEXTO,
            alignment=TA_CENTER,
        ),
        "bold": ParagraphStyle(
            "bold",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=PANEL,
            spaceAfter=3,
        ),
    }
    return estilos


# ── Utilidades de formato ─────────────────────────────────────────────────────
def _mon(v):
    return f"${float(v):,.2f}"

def _fmt(v):
    f = float(v)
    return str(int(f)) if f.is_integer() else f"{f:.2f}"

def _fecha():
    return datetime.now().strftime("%d/%m/%Y  %H:%M:%S")


# ── Header / Footer decorativo ────────────────────────────────────────────────
def _header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter

    # Header — banda azul oscura
    canvas.setFillColor(AZUL_OSC)
    canvas.rect(0, h - 36, w, 36, fill=True, stroke=False)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(BLANCO)
    canvas.drawString(18, h - 22, "Sistema de Transporte -- Metodo de Costo Minimo")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS_CLARO)
    canvas.drawRightString(w - 18, h - 22, f"Generado: {_fecha()}")

    # Footer
    canvas.setFillColor(PANEL2)
    canvas.rect(0, 0, w, 26, fill=True, stroke=False)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SUBTEXTO)
    canvas.drawString(18, 8, "Universidad de El Salvador · FMO")
    canvas.drawCentredString(w / 2, 8, "Optimización de Transporte")
    canvas.drawRightString(w - 18, 8, f"Página {doc.page}")

    canvas.restoreState()


# ── Sección de KPIs ───────────────────────────────────────────────────────────
def _tabla_kpis(p, E):
    total_oferta  = sum(p.oferta)
    total_demanda = sum(p.demanda)

    def _kpi_style(color_val):
        return ParagraphStyle(
            "kv", fontName="Helvetica-Bold", fontSize=16,
            textColor=color_val, alignment=TA_CENTER
        )

    # Fila 1: etiquetas
    fila_labels = [
        Paragraph("COSTO MINIMO TOTAL", E["kpi_label"]),
        Paragraph("OFERTA TOTAL",        E["kpi_label"]),
        Paragraph("DEMANDA TOTAL",       E["kpi_label"]),
    ]
    # Fila 2: valores
    fila_valores = [
        Paragraph(_mon(p.costo_total),          _kpi_style(VERDE)),
        Paragraph(f"{_fmt(total_oferta)} u",    _kpi_style(AZUL)),
        Paragraph(f"{_fmt(total_demanda)} u",   _kpi_style(TEAL)),
    ]

    data = [fila_labels, fila_valores]
    t = Table(data, colWidths=[180, 180, 180], rowHeights=[20, 36])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), PANEL2),
        ("BOX",           (0, 0), (0, -1),  1, VERDE),
        ("BOX",           (1, 0), (1, -1),  1, AZUL),
        ("BOX",           (2, 0), (2, -1),  1, TEAL),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


# ── Tabla de asignaciones ─────────────────────────────────────────────────────
def _tabla_asignaciones(p, E):
    encabezados = ["Origen", "Destino", "Cantidad (u)", "Costo Unit.", "Costo Total"]
    filas = [encabezados]

    for a in p.asignaciones:
        filas.append([
            a["origen"],
            a["destino"],
            _fmt(a["cantidad"]),
            _mon(a["costo_unitario"]),
            _mon(a["costo"]),
        ])

    col_w = [115, 115, 90, 90, 90]
    t = Table(filas, colWidths=col_w, repeatRows=1)

    estilo = [
        # Encabezado
        ("BACKGROUND",   (0, 0), (-1, 0),  AZUL_OSC),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  9),
        ("ALIGN",        (0, 0), (-1, 0),  "CENTER"),
        ("BOTTOMPADDING",(0, 0), (-1, 0),  8),
        ("TOPPADDING",   (0, 0), (-1, 0),  8),
        # Filas de datos
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ALIGN",        (2, 1), (-1, -1), "CENTER"),
        ("ALIGN",        (0, 1), (1, -1),  "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, colors.HexColor("#EFF6FF")]),
        ("GRID",         (0, 0), (-1, -1), 0.4, BORDE),
        ("BOTTOMPADDING",(0, 1), (-1, -1), 6),
        ("TOPPADDING",   (0, 1), (-1, -1), 6),
        # Columna costo total en verde
        ("TEXTCOLOR",    (4, 1), (4, -1),  colors.HexColor("#166534")),
        ("FONTNAME",     (4, 1), (4, -1),  "Helvetica-Bold"),
    ]

    # Filas ficticias en ámbar
    for idx, a in enumerate(p.asignaciones, start=1):
        if "ficticia" in a["origen"].lower() or "ficticia" in a["destino"].lower():
            estilo.append(("BACKGROUND", (0, idx), (-1, idx), colors.HexColor("#FFFBEB")))
            estilo.append(("TEXTCOLOR",  (0, idx), (-1, idx), colors.HexColor("#92400E")))

    t.setStyle(TableStyle(estilo))
    return t


# ── Matriz de costos ──────────────────────────────────────────────────────────
def _tabla_matriz(p, E):
    ventas = getattr(p, "ventas_balanceadas", None) or p.ventas
    prods  = getattr(p, "producciones_balanceadas", None) or p.producciones
    costos = getattr(p, "costos_balanceados", None) or p.matriz_costos

    encabezado = ["Origen \\ Destino"] + list(ventas)
    filas = [encabezado]
    for i, fila in enumerate(costos):
        filas.append([prods[i]] + [_mon(v) for v in fila])

    n_cols = len(encabezado)
    ancho_col = min(90, (540 - 120) / max(n_cols - 1, 1))
    col_w = [130] + [ancho_col] * (n_cols - 1)

    t = Table(filas, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  PANEL),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  GRIS_CLARO),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0),  9),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("BACKGROUND",   (0, 1), (0, -1),  PANEL2),
        ("TEXTCOLOR",    (0, 1), (0, -1),  colors.HexColor("#93C5FD")),
        ("FONTNAME",     (0, 1), (0, -1),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ROWBACKGROUNDS", (1, 1), (-1, -1), [BLANCO, colors.HexColor("#F0F9FF")]),
        ("GRID",         (0, 0), (-1, -1), 0.4, BORDE),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
    ]))
    return t


# ── Bloque de interpretación ──────────────────────────────────────────────────
def _parrafos_interpretacion(p, E):
    elementos = []
    bal = getattr(p, "estado_balance", "BALANCEADO")

    elementos.append(Paragraph(
        f"El costo minimo de transporte para <b>{p.empresa}</b> "
        f"aplicando el Metodo de Costo Minimo es de <b>{_mon(p.costo_total)}</b>.",
        E["normal"]
    ))
    elementos.append(Spacer(1, 6))
    elementos.append(Paragraph("Distribucion recomendada:", E["bold"]))

    for a in p.asignaciones:
        o, d = a["origen"], a["destino"]
        es_fic = "ficticia" in o.lower() or "ficticia" in d.lower()
        if es_fic:
            txt = (f"<font color='#B45309'>&#9888;  {o} &#8594; {d}: "
                   f"{_fmt(a['cantidad'])} u  (nodo ficticio — solo balancea el modelo)</font>")
        else:
            txt = (f"&#8226;  <b>{o}</b> &#8594; <b>{d}</b>: "
                   f"{_fmt(a['cantidad'])} u  |  "
                   f"Costo unit. {_mon(a['costo_unitario'])}  |  "
                   f"Subtotal {_mon(a['costo'])}")
        elementos.append(Paragraph(txt, E["normal"]))

    if bal != "BALANCEADO":
        elementos.append(Spacer(1, 6))
        elementos.append(Paragraph(
            "&#9888;  El problema NO estaba balanceado. "
            "Se agrego un nodo ficticio con costo $0.00 para equilibrar oferta y demanda.",
            E["advertencia"]
        ))
    return elementos


# ── Función pública principal ─────────────────────────────────────────────────
def exportar_reporte_pdf(problema, ruta_salida: str = None) -> str:
    """
    Genera un reporte PDF completo del problema de transporte resuelto.

    Parámetros
    ----------
    problema     : ProblemaTransporte resuelto (con .asignaciones, .costo_total, etc.)
    ruta_salida  : Ruta del archivo PDF de salida. Si es None, se genera automáticamente.

    Retorna
    -------
    str : Ruta absoluta del PDF generado.
    """
    if ruta_salida is None:
        nombre_empresa = getattr(problema, "empresa", "reporte").replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_salida = f"reporte_{nombre_empresa}_{timestamp}.pdf"

    E = _estilos()
    bal = getattr(problema, "estado_balance", "BALANCEADO")
    es_balanceado = bal == "BALANCEADO"

    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.6 * inch,
        title=f"Reporte de Transporte — {getattr(problema, 'empresa', '')}",
        author="Sistema de Transporte — UES FMO",
        subject="Método de Costo Mínimo",
    )

    story = []

    # ── PORTADA ──────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))

    # Banner de portada
    banner_data = [[
        Paragraph("REPORTE DE TRANSPORTE", E["titulo_portada"]),
    ], [
        Paragraph("Metodo de Costo Minimo", E["subtitulo_portada"]),
    ], [
        Paragraph("Universidad de El Salvador  ·  FMO", E["subtitulo_portada"]),
    ], [
        Paragraph(getattr(problema, "empresa", ""), E["empresa"]),
    ]]
    banner = Table(banner_data, colWidths=[540])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), FONDO_OSC),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(banner)
    story.append(Spacer(1, 16))

    # Metadatos de portada
    meta = [
        ["Fecha de generacion:", _fecha()],
        ["Estado del problema:", f"{'BALANCEADO' if es_balanceado else 'NO BALANCEADO'}"],
        ["Origenes (produccion):", str(len(problema.producciones))],
        ["Destinos (ventas):",     str(len(problema.ventas))],
        ["Costo por km:",          _mon(getattr(problema, "costo_km", 0))],
    ]
    t_meta = Table(meta, colWidths=[200, 340])
    t_meta.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",  (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",  (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), SUBTEXTO),
        ("TEXTCOLOR", (1, 0), (1, -1), PANEL),
        ("BACKGROUND",(1, 1), (1, 1),
            colors.HexColor("#DCFCE7") if es_balanceado else colors.HexColor("#FEF3C7")),
        ("FONTNAME",  (1, 1), (1, 1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 1), (1, 1),
            colors.HexColor("#166534") if es_balanceado else colors.HexColor("#92400E")),
        ("GRID",      (0, 0), (-1, -1), 0.3, colors.HexColor("#E2E8F0")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
            [BLANCO, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDE))

    # ── SECCIÓN 1: KPIs ───────────────────────────────────────────────────────
    story.append(Paragraph("1.  Resumen Ejecutivo", E["seccion"]))
    story.append(_tabla_kpis(problema, E))
    story.append(Spacer(1, 14))

    # ── SECCIÓN 2: Asignaciones ───────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDE))
    story.append(Paragraph("2.  Detalle de Asignaciones", E["seccion"]))
    story.append(Paragraph(
        "La siguiente tabla muestra la distribucion optima calculada por el Metodo de Costo Minimo.",
        E["normal"]
    ))
    story.append(Spacer(1, 6))
    story.append(_tabla_asignaciones(problema, E))

    if any(
        "ficticia" in a["origen"].lower() or "ficticia" in a["destino"].lower()
        for a in problema.asignaciones
    ):
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            "Las filas resaltadas corresponden a nodos ficticios agregados para balancear "
            "el modelo. Su costo real es $0.00.",
            E["advertencia"]
        ))

    # ── SECCIÓN 3: Matriz de costos ───────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDE))
    story.append(Paragraph("3.  Matriz de Costos", E["seccion"]))
    story.append(Paragraph(
        "Costo total por ruta = distancia (km) * costo por km * cantidad transportada.",
        E["normal"]
    ))
    story.append(Spacer(1, 6))
    story.append(_tabla_matriz(problema, E))

    # ── SECCIÓN 4: Oferta y Demanda ───────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDE))
    story.append(Paragraph("4.  Centros de Produccion y Ventas", E["seccion"]))

    # Tabla oferta
    story.append(Paragraph("Centros de Produccion (Oferta)", E["bold"]))
    oferta_data = [["Centro", "Oferta (u)"]]
    for nombre, val in zip(problema.producciones, problema.oferta):
        oferta_data.append([nombre, _fmt(val)])
    t_of = Table(oferta_data, colWidths=[280, 180])
    t_of.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  AZUL_OSC),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ALIGN",        (1, 0), (1, -1),  "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, colors.HexColor("#EFF6FF")]),
        ("GRID",         (0, 0), (-1, -1), 0.4, BORDE),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(t_of)
    story.append(Spacer(1, 10))

    # Tabla demanda
    story.append(Paragraph("Centros de Venta (Demanda)", E["bold"]))
    demanda_data = [["Centro", "Demanda (u)"]]
    for nombre, val in zip(problema.ventas, problema.demanda):
        demanda_data.append([nombre, _fmt(val)])
    t_dem = Table(demanda_data, colWidths=[280, 180])
    t_dem.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  colors.HexColor("#0F766E")),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  BLANCO),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 9),
        ("ALIGN",        (1, 0), (1, -1),  "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, colors.HexColor("#F0FDFA")]),
        ("GRID",         (0, 0), (-1, -1), 0.4, BORDE),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(t_dem)

    # ── SECCIÓN 5: Gráfica de asignaciones ───────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDE))
    story.append(Paragraph("5.  Grafica de Distribucion", E["seccion"]))
    story.append(Paragraph(
        "Visualizacion de las unidades asignadas por origen hacia cada centro de venta.",
        E["normal"]
    ))
    story.append(Spacer(1, 8))

    buf_grafica = grafica_asignaciones_bytes(problema)
    if buf_grafica:
        img = RLImage(buf_grafica, width=500, height=280)
        story.append(img)
    else:
        story.append(Paragraph("No hay asignaciones reales para graficar.", E["normal"]))

    # ── SECCIÓN 5: Interpretación ─────────────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDE))
    story.append(Paragraph("6.  Interpretacion de Resultados", E["seccion"]))
    story.extend(_parrafos_interpretacion(problema, E))

    # ── PIE FINAL ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDE))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Documento generado automaticamente por el Sistema de Transporte — "
        "Universidad de El Salvador · FMO",
        E["pie"]
    ))

    # ── BUILD ─────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)

    return os.path.abspath(ruta_salida)