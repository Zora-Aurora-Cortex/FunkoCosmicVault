from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import mercadopago
import os

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask y configuración
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/productos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configurar Mercado Pago
mp_sdk = mercadopago.SDK(os.getenv('MERCADO_PAGO_ACCESS_TOKEN'))

# Modelo de Producto
class Producto(db.Model):
    __tablename__ = 'productos'
    sku_interno = db.Column(db.String, primary_key=True)
    descripcion_corta = db.Column(db.String)
    marca = db.Column(db.String)
    precio_costo = db.Column(db.Float)
    precio_venta = db.Column(db.Float)
    moneda = db.Column(db.String)
    cantidad_stock = db.Column(db.Integer)
    fotos_extra = db.Column(db.String)
    video_url = db.Column(db.String)
    tema = db.Column(db.String)
    etiquetas = db.Column(db.String)
    descripcion_seria = db.Column(db.String)
    descripcion_marciana = db.Column(db.String)
    alto_cm = db.Column(db.Float)
    largo_cm = db.Column(db.Float)
    ancho_cm = db.Column(db.Float)
    peso_g = db.Column(db.Float)
    pais_origen = db.Column(db.String)
    estado = db.Column(db.String)

# Ruta raíz: Listado de productos
@app.route('/')
def index():
    productos = Producto.query.filter(Producto.cantidad_stock > 0).all()
    return render_template('index.html', productos=productos)

# Ruta de producto individual
@app.route('/producto/<sku>')
def producto(sku):
    producto = Producto.query.get_or_404(sku)
    return render_template('producto.html', producto=producto)

# Ruta de checkout con Mercado Pago
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Crear preferencia de pago para Mystery Box
        preference_data = {
            "items": [
                {
                    "title": "Mystery Box FunkoCosmicVault",
                    "quantity": 1,
                    "unit_price": 500.0,
                    "currency_id": "MXN"
                }
            ],
            "back_urls": {
                "success": url_for('index', _external=True),
                "failure": url_for('index', _external=True),
                "pending": url_for('index', _external=True)
            },
            "auto_return": "approved"
        }
        preference_response = mp_sdk.preference().create(preference_data)
        preference = preference_response["response"]
        return redirect(preference["init_point"])  # Redirige a Mercado Pago
    return render_template('checkout.html')

if __name__ == '__main__':
    app.run(debug=True)
