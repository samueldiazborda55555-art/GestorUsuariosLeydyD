from flask import Flask ,render_template,url_for,request,flash, redirect,session
from database import conectar 

#crear la app del proyecto
apps =  Flask(__name__)
apps.secret_key = "12345"

#crear ruta de ingresar y mostrar el formulario
@apps.route('/')
def login():
    return render_template("login.html")

#Crear ruta de ingresar
@apps.route('/',methods=["POST"])
def login_form():

    user = request.form['txtusuario']
    password  = request.form['txtcontrasena']

    con = conectar()
    cursor = con.cursor()
    sql = "SELECT  *  FROM usuarios WHERE usuario=%s AND PASSWORD=%s"
    cursor.execute(sql,(user,password))

    user = cursor.fetchone()

    if user:
        session['usuario'] = user[1]
        session['rol'] = user [3]

        if user[3] == "administrador":
                return redirect(url_for('inicio'))
        else:
                return "Bienvenido empleado"
    else: 
        flash("Usuario y contraseña incorrecto", "danger")
        return redirect(url_for('login_form'))
    

#validad sesion en la pagina principal
@apps.route('/inicio')
def inicio():
         
    if 'usuario' not in session:
        return redirect(url_for('login_form'))
         
    con = conectar()
    cursor = con.cursor()

    sql = "SELECT * FROM usuarios"
    cursor.execute(sql)
    lista = cursor.fetchall()

    sql1 = "SELECT * FROM empleados"
    cursor.execute(sql1)
    empleados = cursor.fetchall()
       
    return render_template('index.html', user=lista, empleados=empleados)


#guardar usuario
@apps.route('/guardar_usuario', methods=["POST"])
def guardar_usuario():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuario = request.form["txtusuario"]
    password = request.form["txtcontrasena"]
    rolusu = request.form["txtrol"]
    documento = request.form["txtdocumento"]

    con = conectar()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE usuario=%s", (usuario,))
    existe = cursor.fetchone()

    if existe:
        flash("El usuario ya existe")
        return redirect(url_for('inicio'))

    sql = """INSERT INTO usuarios(usuario, PASSWORD, rol, documentoEmple) 
             VALUES (%s, %s, %s, %s)"""

    cursor.execute(sql, (usuario, password, rolusu, documento))
    con.commit()

    cursor.close()
    con.close()

    flash("Usuario guardado correctamente")
    return redirect(url_for('inicio'))


#vista formulario registrar empleado
@apps.route('/forempleado')
def forempleado():
    return render_template("registroempleados.html")


