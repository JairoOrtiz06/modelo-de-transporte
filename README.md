# Sistema de Transporte - Metodo de Costo Minimo

Proyecto en Python para resolver problemas del modelo de transporte usando el metodo de costo minimo.

## Como ejecutar

```bash
python main.py
```

## Funciones principales

- Ingreso del nombre de la empresa.
- Cantidad modificable de centros de produccion y centros de venta.
- Registro detallado de nombres, oferta, demanda y distancias en kilometros.
- Registro del costo por kilometro.
- Identificacion automatica de problema balanceado o no balanceado.
- Balanceo automatico mediante centro ficticio cuando la oferta y demanda no coinciden.
- Calculo automatico de asignaciones con el metodo de costo minimo.
- Presentacion del costo total de transporte y de cada asignacion.
- Tabla de costos calculados a partir de distancia por costo por kilometro.
- Graficas de oferta y demanda.

## Interpretacion

La tabla de asignaciones indica cuanto se debe transportar desde cada centro de produccion hacia cada centro de venta. El costo unitario se obtiene multiplicando la distancia por el costo por kilometro. El costo total es la suma de todas las asignaciones realizadas por el metodo de costo minimo.

Si aparece una produccion o venta ficticia, significa que el problema original no estaba balanceado. Ese centro ficticio se agrega con costo cero para poder aplicar correctamente el metodo.
