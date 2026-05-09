import sqlite3
import json
import xml.etree.cElementTree as ET

#tenemos la configuracion mas la coneccion
def conectamos_bd():
    #Se crea si no existe y se conecta
    conn=sqlite3.connect('Hospital.db')
    return conn
def inicializamos_tablas():
    conn=conectamos_bd()
    cursor=conn.cursor()
    
    #Ahora las tablas de personal(Medicos,enfermeros,pacientes,Administrativos)
    cursor.execute('''CREATE TABLE IF NOT EXISTS personal(
                   id INTEGER PRIMARY KEY,
                   nombre TEXT,
                   tipo TEXT,
                   planta INTEGER,
                   depende_medico INTEGER
                   )''')
    #ahora la tabla de pacientes
    cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes(
                   dni TEXT PRIMARY KEY,
                   nombre TEXT,
                   apellido TEXT,
                   tarjeta_sanitaria TEXT
                   )''')
    #ahora la tabla de visitas
    cursor.execute('''CREATE TABLE IF NOT EXISTS visitas(
                   id INTEGER  PRIMARY KEY AUTOINCREMENT,
                   fecha TEXT,
                   dni_paciente TEXT,
                   id_medico INTEGER,
                   diagnostico TEXT
                   )''')
    conn.commit()
    conn.close()
    #Anexo 2. Login y seguridad.
def guardar_log(usuario, password):
    #Guarda los datos en un archivo separado en formato simple.
    #Se podria  aplicar un "hash" para seguridad extra.
    with open ("config_log.txt", "w") as f:
        f.write(f"{usuario},{password}")
            
def verif_log(usuario, password):
    autenticado=False
    #abrimos el archivo para leer
    with open("config_log.txt","r") as  f:
        contenido=f.read()
        if "," in contenido:
           datos=contenido.split(",")
           if datos[0]==usuario and datos[1]==password:
               autenticado=True
    return autenticado                

#Anexo 3. Mantenimiento
def alta_pers(nombre, tipo, planta, medico_asig=None):
    conn=conectamos_bd()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO personal (nombre, tipo, planta, depende_medico) VALUES (?,?,?,?)",("nombre, tipo, planta, medico_asig)"))
    conn.commit()
    conn.close()
    
def alta_paciente(dni, nombre, apellido, tarjeta_sanitaria):              
    conn=conectamos_bd()
    cursor=conn.cursor()
    cursor.execute("INSERT INTO pacientes VALUES (?,?,?,?)", (dni, nombre, apellido, tarjeta_sanitaria))
    conn.commit()
    conn.close()
    
#Anexo 4. Consultas e informes
def informe_personal_planta(planta):
    conn=conectamos_bd()
    cursor=conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM personal WHERE planta =?", (planta,))
    total=cursor.fetchone()[0]
    print(f"En la planta: {planta} trabajan: {total} personas.")
    conn.close()
    
#Anexo 5. Exportacion XML
def exportar_visitas_xml(fecha_inici, fecha_fin):
    conn=conectamos_bd()
    cursor=conn.cursor()
    #Consultamos con Join para traer datos de pacientes y medicos
    cursor.execute('''SELECT v.id, v.fecha, p.nombre, p.dni, m.nombre FROM visitas v JOIN pacientes p ON v.dni_paciente=p.dni JOIN personal m ON v.id_medico=m.id WHERE v.fecha BETWEEN ? AND ?''', (fecha_inici, fecha_fin))
    visitas=cursor.fetchall()
    root=ET.Element("Hospital")
    #Iteracion sobre los resultados.
    for v in visitas:
        v_element=ET.SubElement(root, "Visitas", id=str(v[0]))
        ET.SubElement(v_element, "Fecha").text=v[1]
        ET.SubElement(v_element, "Paciente").text=v[2]
        ET.SubElement(v_element, "DNI").text=v[3]
        ET.SubElement(v_element, "Medico").text=v[4]
        
    #Guardar identado
    tree=ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write("exportacion_visitas.xml", encoding="utf-8", xml_declaration=True)
    conn.close()
    
#Programa principal
def menu():
   inicializamos_tablas()
   #simulacion del primer inicio para crear el archivo login
   guardar_log("adm","Passw0rd")
   print("Hospital")
   usuario=input("Usuario: ")
   password=input("Password: ")
   if verif_log(usuario, password):
      opcion=" "
      #bucle principal
      while opcion != "4":
        print("\n1.Alta personal\n2.Informe Planta\n3.Exportar\n4.Salir.")
        opcion=input("Seleccione: ")
        
        if opcion =="1":
           nom=input("Nombre: ")
           tipo=input ("Tipo: Medico/Enfermero. ")
           planta=input("Planta: ")
           alta_pers(nom, tipo, int(planta))
        elif opcion == "2":
           p=input("Numero de planta: ")
           informe_personal_planta(int(p))
        elif opcion == "3":
           f1=input("Fecha inicio(YYYY-MM-DD): ")
           f2= input("Fecha fin(YYYY-MM-DD): ")
           exportar_visitas_xml(f1, f2)
           print("Archivo 'exportacion_visitas.xml' generado")
#Probamos si funciona
if __name__=="__main__":
   inicializamos_tablas()
   guardar_log("adm", "Passw0rd")
   print("Base de datos y login configurados.")
   menu()
    
    
    
            
            
    
    
    
    