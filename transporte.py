from copy import deepcopy


def generar_matriz_costos(distancias, costo_km):
    filas = len(distancias)
    columnas = len(distancias[0])
    costos = []

    for i in range(filas):
        fila = []

        for j in range(columnas):
            fila.append(distancias[i][j] * costo_km)

        costos.append(fila)

    return costos


def balancear_problema(oferta, demanda, costos, producciones=None, ventas=None):
    oferta = deepcopy(oferta)
    demanda = deepcopy(demanda)
    costos = deepcopy(costos)
    producciones = deepcopy(producciones or [])
    ventas = deepcopy(ventas or [])

    total_oferta = sum(oferta)
    total_demanda = sum(demanda)

    if total_oferta == total_demanda:
        return oferta, demanda, costos, producciones, ventas

    if total_oferta > total_demanda:
        diferencia = total_oferta - total_demanda
        demanda.append(diferencia)
        ventas.append("Venta ficticia")

        for fila in costos:
            fila.append(0)

    else:
        diferencia = total_demanda - total_oferta
        oferta.append(diferencia)
        producciones.append("Produccion ficticia")

        nueva_fila = [0] * len(demanda)
        costos.append(nueva_fila)

    return oferta, demanda, costos, producciones, ventas


def metodo_costo_minimo(oferta, demanda, costos, producciones=None, ventas=None):
    oferta_restante = deepcopy(oferta)
    demanda_restante = deepcopy(demanda)
    costos = deepcopy(costos)
    producciones = producciones or [f"P{i + 1}" for i in range(len(oferta))]
    ventas = ventas or [f"V{j + 1}" for j in range(len(demanda))]
    asignaciones = []
    costo_total = 0

    while any(valor > 0 for valor in oferta_restante) and any(valor > 0 for valor in demanda_restante):
        menor = None

        for i, oferta_i in enumerate(oferta_restante):
            if oferta_i <= 0:
                continue

            for j, demanda_j in enumerate(demanda_restante):
                if demanda_j <= 0:
                    continue

                candidato = (costos[i][j], i, j)
                if menor is None or candidato < menor:
                    menor = candidato

        if menor is None:
            break

        costo_unitario, i, j = menor
        cantidad = min(oferta_restante[i], demanda_restante[j])
        costo_asignacion = cantidad * costo_unitario

        asignaciones.append({
            "origen": producciones[i],
            "destino": ventas[j],
            "cantidad": cantidad,
            "costo_unitario": costo_unitario,
            "costo": costo_asignacion
        })

        oferta_restante[i] -= cantidad
        demanda_restante[j] -= cantidad
        costo_total += costo_asignacion

    return asignaciones, costo_total


def resolver_problema(problema):
    problema.matriz_costos = generar_matriz_costos(
        problema.distancias,
        problema.costo_km
    )

    (
        problema.oferta_balanceada,
        problema.demanda_balanceada,
        problema.costos_balanceados,
        problema.producciones_balanceadas,
        problema.ventas_balanceadas
    ) = balancear_problema(
        problema.oferta,
        problema.demanda,
        problema.matriz_costos,
        problema.producciones,
        problema.ventas
    )

    problema.asignaciones, problema.costo_total = metodo_costo_minimo(
        problema.oferta_balanceada,
        problema.demanda_balanceada,
        problema.costos_balanceados,
        problema.producciones_balanceadas,
        problema.ventas_balanceadas
    )

    return problema
