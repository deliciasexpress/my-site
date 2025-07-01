from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10,2))
    foto = db.Column(db.String(255))



class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Float)
    estado = db.Column(db.String(50), default='Pendiente')
    fecha = db.Column(db.DateTime)
    detalles = db.Column(db.Text)
