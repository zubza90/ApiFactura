import os
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
import requests

app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

documentos = []

# Usar variables de entorno para URLs de servicios
CLIENTE_SERVICE_URL = os.getenv('CLIENTE_SERVICE_URL', 'http://localhost:27776/api/cliente')
PRODUCTO_SERVICE_URL = os.getenv('PRODUCTO_SERVICE_URL', 'http://localhost:27776/api/producto')

class BE(Resource):
    def post(self):
        body = request.get_json()
        response = requests.get(f"{CLIENTE_SERVICE_URL}/{body['client']}")
        cliente = response.json()
        productos = []
        total = 0
        for x in body['products']:
            response = requests.get(f"{PRODUCTO_SERVICE_URL}/{x['id']}")
            product = response.json()
            if product['stock'] >= int(x['quantity']):
                product['quantity'] = int(x['quantity'])
                total += (product['price'] * int(x['quantity']))
                productos.append(product)
            else:
                return {'message': f"Stock insuficiente del producto: {product['name']}"}, 404
        for x in productos:
            response = requests.put(f"{PRODUCTO_SERVICE_URL}/{x['id']}/reducirstock", json={'quantity': x['quantity']})
        data = {
            'documento': body['documento'],
            'cliente': cliente,
            'productos': productos,
            'total': total,
            'id': str(len(documentos) + 1).zfill(6)
        }
        documentos.append(data)
        return data
    
    def get(self, boleta_id):
        boleta = next((obj for obj in documentos if obj['id'] == boleta_id), None)
        return jsonify(boleta)

api.add_resource(BE, '/api/BE')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
