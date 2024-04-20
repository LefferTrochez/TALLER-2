#!/usr/bin/env python3
import rclpy # LIBRERIA PARA UTILIZAR PYTHON (ROS CLIENT LIBRARY PYTHON)
import pygame # BIBLIOTECA PARA APLICACIONES MULTIMEDIA
from geometry_msgs.msg import Twist # ES EL TIPO DE MENSAJE 
from tkinter import filedialog # PARA LA SELECCIÓN DE ARCHIVOS Y DIRECTORIOS
import os # INTERFACE PARA INTERACTUAR CON EL SISTEMA OPERATIVO SUBYACENTE
from std_msgs.msg import Float32MultiArray, MultiArrayDimension

from example_interfaces.srv import SetBool # TIPO DE MENSAJE PARA EL SERVICIO

pygame.init() # INICILIZACIÓN DEL CÓDIGO
pantalla = pygame.display.set_mode((600, 650)) # CREACIÓN DE LA PANTALLA Y TAMAÑO DE LA MISMA
robot = (0, 0, 0) # COLOR DEL ROBOT - NEGRO - (R G B)
pantalla.fill((255, 255, 255)) # COLOR DEL FONDO - BLANCO - (R G B)
# VARIABLES GLOBALES A UTILIZAR 
global vel_lineal
global vel_angular
global x
global y
global xx
global yy
global primero
global velocidad_lineal, velocidad_angular
global nombre_archivo
global inicio
global escala
escala=0.05
last_written_velocity = (0, 0) 

def evento(i, forma_boton, funcion_asiganada = None): # FUNCIÓN PARA DETECTAR EL MOUSE
    if i.type == pygame.MOUSEBUTTONDOWN and i.button == 1: # DETECCIÓN DEL MOUSE
        if forma_boton.collidepoint(i.pos): # HABILITAR EL BOTÓN
            if funcion_asiganada: 
                funcion_asiganada() # CORRER LA FUNCIÓN ASIGNADA

def boton(pantalla, posicion_y_boton, texto, function = None): # FUNCIÓN PARA CREAR EL BOTÓN
    posicion_x_boton = 430 # POSICIÓN X DEL BOTON DENTRO DE LA PANTALLA
    ancho_boton = 160 # DIMENSIÓN ANCHO DEL BOTÓN
    alto_boton = 30 # DIMENSIÓN ALTO DEL BOTÓN
    parametro_boton = pygame.Surface((ancho_boton, alto_boton)) # DEFINE EL ANCHO Y ALTO DEL BOTÓN
    parametro_boton.fill((0, 0, 0)) # DEFINE EL COLOR DEL BOTÓN - NEGRO - (R G B)
    fuente_boton = pygame.font.SysFont("Aharoni", 24) # TIPO DE FUENTE DEL BOTÓN Y TAMAÑO DE LA LETRA
    texto_boton = fuente_boton.render(texto, True, (255, 255, 255)) # CREAR EL TEXTO DEL BOTÓN EN COLOR BLANCO - (R G B)
    parametro_boton.blit(texto_boton, ((1/2)*(ancho_boton - texto_boton.get_width()), (1/2)*(alto_boton - texto_boton.get_height()))) # PONER TEXTO EN LA SUPERFICIE DEL BOTÓN CENTRADO
    pantalla.blit(parametro_boton, (posicion_x_boton, posicion_y_boton)) # CONSTRUIR EL BOTÓN EN LA PANTALLA
    forma_boton = pygame.Rect(posicion_x_boton, posicion_y_boton, ancho_boton, alto_boton) # FORMA RECTÁNGULAR DEL BOTÓN INSERTADO EN LA PANTALLA
    return parametro_boton, forma_boton # RETORNOS DE LA FUNCIÓN

