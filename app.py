from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from models import db, Producto, Pedido
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecreto123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:75266245@localhost/delicias_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img'

db.init_app(app)

# -------------------- RUTAS PÚBLICAS --------------------
@app.route('/')
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

@app.route('/productos')
def productos():
    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

@app.route('/carrito')
def carrito():
    return render_template('carrito.html')

@app.route('/pago')
def pagos():
    return render_template('pago.html')

@app.route('/api/productos', methods=['POST'])
def api_productos():
    ids = request.json.get('ids', [])
    productos = Producto.query.filter(Producto.id.in_(ids)).all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'descripcion': p.descripcion,
        'precio': float(p.precio),
        'foto': p.foto
    } for p in productos])

@app.route('/api/resumen')
def api_resumen():
    ids = session.get('carrito', [])
    productos = Producto.query.filter(Producto.id.in_(ids)).all()
    cantidades = {i: ids.count(i) for i in ids}
    resumen = [{
        'nombre': p.nombre,
        'precio': float(p.precio),
        'cantidad': cantidades[p.id],
        'subtotal': float(p.precio) * cantidades[p.id]
    } for p in productos]
    total = sum(item['subtotal'] for item in resumen)
    return jsonify({'items': resumen, 'total': total})

# -------------------- LOGIN ADMIN --------------------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['admin_logged'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Credenciales incorrectas'
    return render_template('admin/login.html', error=error)

@app.route('/admin/logout')
def logout_admin():
    session.pop('admin_logged', None)
    return redirect(url_for('index'))

# -------------------- PANEL ADMIN --------------------
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    productos = Producto.query.all()
    return render_template('admin/dashboard.html', productos=productos)

# -------------------- CRUD PRODUCTOS --------------------
@app.route('/admin/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        foto_file = request.files['foto']
        filename = None

        if foto_file and foto_file.filename != '':
            filename = secure_filename(foto_file.filename)
            foto_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        prod = Producto(
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            precio=request.form['precio'],
            foto=filename
        )
        db.session.add(prod)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/productos_admin.html', producto=None)

@app.route('/admin/productos/editar/<int:prod_id>', methods=['GET', 'POST'])
def editar_producto(prod_id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    prod = Producto.query.get_or_404(prod_id)
    if request.method == 'POST':
        prod.nombre = request.form['nombre']
        prod.descripcion = request.form['descripcion']
        prod.precio = request.form['precio']
        prod.foto = request.form['foto']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/productos_admin.html', producto=prod)

@app.route('/admin/productos/borrar/<int:prod_id>')
def borrar_producto(prod_id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))

    prod = Producto.query.get_or_404(prod_id)
    db.session.delete(prod)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# -------------------- PEDIDOS --------------------
@app.route('/admin/pedidos')
def mostrar_pedidos():
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    return render_template('admin/pedidos.html', pedidos=pedidos)

@app.route('/admin/pedidos/<int:pedido_id>')
def ver_pedido(pedido_id):
    if not session.get('admin_logged'):
        return redirect(url_for('admin_login'))
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('admin/pedido_detalle.html', pedido=pedido)

# -------------------- API GUARDAR PEDIDO --------------------
@app.route('/api/guardar_pedido', methods=['POST'])
def guardar_pedido():
    data = request.get_json()

    if not data or len(data) == 0:
        return jsonify({'error': 'El carrito está vacío.'}), 400

    try:
        total = sum(float(item['precio']) * int(item['cantidad']) for item in data)

        detalles = ""
        for item in data:
            subtotal = float(item['precio']) * int(item['cantidad'])
            detalles += f"{item['nombre']} x{item['cantidad']} - S/. {subtotal:.2f}\n"

        nuevo_pedido = Pedido(
            cliente_nombre="Cliente web",
            total=total,
            fecha=datetime.now(),
        )
        # Si tu tabla tiene campo 'detalles':
        if hasattr(nuevo_pedido, 'detalles'):
            nuevo_pedido.detalles = detalles

        db.session.add(nuevo_pedido)
        db.session.commit()

        return jsonify({'mensaje': 'Pedido guardado correctamente.'}), 200

    except Exception as e:
        print("Error al guardar pedido:", e)
        return jsonify({'error': 'Error al guardar el pedido.'}), 500

# -------------------- EJECUCIÓN --------------------
if __name__ == '__main__':
    app.run(debug=True)
