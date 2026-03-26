from flask import Flask, render_template,url_for,request,flash,redirect, session
from database import conectar


#crear la app del proyecto
apps = Flask(__name__)
apps.secret_key = "123456"

#crear ruta de ingresar y mostrar el formulario
@apps.route('/')
def login():

    return render_template("ingresar.html")

#crear ruta de ingresar
@apps.route('/',methods=["POST"])
def login_form():
    #crea variables de phyton user, contraseña para recibir del formulario
    user = request.form['txtusuario']
    password = request.form['txtcontrasena']

    #llamar a la bd

    con = conectar()
    cursor = con.cursor()

    sql = "SELECT * FROM usuarios WHERE usuario=%s and PASSWORD=%s"
    cursor.execute(sql,(user,password))

    #resultado de la consulta
    user = cursor.fetchone()

    if user:

        #guarda las variables de session
        session['usuario'] = user[1]
        session['rol'] = user[3]#columna del rol

        #if rol == rol:

        if user[3] =="administrador":
                return render_template("index.html")
        else:
                return "Bienvenido empleado"
    else:
        flash("usuario y contraseña incorrecto","danger")
        return redirect(url_for('login_form'))
#validar sesiom en la pagina inicial
@apps.route('/inicio')
def inicio():
     
     if 'usuario' not in session:
          return redirect(url_for('login_form'))
     else:
          render_template('index.html')

#cerrar la sesion
@apps.route('/salir')
def salir():
     session.clear()
     return redirect (url_for('login_form'))



if __name__ == '__main__':
    apps.run(debug=True)