def boton_decision(pantalla, posicion_x_boton, texto, function = None): # FUNCIÓN PARA CREAR EL BOTÓN
    posicion_y_boton = 325 # POSICIÓN Y DEL BOTON DENTRO DE LA PANTALLA
    ancho_boton = 110 # DIMENSIÓN ANCHO DEL BOTÓN
    alto_boton = 30 # DIMENSIÓN ALTO DEL BOTÓNs
    parametro_boton = pygame.Surface((ancho_boton, alto_boton)) # DEFINE EL ANCHO Y ALTO DEL BOTÓN
    parametro_boton.fill((0, 0, 0)) # DEFINE EL COLOR DEL BOTÓN - NEGRO - (R G B)
    fuente_boton = pygame.font.SysFont("Aharoni", 24) # TIPO DE FUENTE DEL BOTÓN Y TAMAÑO DE LA LETRA
    texto_boton = fuente_boton.render(texto, True, (255, 255, 255)) # CREAR EL TEXTO DEL BOTÓN EN COLOR BLANCO - (R G B)
    parametro_boton.blit(texto_boton, ((1/2)*(ancho_boton - texto_boton.get_width()), (1/2)*(alto_boton - texto_boton.get_height()))) # PONER TEXTO EN LA SUPERFICIE DEL BOTÓN CENTRADO
    pantalla.blit(parametro_boton, (posicion_x_boton, posicion_y_boton)) # CONSTRUIR EL BOTÓN EN LA PANTALLA
    forma_boton = pygame.Rect(posicion_x_boton, posicion_y_boton, ancho_boton, alto_boton) # FORMA RECTÁNGULAR DEL BOTÓN INSERTADO EN LA PANTALLA
    return parametro_boton, forma_boton # RETORNOS DE LA FUNCIÓN

