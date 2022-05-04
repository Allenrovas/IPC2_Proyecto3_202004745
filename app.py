from flask import Flask, jsonify, request, Response
import xml.etree.ElementTree as ET
from flask_cors import CORS


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


    

    entrada = request.data.decode('utf-8')
    print(entrada)
    xmlentrada = ET.fromstring(entrada)


    return jsonify({'Mensaje':'Se agregaron las facturas exitosamente',})




if __name__ == "__main__":
    app.run( port=5000, debug=True)