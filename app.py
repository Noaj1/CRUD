from flask import Flask, request, redirect, session, render_template
import psycopg2
import os
import csv
import io
from flask import Response

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'esto-es-una-clave-secreta')

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get('PGHOST'),
        database=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        port=int(os.environ.get('PGPORT', 5432))  # Convertir puerto a entero
    )

# --- RUTA INICIAL ---
@app.route('/')
def home():
    return redirect('/login')

# --- LOGIN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE usuario = %s AND password = %s", (usuario, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['usuario'] = usuario
            return redirect('/contactos')
        else:
            error = "Usuario o contraseña incorrectos"
    return render_template('login.html', error=error)

# --- REGISTRO ---
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    error = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE usuario = %s", (usuario,))
        existente = cursor.fetchone()

        if existente:
            error = "El usuario ya existe. Intenta con otro nombre."
        else:
            cursor.execute("INSERT INTO users (usuario, password) VALUES (%s, %s)", (usuario, password))
            conn.commit()
            conn.close()
            return redirect('/login')

        conn.close()
    return render_template('registro.html', error=error)

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
    cursor.execute("SELECT id, nombre, telefono, correo FROM contactos WHERE usuario_id = %s", (session['user_id'],))
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
        cursor.execute("INSERT INTO contactos (nombre, telefono, correo, usuario_id) VALUES (%s, %s, %s, %s)",
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

        cursor.execute("UPDATE contactos SET nombre = %s, telefono = %s, correo = %s WHERE id = %s AND usuario_id = %s",
                       (nombre, telefono, correo, id, session['user_id']))
        conn.commit()
        conn.close()
        return redirect('/contactos')

    cursor.execute("SELECT nombre, telefono, correo FROM contactos WHERE id = %s AND usuario_id = %s", (id, session['user_id']))
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
    cursor.execute("DELETE FROM contactos WHERE id = %s AND usuario_id = %s", (id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/contactos')

# --- EXPORTAR CONTACTOS ---
@app.route('/contactos/exportar', methods=['GET'])
def exportar_contactos():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, telefono, correo FROM contactos WHERE usuario_id = %s", (session['user_id'],))
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