def dibujar_ejes_con_numeros(pantalla, tamano_recuadro, color, grosor, escala_px_por_unidad):
    # Calcular el punto de origen para centrar el recuadro justo por encima del borde inferior de la pantalla
    origen_x = (pantalla.get_width() - tamano_recuadro[0]) // 2
    origen_y = pantalla.get_height() - tamano_recuadro[1] - 50  # 50 píxeles por encima del borde inferior
    
    # Define la fuente para los números
    fuente = pygame.font.SysFont("Arial", 20)
    
    # Dibujar la grilla punteada dentro del recuadro
    distancia_entre_puntos = escala_px_por_unidad // 5  # Distancia entre los puntos de la grilla
    for i in range(0, tamano_recuadro[0] + 1, distancia_entre_puntos):
        for j in range(0, tamano_recuadro[1] + 1, distancia_entre_puntos):
            if (i % escala_px_por_unidad) or (j % escala_px_por_unidad):  # No dibujar sobre las líneas de ejes
                pygame.draw.circle(pantalla, color, (origen_x + i, origen_y + j), 1)
    
    # Dibujar el borde del recuadro
    pygame.draw.rect(pantalla, color, (origen_x, origen_y, tamano_recuadro[0], tamano_recuadro[1]), grosor)
    
    # Dibujar las marcas y números en los ejes
    for i in range(-tamano_recuadro[0] // 2 // escala_px_por_unidad, tamano_recuadro[0] // 2 // escala_px_por_unidad + 1):
        num = i * escala_px_por_unidad / 100  # Convertir la posición a unidades numéricas
        x = origen_x + (i * escala_px_por_unidad) + tamano_recuadro[0] // 2
        y = origen_y + (i * escala_px_por_unidad) + tamano_recuadro[1] // 2

        if i != 0:  # No dibujar el cero en el origen para los ejes vertical y horizontal
            # Dibujar números en el eje horizontal inferior
            texto = fuente.render(str(num), True, color)
            pantalla.blit(texto, (x - texto.get_width() // 2, origen_y + tamano_recuadro[1] + 5))

            # Dibujar números en el eje vertical izquierdo
            texto = fuente.render(str(-num), True, color)
            pantalla.blit(texto, (origen_x - texto.get_width() - 15, y - texto.get_height() // 2))

    # Dibujar el cero solo en el origen del eje vertical
    texto_cero = fuente.render("0", True, color)
    pantalla.blit(texto_cero, (origen_x - texto_cero.get_width() - 15, origen_y + tamano_recuadro[1] // 2 - texto_cero.get_height() // 2))
primero = True
def callback(msg): # FUNCIÓN PARA GRAFICAR EN TIEMPO REALuuuuuuu
    global escala
    TurtleBotInterfaceNode = rclpy.create_node('turtle_bot_interface') # CREACION DEL NODO
    TurtleBotInterfaceNode.create_timer(0.0524, callback) # TIEMPO DE MUESTREO
    if inicio: # SI EXISTE UN SERVICIO
        xx = (msg.data[0])*escala
        yy = (msg.data[1])*escala
        print("if inicio,   xx: " + str(round(xx,3)) + " ,   yy: " + str(round(yy,3)))
    #if len(str(xx)) > 6 and len(str(yy)) > 6: # CLASIFICA VALORES DE POSICION
        # Define el origen de los ejes (esquina inferior izquierda del recuadro)



        pygame.draw.circle(pantalla, robot, (xx+pantalla.get_width()/2, -yy+pantalla.get_height()/2), 4) # DIBUJA EL CIRCULO EN LA PANTALLA EN LA COORDENADA DADA
        dibujar_ejes_con_numeros(pantalla, (500, 500), (0, 0, 0), 1, 100)
        titulo = pygame.font.SysFont("Arial", 26) # TIPO DE FUENTE DEL TÍTULO Y TAMAÑO DE LA LETRA
        texto_titulo = titulo.render("Este fue el recorrido TurtleBot", True, (0, 0, 0)) # TÍTULO DE LA GRÁFICA
        posicion_x_titulo = 20 # POSICIÓN X DEL TÍTULO DENTRO DE LA PANTALLA
        posicion_y_titulo = 25 # POSICIÓN Y DEL TÍTULO DENTRO DE LA PANTALLA
        pantalla.blit(texto_titulo, (posicion_x_titulo, posicion_y_titulo)) # PONER EL TEXTO DEL TÍTULO EN LA PANTALLA
        pygame.display.update()  # ACTUALIZAR
        posicion_y_boton_imagen = 10 # POSICIÓN Y DEL BOTON DENTRO DE LA PANTALLA
        parametro_boton, Boton_guardar_imagen = boton(pantalla, posicion_y_boton_imagen, "Guardar imagen") # CREAR EL BOTÓN "GUARDAR"
        for i in pygame.event.get(): # ENTRAR A LA FUNCIÓN EVENTO
            evento(i, Boton_guardar_imagen, funcion_asiganada = lambda:GuardarImagen()) # SI SE OPRIME EL BOTÓN "GUARDAR" CORRER LA FUNCIÓN "GUARDAR ARCHIVO"
            pygame.display.update() # ACTUALIZAR
    else:
        if primero: # PAR PREGUNTAR SI SE QUIERE GUARDAR EL ARCHIVO
            origen_ejes = (100, pantalla.get_height() - 1100) # Ajusta según la posición deseada
        # Dibuja los ejes de 50 unidades, cada unidad representa 10 cm, y cada unidad es de 20 píxeles
            preguntar = pygame.font.SysFont("Arial", 30) 
            texto_preguntar = preguntar.render("¿Quieres guardar el recorrido del TurtleBot?", True, (0, 0, 0)) 
            posicion_x_preguntar = 12 # POSICIÓN X DEL TÍTULO DENTRO DE LA PANTALLA
            posicion_y_preguntar = 250 # POSICIÓN Y DEL TÍTULO DENTRO DE LA PANTALLA
            pantalla.blit(texto_preguntar, (posicion_x_preguntar, posicion_y_preguntar)) # PONER EL TEXTO DEL TÍTULO EN LA PANTALLA
            pygame.display.update()  # ACTUALIZAR
            posicion_x_boton_no = 350 # POSICION EN X DEL BOTON NO
            posicion_x_boton_si = 150 # POSICION EN X DEL BOTON SI
            parametro_boton, Boton_si = boton_decision(pantalla,posicion_x_boton_si , "Si quiero") # BOTON DE SI
            parametro_boton, Boton_no = boton_decision(pantalla, posicion_x_boton_no ,"No quiero") # BOTON DE NO
            for i in pygame.event.get(): # ENTRAR A LA FUNCIÓN EVENTO
                evento(i, Boton_si, funcion_asiganada = lambda:SiQuiero()) 
                evento(i, Boton_no, funcion_asiganada = lambda:NoQuiero()) 
        else:
                if escribir: # SI SE QUIERE GUARDAR EL RECORRIDO
                    global velocidad_angular, velocidad_lineal
                    pygame.display.update() # ACTUALI

                    vel_lineal=msg.data[2]
                    vel_angular=msg.data[3]
                    print("if escribir,    vel_lineal: " +str(round(vel_lineal,3)) + " ,    vel_ang: " +str(round(vel_angular,3)))
                   
                
                    EscribirArchivoTexto(vel_lineal, -vel_angular, "SinNombre.txt")
                    x=msg.data[0]*escala
                    y=msg.data[1]*escala
                    print("if escribir,   xx: " + str(round(x,3)) + " ,   yy: " + str(round(y,3)))
                   # if len(str(x)) > 6 and len(str(y)) > 6: # CLASIFICA VALOR DE POSICION PARA GRAFICAR

                    origen_ejes = (100, pantalla.get_height() - 1100) # Ajusta según la posición deseada
        # Dibuja los ejes de 50 unidades, cada unidad representa 10 cm, y cada unidad es de 20 píxeles
                    dibujar_ejes_con_numeros(pantalla, (500, 500), (0, 0, 0), 1, 100)

                    pygame.draw.circle(pantalla, robot, (x+pantalla.get_width()/2, -y+pantalla.get_height()/2), 4) # DIBUJA EL CIRCULO EN LA PANTALLA EN LA COORDENADA DADA
                    titulo = pygame.font.SysFont("Arial", 26) # TIPO DE FUENTE DEL TÍTULO Y TAMAÑO DE LA LETRA
                    texto_titulo = titulo.render("Gráfica de Posición TurtleBot", True, (0, 0, 0)) # TÍTULO DE LA  GRÁFICA
                    posicion_x_titulo = 20 # POSICIÓN X DEL TÍTULO DENTRO DE LA PANTALLA
                    posicion_y_titulo = 25 # POSICIÓN Y DEL TÍTULO DENTRO DE LA PANTALLA
                    pantalla.blit(texto_titulo, (posicion_x_titulo, posicion_y_titulo)) # PONER EL TEXTO DEL TÍTULO EN LA PANTALLA
                    velocidad_lineal = (msg.data[2])
                    velocidad_angular = (msg.data[3])
                    pygame.display.update()  # ACTUALIZAR
                    posicion_y_boton_imagen = 10 # POSICIÓN Y DEL BOTON DENTRO DE LA PANTALLA
                    parametro_boton, Boton_guardar_imagen = boton(pantalla, posicion_y_boton_imagen, "Guardar imagenn") # CREAR EL BOTÓN "GUARDAR"
                    posicion_y_boton_recorrido = 45 # POSICIÓN Y DEL BOTON DENTRO DE LA PANTALLA
                    parametro_boton, Boton_guardar_recorrido = boton(pantalla, posicion_y_boton_recorrido, "Guardar recorrido") # CREAR EL BOTÓN "GUARDAR"
                    for i in pygame.event.get(): # ENTRAR A LA FUNCIÓN EVENTO
                        evento(i, Boton_guardar_imagen, funcion_asiganada = lambda:GuardarImagen()) # SI SE OPRIME EL BOTÓN "GUARDAR" CORRER LA FUNCIÓN "GUARDAR ARCHIVO"
                        evento(i, Boton_guardar_recorrido, funcion_asiganada = lambda:GuardarRecorrido()) 
                        pygame.display.update() # ACTUALIZAR
                else: 
                    x=msg.data[0]*escala
                    y=msg.data[1]*escala# COORDENADA DEL ROBOT EN Y ESCALA POR 100
                    print("else escribir,   x: " + str(round(x,3)) + " ,   yy: " + str(round(y,3)))
                  #  if len(str(x)) > 6 and len(str(y)) > 6: # CLASIFICA VALOR DE POSICION PARA GRAFICAR
                    pygame.draw.circle(pantalla, robot, (x+pantalla.get_width()/2, -y+pantalla.get_height()/2), 4) # DIBUJA EL CIRCULO EN LA PANTALLA EN LA COORDENADA DADA
                    dibujar_ejes_con_numeros(pantalla, (500, 500), (0, 0, 0), 1, 100)
                    titulo = pygame.font.SysFont("Arial", 26) # TIPO DE FUENTE DEL TÍTULO Y TAMAÑO DE LA LETRA
                    texto_titulo = titulo.render("Gráfica de Posición TurtleBot", True, (0, 0, 0)) # TÍTULO DE LA  GRÁFICA
                    posicion_x_titulo = 20 # POSICIÓN X DEL TÍTULO DENTRO DE LA PANTALLA
                    posicion_y_titulo = 25 # POSICIÓN Y DEL TÍTULO DENTRO DE LA PANTALLA
                    pantalla.blit(texto_titulo, (posicion_x_titulo, posicion_y_titulo)) # PONER EL TEXTO DEL TÍTULO EN LA PANTALLA
                    pygame.display.update()  # ACTUALIZAR
                    posicion_y_boton_imagen = 10 # POSICIÓN Y DEL BOTON DENTRO DE LA PANTALLA
                    parametro_boton, Boton_guardar_imagen = boton(pantalla, posicion_y_boton_imagen, "Guardar imagen") # CREAR EL BOTÓN "GUARDAR"
                    for i in pygame.event.get(): # ENTRAR A LA FUNCIÓN EVENTO
                        evento(i, Boton_guardar_imagen, funcion_asiganada = lambda:GuardarImagen()) # SI SE OPRIME EL BOTÓN "GUARDAR" CORRER LA FUNCIÓN "GUARDAR ARCHIVO"
                        pygame.display.update() # ACTUALIZAR


def EscribirArchivoTexto(vel_lineal, vel_angular, nombre_txt):
    if vel_lineal != 0.0 or vel_angular!= 0.0:
        with open(nombre_txt, 'a') as archivo:
            archivo.write(f"{vel_lineal}, {vel_angular}\n")
            print(vel_lineal,vel_angular)
            
      
            

def SiQuiero(): # FUNCION SI SE QUIERE GUARDAR EL RECORRIDO
    global escribir, primero
    escribir = True # HABILITA LA OPCION DE ESCRIBIR
    pantalla.fill((255, 255, 255)) # PANTALLA EN BLANCO
    pygame.display.update() # ACTUALIZAR LA PANTALLA
    primero = False

def NoQuiero(): # FUNCION SI NO SE QUIERE GUARDAR EL RECORRIDO
    global escribir, primero
    escribir = False # NO GUARDAR RECORRIDO
    pantalla.fill((255, 255, 255))
    pygame.display.update() # ACTUALIZAR
    primero = False
        
def GuardarImagen(): # FUNCIÓN PARA GUARDAR LA IMAGEN DEL RECORRIDO
    imagen = pygame.Surface(pantalla.get_size()) # TOMA EL TAMAÑO DE LA PANTALLA
    imagen.blit(pantalla, (0, 0)) # CAPTURA LA IMAGEN
    pygame.image.save(imagen, 'SinNombre.png') # GUARDA LA IMAGEN CON EL NOMBRE POR DEFECTO "SINNOMBRE" POR SI NO SE LE DA UN NOMBRE A LA IMAGEN
    archivo = filedialog.asksaveasfilename(defaultextension='.png') # PREGUNTAR AL USUARIO POR EL NOMBRE DE LA GRÁFICA
    if archivo: # ENTRA AL ARCHIVO 
        with open('SinNombre.png', 'rb') as SinNombre: # ABRIR EL ARCHIVO EN MODO LECTURA BINARIA
            with open(archivo, 'wb') as ConNombre: # ABRIR EL ARCHIVO EN MODO ESCRITURA BINARIA
                ConNombre.write(SinNombre.read()) # ESCRIBIR EN EL ARCHIVO EL CONTENIDO DE LA IMAGEN "SINNOMBRE"
                os.remove('SinNombre.png') # ELIMINA LA IMAGEN "SINNOMBRE" Y DEJA LA IMAGEN ARCHIVO 

def GuardarRecorrido(): # FUNCIÓN PARA GUARDAR LA IMAGEN DEL RECORRIDO
    with open("SinNombre.txt", 'a') as archivo:
            archivo.write(f"{0}, {0}\n")
    archivo = filedialog.asksaveasfilename(defaultextension='.txt') # PREGUNTAR AL USUARIO POR EL NOMBRE DE LA GRÁFICA
    Nombre_predetermiando = "SinNombre.txt"
    if archivo: # ENTRA AL ARCHIVO 
        with open(Nombre_predetermiando, 'rb') as SinNombre: # ABRIR EL ARCHIVO EN MODO LECTURA BINARIA
            with open(archivo, 'wb') as ConNombre: # ABRIR EL ARCHIVO EN MODO ESCRITURA BINARIA
                ConNombre.write(SinNombre.read()) # ESCRIBIR EN EL ARCHIVO EL CONTENIDO DE LA IMAGEN "SINNOMBRE"
                ConNombre.close() # CERRA EL DOCUMENTO

inicio = False
nombre_archivo = "no.txt" # NOMBRE AUXILIAR DEL ARCHIVO TXT
def servicio_player(request, response): # FUNCION SI HAY UN SERVICIO
        global inicio
        inicio = True
        TurtleBotInterfaceNode = rclpy.create_node('turtle_bot_interface')
        TurtleBotInterfaceNode.create_timer(0.75, servicio_player) # TIEMPO DE MUESTREO
        if request.data: # SI HAY UN SERVICIO
            response.success = True # COMUNICACIÓN BOOLEANA DEL SERVICIO
            global nombre_archivo
            if nombre_archivo != "recorrido.txt": # NOMBRE DEL ARCHIVO A GUARDAR Y QUE SE DEBE INGRESAR POR EL USARIO
                file_options = {
                'title': 'Seleccionar un archivo',
                'filetypes': [('Todos los archivos', '.*')],
                'initialdir': '~/Descargas',  # BUSCA EL ARCHIVO EN DESCARGAD
                }
                
                archivo = filedialog.askopenfilename(**file_options)
                nombre_archivo = os.path.basename(archivo)
                response.message = str(nombre_archivo) # SE OBTIENE EL NOMBRE DEL ARCHIVO PARA ENVIARLO POR MEDIO DEL SERVICIO
                pantalla.fill((255, 255, 255)) # PANTALLA EN BLANCO
                pygame.display.update() # ACTUALIZACION DE LA PANTALLA
        else:
            response.success = False
            response.message = "no puedo enviarte el archivo"
        return response

def main(args=None): # FUNCIÓN PRINCIAL
    rclpy.init(args=args) # PARA INICIALIZAR EL CÓDIGO EN PYTHON
    TurtleBotInterfaceNode = rclpy.create_node('turtle_bot_interface') # CREACIÓN DEL NODO
    Servicio = TurtleBotInterfaceNode.create_service(SetBool, 'recorrido_guardado', servicio_player)
    subscriber_position = TurtleBotInterfaceNode.create_subscription(Float32MultiArray, '/turtlebot_position', callback, 10) # CREACIÓN DEL SUSCRIBER
    #suscriber_velocity=TurtleBotInterfaceNode.create_subscription(Float32MultiArray, "/turtlebot_cmdVel2", callback,10)
    callback(msg=Float32MultiArray()) # LLAMAR SIEMPRE ESTA FUNCION
    rclpy.spin(TurtleBotInterfaceNode) # PARA NO DEJAR MORIR LA COMUNICACIÓN
    rclpy.shutdown() # PARA APAGAR LA COMUNICACIÓN

if __name__ == '__main__': # PARA CORRER LA FUNCIÓN PRINCIPAL
    main() # FUNCIÓN PRINCIPAL
