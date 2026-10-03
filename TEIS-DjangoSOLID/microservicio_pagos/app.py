from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/api/v2/comprar', methods=['POST'])
def comprar():
    datos = request.get_json(silent=True) or {}

    producto_id = datos.get('producto_id')
    if producto_id is None:
        return jsonify({'error': 'Falta el ID del producto'}), 400

    return jsonify({
        'mensaje': 'Compra procesada exitosamente por el Microservicio Flask (v2)',
        'producto_id': producto_id,
        'cantidad': datos.get('cantidad', 1),
        'status': 'Aprobado',
    }), 200
