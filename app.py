from flask import Flask, jsonify, request, Response
import xml.etree.ElementTree as ET
from flask_cors import CORS
from objetos import *
from unicodedata import normalize

NuevoDiccionario = Diccionario()
listamensajes = []

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origin": "*"}})

#--------------iniciales------------------------
@app.route('/', methods=['GET'])
def rutaInicial():
    return("<h1>Inicio de flask</h1>")

@app.route('/', methods=['POST'])
def rutaPost():
    objeto = {"Mensaje":"Prueba en flask"}
    return(jsonify(objeto))




@app.route('/Mensajes', methods=['POST'])
def cargaMensajes():

    global NuevoDiccionario
    global listamensajes

    entrada = request.data.decode('utf-8')
    xmlentrada = ET.fromstring(entrada)
    #solicitud_clasificacion = xmlentrada.getroot()

    for hijo in xmlentrada:
        if hijo.tag == "diccionario":
            for subhijo in hijo:
                if subhijo.tag == "sentimientos_positivos":
                    for sentimiento in subhijo:
                        palabra = sentimiento.text
                        palabra = palabra.replace(" ", "")
                        NuevoDiccionario.positivos.append(palabra)

                
                elif subhijo.tag == "sentimientos_negativos":
                    for sentimiento in subhijo:
                        palabra = sentimiento.text
                        palabra = palabra.replace(" ", "")
                        NuevoDiccionario.negativos.append(palabra)

                elif subhijo.tag == "empresas_analizar":
                    for empresa in subhijo:
                        for atributo in empresa: 
                            if atributo.tag == "nombre":
                                nombre = atributo.text
                                nombre = nombre.replace(" ", "")
                                NuevoEmpresa = Empresa()
                                NuevoEmpresa.nombre = nombre
                            elif atributo.tag == "servicio":
                                nombreServicio = atributo.attrib['nombre']
                                nombreServicio = nombreServicio.replace(" ", "")
                                NuevoServicio = Servicio()
                                NuevoServicio.nombre = nombreServicio
                                for alias in atributo:
                                    Alias_Servicio = alias.text
                                    Alias_Servicio = Alias_Servicio.replace(" ", "")
                                    NuevoServicio.alias.append(Alias_Servicio)
                                NuevoEmpresa.servicios.append(NuevoServicio)
                            NuevoDiccionario.empresas.append(NuevoEmpresa)



        elif hijo.tag == "lista_mensajes":
            for mensaje in hijo:
                Mensaje = mensaje.text
                trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
                Mensaje = normalize('NFKC', normalize('NFKD', Mensaje).translate(trans_tab))
                Mensaje = Mensaje.lower()

                linea = 1
                columna = 1
                centinela = '¬'
                buffer = ''
                estado = 0
                fecha = ""
                aux = ""

                Mensaje += centinela
                i = 0
                while i < len(Mensaje):
                    c = Mensaje[i]
                    if estado == 0:
                        if c.isalpha():
                            columna += 1
                            estado = 1
                        elif c.isdigit():
                            buffer += c
                            columna += 1
                            estado = 2
                        elif c == '#':
                            print('Se aceptó la cadena!')
                            break
                        else:
                            buffer += c
                            buffer = ''
                            columna += 1
                    elif estado == 1:
                        if c.isalpha():
                            linea += 1
                            columna = 1
                        elif c == ',':
                            linea += 1
                            columna = 1
                        elif c == ' ':
                            linea += 1
                            columna = 1
                            estado = 0
                        else:
                            columna += 1
                    elif estado == 2:
                        if c.isdigit():
                            buffer += c
                            linea += 1
                            columna = 1
                        elif c == "/":
                            buffer += c
                            linea += 1
                            columna = 1
                        elif c == ' ':
                            fecha += buffer
                            buffer = ''
                            estado = 3
                        else:
                            pass
                    elif estado == 3:
                        buffer += c

                    i += 1

                print(Mensaje)
                NuevoMensaje = Mensajes(Mensaje,fecha)
                listamensajes.append(NuevoMensaje)
    

    return jsonify({'Mensaje':'Se agregó exitosamente',})


