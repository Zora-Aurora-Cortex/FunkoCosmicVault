import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
import os
import time

load_dotenv()
client = OpenAI(api_key=os.getenv('XAI_API_KEY'), base_url="https://api.x.ai/v1")

BATCH_SIZE = 50

def generate_seria_description(producto):
    prompt = f"Genera una descripción factual, detallada y SEO-friendly para un producto de e-commerce en México, usando jerga casual mexicana. Incluye características técnicas, materiales, medidas, y beneficios. Producto: {producto['descripcion_corta']} Marca: {producto['marca']} Tema: {producto['tema']} Etiquetas: {producto['etiquetas']} Medidas: {producto['alto_cm']}x{producto['largo_cm']}x{producto['ancho_cm']} cm, Peso: {producto['peso_g']} g, Origen: {producto['pais_origen']}"
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def generate_marciana_description(producto):
    prompt = f"Genera una descripción creativa y viral 'marciana' para redes sociales en español mexicano, con jerga local. Hazla divertida, cósmica, con emojis y referencias pop. Producto: {producto['descripcion_corta']} Marca: {producto['marca']} Tema: {producto['tema']} Etiquetas: {producto['etiquetas']}"
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.8
    )
    return response.choices[0].message.content.strip()

# Conectar a SQLite
conn = sqlite3.connect('data/productos.db')
cursor = conn.cursor()

# Obtener lote de productos con descripciones vacías
cursor.execute("""
    SELECT * FROM productos 
    WHERE (descripcion_seria IS NULL OR descripcion_seria = '') 
    AND cantidad_stock > 0 
    LIMIT ?
""", (BATCH_SIZE,))
productos = cursor.fetchall()

for row in productos:
    sku = row[0]
    producto = dict(zip(['sku_interno', 'descripcion_corta', 'marca', 'precio_costo', 'precio_venta', 'moneda', 'cantidad_stock', 'fotos_extra', 'video_url', 'tema', 'etiquetas', 'descripcion_seria', 'descripcion_marciana', 'alto_cm', 'largo_cm', 'ancho_cm', 'peso_g', 'pais_origen', 'estado'], row))
    
    # Generar descripciones
    seria = generate_seria_description(producto)
    marciana = generate_marciana_description(producto)
    
    # Actualizar en SQLite
    cursor.execute("""
        UPDATE productos 
        SET descripcion_seria = ?, descripcion_marciana = ? 
        WHERE sku_interno = ?
    """, (seria, marciana, sku))
    
    print(f"Descripciones generadas para {sku}: Seria ({len(seria)} chars), Marciana ({len(marciana)} chars)")
    time.sleep(1)  # Pausa para evitar límites de API

conn.commit()
conn.close()

print(f"Completado lote de {len(productos)} productos.")
