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
    trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
    entrada = normalize('NFKC', normalize('NFKD', entrada).translate(trans_tab))
    entrada = entrada.lower()
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
                        elif c == '¬':
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
        respuesta = ET.SubElement(lista_respuestas, 'respuesta')
        fecha_respuesta = ET.SubElement(respuesta, 'fecha')
        fecha_respuesta.text = fecha
        mensajes = ET.SubElement(respuesta, 'mensajes')
        
        for empresa in NuevoDiccionario.empresas:
            empresa.total = empresa.negativos = empresa.neutros = empresa.positivos = 0
            for servicio in empresa.servicios:
                servicio.total = servicio.negativos = servicio.neutros = servicio.positivos = 0


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
        total_mensajes = ET.SubElement(mensajes, 'total')
        positivos_mensajes = ET.SubElement(mensajes, 'positivos')
        negativos_mensajes = ET.SubElement(mensajes, 'negativos')
        neutros_mensajes = ET.SubElement(mensajes, 'neutros')

        total_mensajes.text = str(Total)
        positivos_mensajes.text = str(PositivosTotal)
        negativos_mensajes.text = str(NegativosTotal)
        neutros_mensajes.text = str(NeutrosTotal)            
        analisis = ET.SubElement(respuesta, 'analisis')

        for empresa in NuevoDiccionario.empresas:
            print(empresa.nombre) 
        
        for empresa in NuevoDiccionario.empresas:
            empresaET = ET.SubElement(analisis, 'empresa', nombre=empresa.nombre)
            mensajesEt = ET.SubElement(empresaET, 'mensajes')
                

            for mensaje in listamensajes:
                if mensaje.fecha == fecha:
                    Palabras = []
                    Palabras1 = mensaje.mensaje.replace("\n", " ")
                    Palabras1 = Palabras1.replace("\t", " ")
                    Palabras1 = Palabras1.replace("\r", " ")
                    Palabras1 = Palabras1.split(" ")
                    for palabra in Palabras1:
                        palabra = ''.join(char for char in palabra if char.isalnum())
                        Palabras.append(palabra)
            
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
                        if pos1 > neg1:
                            empresa.positivos += 1
                        elif neg1 > pos1:
                            empresa.negativos += 1
                        else:
                            empresa.neutros += 1

            empresa_total = ET.SubElement(mensajesEt, 'total')
            empresa_positivos = ET.SubElement(mensajesEt, 'positivos')
            empresa_negativos = ET.SubElement(mensajesEt, 'negativos')
            empresa_neutros = ET.SubElement(mensajesEt, 'neutros')

            empresa_total.text = str(empresa.total)
            empresa_positivos.text = str(empresa.positivos)
            empresa_negativos.text = str(empresa.negativos)
            empresa_neutros.text = str(empresa.neutros)

            print(empresa.nombre,empresa.total,empresa.positivos,empresa.negativos,empresa.neutros)

            for servicio in empresa.servicios:
                servicioET = ET.SubElement(empresaET, 'servicio', nombre=servicio.nombre)
                mensajeET2 = ET.SubElement(servicioET, 'mensajes')

                for mensaje in listamensajes:
                    if mensaje.fecha == fecha:
                        Palabras = []
                        Palabras1 = mensaje.mensaje.replace("\n", " ")
                        Palabras1 = Palabras1.replace("\t", " ")
                        Palabras1 = Palabras1.replace("\r", " ")
                        Palabras1 = Palabras1.split(" ")
                        for palabra in Palabras1:
                            palabra = ''.join(char for char in palabra if char.isalnum())
                            Palabras.append(palabra)
                
                        if servicio.nombre.lower() in Palabras:
                            servicio.total += 1
                            pos2 = neg2 = neu2 = 0
                            for palabra in Palabras:
                                if palabra in NuevoDiccionario.positivos:
                                    pos2 += 1
                                elif palabra in NuevoDiccionario.negativos:
                                    neg2 += 1
                                else:
                                    pass
                            if pos2 > neg2:
                                servicio.positivos += 1
                            elif neg2 > pos2:
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
                                            pos2 += 1
                                        elif palabra in NuevoDiccionario.negativos:
                                            neg2 += 1
                                        else:
                                            pass
                                    if pos2 > neg2:
                                        servicio.positivos += 1
                                    elif neg2 > pos2:
                                        servicio.negativos += 1
                                    else:
                                        servicio.neutros += 1
                                else:
                                    pass

                servicio_total = ET.SubElement(mensajeET2, 'total')
                servicio_positivos = ET.SubElement(mensajeET2, 'positivos')
                servicio_negativos = ET.SubElement(mensajeET2, 'negativos')
                servicio_neutros = ET.SubElement(mensajeET2, 'neutros')

                servicio_total.text = str(servicio.total)
                servicio_positivos.text = str(servicio.positivos)
                servicio_negativos.text = str(servicio.negativos)
                servicio_neutros.text = str(servicio.neutros)
                
                servicio.total = servicio.negativos = servicio.neutros = servicio.positivos = 0


        




    mydata = ET.tostring(lista_respuestas)
    myfile = open('ListasRespuestas.xml','wb')
    myfile.write(mydata)                  

    return mydata            

