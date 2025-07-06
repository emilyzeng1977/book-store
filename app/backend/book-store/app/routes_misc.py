from flask import jsonify, request
import socket
import requests
import logging
from . import app
from .config import PRICE_SERVER, PRICE_PORT

@app.route('/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'World')
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return jsonify({'message': f"Hello, {name}! Server IP: {ip}"})

@app.route('/call-price', methods=['GET'])
def call_price():
    book_id = request.args.get('book_id')
    price_service_url = f"http://{PRICE_SERVER}:{PRICE_PORT}/price"
    try:
        response = requests.get(price_service_url, params={'book_id': book_id}, timeout=2)
        response.raise_for_status()
        return jsonify({
            "message": "Call price Service",
            "server_name": socket.gethostname(),
            "server_ip": socket.gethostbyname(socket.gethostname()),
            "response from price server": response.json()
        })
    except Exception as e:
        logging.error(f"Price service error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Hello, bookStore!"}), 200
