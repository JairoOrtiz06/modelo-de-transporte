class ProblemaTransporte:
    def __init__(
        self,
        empresa="",
        producciones=None,
        ventas=None,
        oferta=None,
        demanda=None,
        distancias=None,
        costo_km=0
    ):
        self.empresa = empresa.strip()
        self.producciones = producciones or []
        self.ventas = ventas or []
        self.oferta = oferta or []
        self.demanda = demanda or []
        self.distancias = distancias or []
        self.costo_km = costo_km
        self.matriz_costos = []
        self.asignaciones = []
        self.costo_total = 0
        self.estado_balance = ""
        self.oferta_balanceada = []
        self.demanda_balanceada = []
        self.costos_balanceados = []
        self.producciones_balanceadas = []
        self.ventas_balanceadas = []
