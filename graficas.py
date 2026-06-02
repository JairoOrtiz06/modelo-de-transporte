import matplotlib.pyplot as plt


def _mostrar_barras(nombres, valores, titulo, etiqueta_x, color):
    plt.figure(figsize=(8, 5))
    plt.bar(nombres, valores, color=color)
    plt.title(titulo)
    plt.xlabel(etiqueta_x)
    plt.ylabel("Cantidad")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.show()


def grafica_oferta(nombres, oferta):
    _mostrar_barras(nombres, oferta, "Oferta por centro de produccion", "Centros de produccion", "#2E86AB")


def grafica_demanda(nombres, demanda):
    _mostrar_barras(nombres, demanda, "Demanda por centro de venta", "Centros de venta", "#F18F01")
