def validar_balance(oferta, demanda):
    total_oferta = sum(oferta)
    total_demanda = sum(demanda)

    if total_oferta == total_demanda:
        return "BALANCEADO"

    if total_oferta > total_demanda:
        return "OFERTA MAYOR"

    return "DEMANDA MAYOR"


def total_oferta(oferta):
    return sum(oferta)


def total_demanda(demanda):
    return sum(demanda)


def convertir_numero(valor, nombre, minimo=0, entero=False):
    texto = str(valor).strip().replace(",", ".")

    if texto == "":
        raise ValueError(f"El campo '{nombre}' no puede quedar vacio.")

    try:
        numero = int(texto) if entero else float(texto)
    except ValueError as error:
        raise ValueError(f"El campo '{nombre}' debe ser numerico.") from error

    if numero < minimo:
        raise ValueError(f"El campo '{nombre}' debe ser mayor o igual a {minimo}.")

    return numero


def validar_matriz(distancias, oferta, demanda):
    if not oferta:
        raise ValueError("Debe ingresar al menos un centro de produccion.")

    if not demanda:
        raise ValueError("Debe ingresar al menos un centro de venta.")

    if len(distancias) != len(oferta):
        raise ValueError("La matriz de distancias no coincide con la oferta.")

    for fila in distancias:
        if len(fila) != len(demanda):
            raise ValueError("La matriz de distancias no coincide con la demanda.")
