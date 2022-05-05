class Diccionario():
    def __init__(self):
        self.positivos = []
        self.negativos = []
        self.empresas = []

class Empresa():
    def __init__(self):
        self.nombre = None
        self.servicios = []
        self.total = 0
        self.positivos = 0
        self.negativos = 0
        self.neutros = 0

class Servicio():
    def __init__(self):
        self.nombre = None
        self.alias = []
        self.total = 0
        self.positivos = 0
        self.negativos = 0
        self.neutros = 0

class Mensajes():
    def __init__(self, mensaje, fecha):
        self.mensaje = mensaje
        self.fecha = fecha