@app.route('/Peticiones/MensajePrueba', methods=['POST'])
def MensajePrueba():
    global NuevoDiccionario
    global listamensajes
    global mydata

    entrada = request.data.decode('utf-8')
    trans_tab = dict.fromkeys(map(ord, u'\u0301\u0308'), None)
    entrada = normalize('NFKC', normalize('NFKD', entrada).translate(trans_tab))
    entrada = entrada.lower()
    xmlentrada = ET.fromstring(entrada)
    Mensaje=""
    Variables = []
    
    linea = 1
    columna = 1
    centinela = '¬'
    buffer = ''
    estado = 0
    fecha = ""
    aux = ""

    Mensaje = xmlentrada.text
        
    Mensaje += centinela
    i = 0
    print(Mensaje)

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
            elif c == '¬':
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
            elif c == ':':
                columna += 1
                estado = 4
                i+=1
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
            estado = 0

        elif estado == 4:
            
            if c == ' ':
                estado = 0
                Variables.append(buffer)
                buffer =''
            else:
                buffer += c

        i += 1
        print("Carac: "+c+" est: "+str(estado))

    print(Variables)
    respuesta = ET.Element('respuesta')
    fecha_respuesta = ET.SubElement(respuesta, 'fecha')
    fecha_respuesta.text = fecha

    red_social = ET.SubElement(respuesta, 'red_social')
    red_social.text = Variables[2]

    usuario = ET.SubElement(respuesta, 'usuario')
    usuario.text = Variables[1]

    
    empresasEt = ET.SubElement(respuesta, 'empresas')
    pos = neg = 0
    Palabras = []
    Palabras1 = Mensaje.replace("\n", " ")
    Palabras1 = Palabras1.replace("\t", " ")
    Palabras1 = Palabras1.replace("\r", " ")
    Palabras1 = Palabras1.split(" ")
    for palabra in Palabras1:
        palabra = ''.join(char for char in palabra if char.isalnum())
        Palabras.append(palabra)
    
    for empresa in NuevoDiccionario.empresas:
        if empresa.nombre.lower() in Palabras:
            empresaET = ET.SubElement(empresasEt, 'empresa')
            empresasEt.text = empresa.nombre

            for servicio in empresa.servicios:
                if servicio.nombre.lower() in Palabras:
                    servicioET = ET.SubElement(empresaET, 'servicio')
                    servicioET.text = servicio.nombre
                else:
                    for alias in servicio.alias:
                        if alias.lower() in Palabras:
                            servicioET = ET.SubElement(empresaET, 'servicio')
                            servicioET.text = servicio.nombre
                        else:
                            pass
    
    Palabras1 = Mensaje.replace("\n", " ")
    Palabras1 = Palabras1.replace("\t", " ")
    Palabras1 = Palabras1.replace("\r", " ")
    Palabras1 = Palabras1.split(" ")
    for palabra in Palabras1:
        palabra = ''.join(char for char in palabra if char.isalnum())
        Palabras.append(palabra)
        
    for palabra in Palabras:
        if palabra in NuevoDiccionario.positivos:
            pos += 1
        elif palabra in NuevoDiccionario.negativos:
            neg += 1
        else:
            pass
    
    palabras_positivas = ET.SubElement(respuesta, 'palabras_positivas')
    palabras_positivas.text = str(pos)

    palabras_negativas = ET.SubElement(respuesta, 'palabras_negativas')
    palabras_negativas.text = str(neg)

    sentimiento_positivo = ET.SubElement(respuesta, 'sentimiento_positivo')
    sentimiento_positivo.text = str((pos/(pos+neg))*100)+"%"

    sentimiento_negativo = ET.SubElement(respuesta, 'sentimiento_negativo')
    sentimiento_negativo.text = str((neg/(pos+neg))*100)+"%"

    sentimiento_analizado = ET.SubElement(respuesta, 'sentimiento_analizado')
    if pos > neg:
        sentimiento_analizado.text = "Positivo"
    elif neg > pos:
        sentimiento_analizado.text = "Negativo"
    else:
        sentimiento_analizado.text = "Neutro"

    mydata = ET.tostring(respuesta)
    myfile = open('Mensaje.xml','wb')
    myfile.write(mydata)                  

    return jsonify({'Mensaje':'Se agregó exitosamente',}) 

@app.route('/Peticiones/MensajePrueba', methods=['GET'])
def MensajePruebaRet():
    global mydata

    return mydata


    


                


if __name__ == "__main__":
    app.run( port=5000, debug=True)