@app.route('/Mensajes', methods=['GET'])
def retornoXML():
    global listamensajes
    global NuevoDiccionario

    lista_respuestas = ET.Element('lista_respuestas')
    ListaFechas = []
    for fecha in listamensajes:
        if fecha.fecha not in ListaFechas:
            ListaFechas.append(fecha.fecha)
    
    

    for fecha in ListaFechas:
        PositivosTotal = NegativosTotal = NeutrosTotal = 0
        Total = 0
        print(fecha)
        for mensaje in listamensajes:
            if mensaje.fecha == fecha:
                Total += 1
                Palabras = []
                Palabras1 = mensaje.mensaje.replace("\n", " ")
                Palabras1 = Palabras1.replace("\t", " ")
                Palabras1 = Palabras1.replace("\r", " ")
                Palabras1 = Palabras1.split(" ")
                for palabra in Palabras1:
                    palabra = ''.join(char for char in palabra if char.isalnum())
                    Palabras.append(palabra)
                pos = neg = neu = 0
                for palabra in Palabras:
                    if palabra in NuevoDiccionario.positivos:
                        pos += 1
                    elif palabra in NuevoDiccionario.negativos:
                        neg += 1
                    else:
                        pass
                if pos > neg:
                    PositivosTotal += 1
                elif neg > pos:
                    NegativosTotal += 1
                else:
                    NeutrosTotal += 1
                print(PositivosTotal,NegativosTotal,NeutrosTotal,Total)
            
                ListaNombres = []
                for empresa in NuevoDiccionario.empresas:
                    if empresa.nombre.lower() in Palabras:
                        empresa.total += 1
                        pos1 = neg1 = neu1 = 0
                        for palabra in Palabras:
                            if palabra in NuevoDiccionario.positivos:
                                pos1 += 1
                            elif palabra in NuevoDiccionario.negativos:
                                neg1 += 1
                            else:
                                pass
                        if pos > neg:
                            empresa.positivos += 1
                        elif neg > pos:
                            empresa.negativos += 1
                        else:
                            empresa.neutros += 1

                        print(empresa.nombre,empresa.total,empresa.positivos,empresa.negativos,empresa.neutros)

                        for servicio in empresa.servicios:
                            if servicio.nombre.lower() in Palabras:
                                servicio.total += 1
                                pos2 = neg2 = neu2 = 0
                                for palabra in Palabras:
                                    if palabra in NuevoDiccionario.positivos:
                                        pos1 += 1
                                    elif palabra in NuevoDiccionario.negativos:
                                        neg1 += 1
                                    else:
                                        pass
                                if pos > neg:
                                    servicio.positivos += 1
                                elif neg > pos:
                                    servicio.negativos += 1
                                else:
                                    servicio.neutros += 1
                            else:
                                for alias in servicio.alias:
                                    if alias.lower() in Palabras:
                                        servicio.total += 1
                                        pos2 = neg2 = neu2 = 0
                                        for palabra in Palabras:
                                            if palabra in NuevoDiccionario.positivos:
                                                pos1 += 1
                                            elif palabra in NuevoDiccionario.negativos:
                                                neg1 += 1
                                            else:
                                                pass
                                        if pos > neg:
                                            servicio.positivos += 1
                                        elif neg > pos:
                                            servicio.negativos += 1
                                        else:
                                            servicio.neutros += 1
                                    else:
                                        pass
                            print(servicio.nombre,servicio.total,servicio.positivos,servicio.negativos,servicio.neutros)

    return jsonify({'Mensaje':'Se agregó exitosamente',})            

                


if __name__ == "__main__":
    app.run( port=5000, debug=True)