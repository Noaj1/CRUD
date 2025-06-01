from flask import Flask, request, redirect, session, render_template
import pyodbc
import csv
import io
from flask import Response

app = Flask(__name__)
app.secret_key = 'esto-es-una-clave-secreta'

def get_db_connection():
    return pyodbc.connect(
        'DRIVER={SQL Server};'
        'SERVER=DESKTOP-DQFUD2P\\SQLEXPRESS;'
        'DATABASE=CRUD;'
        'Trusted_Connection=yes;'
    )

# --- RUTA INICIAL ---
@app.route('/')
def home():
    return redirect('/login')

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE usuario = ? AND password = ?", (usuario, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user.id
            session['usuario'] = usuario
            return redirect('/contactos')
        else:
            error = "Usuario o contraseña incorrectos"
            return render_template('login.html', error=error)
    return render_template('login.html')

# --- REGISTRO ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM users WHERE usuario = ?", (usuario,))
        existente = cursor.fetchone()

        if existente:
            conn.close()
            return render_template('registro.html', error="El usuario ya existe. Intenta con otro nombre.")

        # Insertar si no existe
        cursor.execute("INSERT INTO users (usuario, password) VALUES (?, ?)", (usuario, password))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('registro.html')


# --- LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- LISTAR CONTACTOS ---
@app.route('/contactos')
def contactos():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, correo FROM contactos WHERE usuario_id = ?", (session['user_id'],))
    contactos = cursor.fetchall()
    conn.close()

    return render_template('contactos.html', usuario=session['usuario'], contactos=contactos)

# --- AGREGAR CONTACTO ---
@app.route('/contactos/agregar', methods=['GET', 'POST'])
def agregar_contacto():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contactos (nombre, telefono, correo, usuario_id) VALUES (?, ?, ?, ?)",
                       (nombre, telefono, correo, session['user_id']))
        conn.commit()
        conn.close()
        return redirect('/contactos')

    return render_template('agregar_contacto.html')

# --- EDITAR CONTACTO ---
@app.route('/contactos/editar/<int:id>', methods=['GET', 'POST'])
def editar_contacto(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']

        cursor.execute("UPDATE contactos SET nombre = ?, telefono = ?, correo = ? WHERE id = ? AND usuario_id = ?",
                       (nombre, telefono, correo, id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect('/contactos')

    cursor.execute("SELECT nombre, telefono, correo FROM contactos WHERE id = ? AND usuario_id = ?", (id, session['user_id']))
    contacto = cursor.fetchone()
    conn.close()

    if contacto is None:
        return "Contacto no encontrado o no autorizado", 404
    
    return render_template('editar_contacto.html', nombre=contacto[0], telefono=contacto[1], correo=contacto[2])

# --- ELIMINAR CONTACTO ---
@app.route('/contactos/eliminar/<int:id>', methods=['POST'])
def eliminar_contacto(id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contactos WHERE id = ? AND usuario_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/contactos')

@app.route('/contactos/exportar', methods=['GET'])
def exportar_contactos():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, telefono, correo FROM contactos WHERE usuario_id = ?", (session['user_id'],))
    contactos = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nombre', 'Telefono', 'Correo'])
    for contacto in contactos:
        writer.writerow(contacto)

    output.seek(0)
    
    return Response(output.getvalue(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment;filename=contactos.csv"})

# --- INICIAR APP ---
if __name__ == '__main__':
    print("🚀 Servidor corriendo en http://localhost:5000")
    app.run(debug=True)
