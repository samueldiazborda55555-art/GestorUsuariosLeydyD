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

#crea variable de python user, contraseña para recibir del formulario 
    user = request.form['txtusuario']
    password  = request.form['txtcontrasena']

    #llamar a la bd

    con = conectar()
    cursor = con.cursor()
    sql = "SELECT  *  FROM usuarios WHERE usuario=%s AND PASSWORD=%s"
    cursor.execute(sql,(user,password))


    #resultado de la consulta
    user = cursor.fetchone()

    if user:
        #guardar las variables de sesion 
        session['usuario'] = user[1]
        session['rol'] = user [3]

        #rol = user[3] # Numero de columna del rol

        #if rol == rol:

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

    # validar si ya existe
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

#vista formulario registrar empeado
@apps.route('/foremmpleado')
def forempleado():
    return render_template("registroempleados.html")

#registrar empleado 

@apps.route('/guardar_empleado', methods=["POST"])
def guardar_empleado():

    nombre = request.form["txtnombre"]
    apellido = request.form["txtapellido"]
    documento = request.form["txtdocumento"]
    cargo = request.form["txtcargo"]
    departamento = request.form["txtdepartamento"]
    horasExtras = int(request.form["txthorasextra"])
    bonificacion = float(request.form["txtbonificacion"])

    def salario_base():

        if cargo == "gerente":
            return 5000000
        elif cargo == "administrador":
            return 3500000
        elif cargo == "docente":
            return 2800000
        else:
            return 1800000


    salbase = salario_base()
    totalextras = horasExtras * 3000
    salariobru = salbase + totalextras + bonificacion
    salud = salariobru * 0.04
    pension = salariobru * 0.04
    salarioneto = salariobru - salud - pension
    salariobru, salud, pension, salarioneto

    con = conectar()
    cursor = con.cursor()
    sqldep = "SELECT id_area FROM departamentos WHERE nombre_area = %s"
    cursor.execute(sqldep,(departamento,))

    resultado = cursor.fetchone()

    if resultado: 
        nombredep = resultado[0]
        sql = """INSERT INTO empleados
        (documentoEmple,nombreEmple,apellidoEmple,cargo,salarioB,horasExtras,bonificacion,salud,pension,salario_neto,id_dep)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        datos = (documento, nombre, apellido, cargo, salariobru, horasExtras, bonificacion, salud, pension, salarioneto,nombredep)
        cursor.execute(sql, datos)
        con.commit()
        print("\nEmpleado guardado en la base de datos") 
    else:
        
        print ("\n Departamento no existe")
    return redirect(url_for('inicio'))
# eliminar el empleado
@apps.route('/eliminarempleado/<int:id>')
def eliminar_empleado(id):
   
    if 'usuario' not in session:
        return redirect(url_for('login_form'))
    
    con = conectar()
    cursor = con.cursor()

    
    cursor.execute("DELETE FROM empleados WHERE id=%s",(id,))
    con.commit()
    print("Empleado eliminado")
   

    cursor.close()
    con.close()

    return redirect(url_for('inicio'))

    


#cerrar la sesion
@apps.route('/salir')
def salir():
      session.clear()
      return redirect(url_for('login_form'))

#crear una ruta para eliminar los usuarios tipo empleado
@apps.route('/eliminar/<int:id>')
def eliminarusu(id):
    if 'usuario' not in session:
        return redirect(url_for('login_form'))
    
    con = conectar()
    cursor = con.cursor()

    #buscar el usuario

    sql = "SELECT rol FROM usuarios WHERE id_usuario=%s"
    cursor.execute(sql,(id,))

    usuario = cursor.fetchone()

    #validar el rol usuario
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


    
    
if __name__ == '__main__':
    apps.run(debug=True)