#registrar empleado 
@apps.route('/guardar_empleado', methods=["POST"])
def guardar_empleado():

    if 'usuario' not in session:
        return redirect(url_for('login'))

    nombre = request.form["txtnombre"]
    apellido = request.form["txtapellido"]
    documento = request.form["txtdocumento"]
    cargo = request.form["txtcargo"]
    departamento = request.form["txtdepartamento"]
    horasExtras = request.form["txthorasextra"]
    bonificacion = request.form["txtbonificacion"]

    # CALCULAR SALARIO
    salariobru, salud, pension, salario_neto = calcular_salario(cargo, horasExtras, bonificacion)

    con = conectar()
    cursor = con.cursor()

    #validar si ya existe 
    cursor.execute("SELECT * FROM empleados WHERE documentoEmple=%s", (documento,))
    existe = cursor.fetchone()

    if existe:
        flash("El empleado ya existe")
        return redirect(url_for('inicio'))

    # INSERT CORRECTO
    sql = """INSERT INTO empleados(
        nombreEmple, apellidoEmple, documentoEmple, cargo, id_dep, 
        horasExtras, bonificacion, salarioB, salud, pension, salario_neto
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    cursor.execute(sql, (
        nombre,
        apellido,
        documento,
        cargo,
        departamento,
        horasExtras,
        bonificacion,
        salariobru,
        salud,
        pension,
        salario_neto
    ))

    con.commit()

    cursor.close()
    con.close()

    flash("Empleado guardado correctamente")
    return redirect(url_for('inicio'))


# SALARIOS EMPLEADOS
def calcular_salario(cargo, horas_extra, bonificacion):

    horas_extra = int(horas_extra or 0)
    bonificacion = float(bonificacion or 0)

    if cargo.lower() == "gerente":
        salbase = 5000000
    elif cargo.lower() == "administrador":
        salbase = 3500000
    elif cargo.lower() == "contador":
        salbase = 2800000
    else:
        salbase = 1800000

    totalextras = horas_extra * 3000

    salariobru = salbase + totalextras + bonificacion
    salud = salariobru * 0.04
    pension = salariobru * 0.04
    salarioneto = salariobru - salud - pension

    return salariobru, salud, pension, salarioneto


#ELIMINAR EMPLEADO 
@apps.route('/eliminaremple/<int:id>')
def eliminar_empleado(id):
    if 'usuario' not in session:
        return redirect(url_for('login_form'))
    
    con = conectar()
    cursor = con.cursor()

    cursor.execute("DELETE FROM empleados WHERE id=%s", (id,))
    con.commit()

    cursor.close()
    con.close()

    return redirect(url_for('inicio'))


#cerrar la sesion
@apps.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('login_form'))


#eliminar usuarios
@apps.route('/eliminar/<int:id>')
def eliminarusu(id):
    if 'usuario' not in session:
        return redirect(url_for('login_form'))
    
    con = conectar()
    cursor = con.cursor()

    sql = "SELECT rol FROM usuarios WHERE id_usuario=%s"
    cursor.execute(sql,(id,))

    usuario = cursor.fetchone()

    if usuario:
        rol = usuario[0]

        if rol == "administrador":
            flash("No se puede eliminar el administrador")
        else:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s",(id,))
            con.commit()
            flash("Empleado eliminado")
    else:
        flash("Usuario no encontrado")

    cursor.close()
    con.close()

    return redirect(url_for('inicio'))


#Editar usuarios
@apps.route('/editarusu/<int:id>')
def editarusu(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    con = conectar()
    cursor = con.cursor()

    sql1 = "SELECT * FROM usuarios WHERE id_usuario=%s"
    cursor.execute(sql1, (id,))
    usuario = cursor.fetchone()

    cursor.close()
    con.close()

    return render_template("editarusuario.html", usu=usuario)

#actualizar la informacion del formulario
@apps.route('/actualizar', methods=["POST"])
def actualizar_usuarios():

    id = request.form["id"]
    usuario = request.form["txtusuario"]
    password = request.form["txtcontrasena"]

    con = conectar()
    cursor = con.cursor()

    sqla = "UPDATE usuarios SET usuario=%s, PASSWORD=%s WHERE id_usuario=%s"
    cursor.execute(sqla, (usuario, password, id))
    con.commit()

    cursor.close()
    con.close()

    print("usuario actualizado")
    return redirect(url_for('inicio'))


#Editar empleados
@apps.route('/editarempleado/<int:id>')
def editarempleado(id):

    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    con = conectar()
    cursor = con.cursor()

    sql2 = "SELECT * FROM empleados WHERE id=%s"
    cursor.execute(sql2, (id,))
    empleado = cursor.fetchone()

    cursor.close()
    con.close()

    return render_template("editarempleado.html", emple=empleado)


    #actualizar la informacion del empleado
@apps.route('/editarempleado', methods=["POST"])
def actualizar_empleado():

    id = request.form["id"]
    nombre = request.form["txtnombre"]
    apellido = request.form["txtapellido"]
    cargo = request.form["txtcargo"]
    horas_extras = request.form["txthorasextras"]
    bonificacion = request.form["txtbonificacion"]
    departamento = request.form["txtdepartamento"]

    con = conectar()
    cursor = con.cursor()

    sqle = "UPDATE empleados SET nombreEmple=%s, apellidoEmple=%s, cargo=%s, horasExtras=%s, bonificacion=%s, id_dep=%s WHERE id=%s"
    cursor.execute(sqle, (nombre, apellido, cargo, horas_extras, bonificacion, departamento, id))
    con.commit()

    cursor.close()
    con.close()

    print("empleado actualizado")

    return redirect(url_for('inicio'))

    redirect(url_for('inicio'))

if __name__ == '__main__':
    apps.run(debug=True)