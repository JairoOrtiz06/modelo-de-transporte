import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import io
from reportlab.platypus import Image as RLImage


PALETA = ["#3B82F6", "#14B8A6", "#F59E0B", "#22C55E", "#A855F7", "#EF4444"]


def grafica_asignaciones(problema):
    asignaciones = [a for a in problema.asignaciones
                    if "ficticia" not in a["origen"].lower()
                    and "ficticia" not in a["destino"].lower()]

    if not asignaciones:
        return

    origenes = list(dict.fromkeys(a["origen"] for a in asignaciones))
    destinos = list(dict.fromkeys(a["destino"] for a in asignaciones))

    n_orig  = len(origenes)
    n_dest  = len(destinos)
    x       = np.arange(n_dest)
    ancho   = 0.7 / max(n_orig, 1)

    fig, ax = plt.subplots(figsize=(max(8, n_dest * 2), 6))
    fig.patch.set_facecolor("#0B1628")
    ax.set_facecolor("#111F35")

    for idx, origen in enumerate(origenes):
        alturas = []
        for destino in destinos:
            asig = next((a for a in asignaciones
                         if a["origen"] == origen and a["destino"] == destino), None)
            alturas.append(asig["cantidad"] if asig else 0)

        offset = (idx - n_orig / 2 + 0.5) * ancho
        barras = ax.bar(x + offset, alturas, width=ancho * 0.9,
                        color=PALETA[idx % len(PALETA)],
                        label=origen, zorder=3)

        for barra, h in zip(barras, alturas):
            if h > 0:
                ax.text(barra.get_x() + barra.get_width() / 2,
                        h + max(alturas) * 0.01,
                        str(int(h)),
                        ha="center", va="bottom",
                        fontsize=8, color="#F1F5F9", fontweight="bold")

    # Estilo
    ax.set_xticks(x)
    ax.set_xticklabels(destinos, color="#94A3B8", fontsize=10)
    ax.set_yticklabels([str(int(v)) for v in ax.get_yticks()],
                       color="#94A3B8", fontsize=9)
    ax.set_xlabel("Centros de venta", color="#64748B", fontsize=11, labelpad=10)
    ax.set_ylabel("Unidades asignadas", color="#64748B", fontsize=11, labelpad=10)
    ax.set_title(
        f"Distribución de asignaciones — {problema.empresa}",
        color="#F1F5F9", fontsize=13, fontweight="bold", pad=14
    )

    for spine in ax.spines.values():
        spine.set_edgecolor("#1E3A5F")
    ax.yaxis.grid(True, color="#1E3A5F", linestyle="--", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    leyenda = ax.legend(
        handles=[mpatches.Patch(color=PALETA[i], label=o)
                 for i, o in enumerate(origenes)],
        facecolor="#0C1A2E", edgecolor="#1E3A5F",
        labelcolor="#F1F5F9", fontsize=9,
        loc="upper right"
    )

    costo_str = f"Costo mínimo total: ${problema.costo_total:,.2f}"
    ax.text(0.01, 0.98, costo_str,
            transform=ax.transAxes,
            fontsize=9, color="#22C55E",
            va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.4",
                      facecolor="#0C1F14",
                      edgecolor="#1a4a2a"))

    plt.tight_layout()
    plt.show()

def grafica_asignaciones_bytes(problema):
    """Genera la gráfica y la retorna como BytesIO para incrustar en PDF."""
    asignaciones = [a for a in problema.asignaciones
                    if "ficticia" not in a["origen"].lower()
                    and "ficticia" not in a["destino"].lower()]
    if not asignaciones:
        return None

    origenes = list(dict.fromkeys(a["origen"] for a in asignaciones))
    destinos = list(dict.fromkeys(a["destino"] for a in asignaciones))
    n_orig   = len(origenes)
    n_dest   = len(destinos)
    x        = np.arange(n_dest)
    ancho    = 0.7 / max(n_orig, 1)

    fig, ax = plt.subplots(figsize=(max(8, n_dest * 2), 5))
    fig.patch.set_facecolor("#0B1628")
    ax.set_facecolor("#111F35")

    for idx, origen in enumerate(origenes):
        alturas = []
        for destino in destinos:
            asig = next((a for a in asignaciones
                         if a["origen"] == origen and a["destino"] == destino), None)
            alturas.append(asig["cantidad"] if asig else 0)

        offset = (idx - n_orig / 2 + 0.5) * ancho
        barras = ax.bar(x + offset, alturas, width=ancho * 0.9,
                        color=PALETA[idx % len(PALETA)],
                        label=origen, zorder=3)

        for barra, h in zip(barras, alturas):
            if h > 0:
                ax.text(barra.get_x() + barra.get_width() / 2,
                        h + max(alturas) * 0.02,
                        str(int(h)),
                        ha="center", va="bottom",
                        fontsize=8, color="#F1F5F9", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(destinos, color="#94A3B8", fontsize=10)
    ax.tick_params(axis="y", colors="#94A3B8", labelsize=9)
    ax.set_xlabel("Centros de venta",    color="#64748B", fontsize=11, labelpad=8)
    ax.set_ylabel("Unidades asignadas",  color="#64748B", fontsize=11, labelpad=8)
    ax.set_title(f"Distribucion de asignaciones — {problema.empresa}",
                 color="#F1F5F9", fontsize=12, fontweight="bold", pad=12)

    for spine in ax.spines.values():
        spine.set_edgecolor("#1E3A5F")
    ax.yaxis.grid(True, color="#1E3A5F", linestyle="--", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

    ax.legend(
        handles=[mpatches.Patch(color=PALETA[i], label=o) for i, o in enumerate(origenes)],
        facecolor="#0C1A2E", edgecolor="#1E3A5F",
        labelcolor="#F1F5F9", fontsize=9, loc="upper right"
    )

    costo_str = f"Costo minimo total: ${problema.costo_total:,.2f}"
    ax.text(0.01, 0.98, costo_str, transform=ax.transAxes,
            fontsize=9, color="#22C55E", va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.4",
                      facecolor="#0C1F14", edgecolor="#1a4a2a"))

    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)   # ← importante: libera memoria, no abre ventana
    buf.seek(0)
    return buf