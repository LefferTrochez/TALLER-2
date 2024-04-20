#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import os
from example_interfaces.srv import SetBool
from std_msgs.msg import Float32MultiArray, MultiArrayDimension

# Variables globales
cont = 0
inicio = True
global acumular1
acumular1=[0,0]
datos = []
global tiempo
global acumular2
acumular2=[0,0]
tiempo=0
class TurtleBotPlayerNode(Node):
    def __init__(self):
        super().__init__("turtle_bot_player")
        self.publisher_ = self.create_publisher(Float32MultiArray, "turtlebot_cmdVel", 10)
        self.timer_ = self.create_timer(0.0335, self.recorrido)
        self.cliente = self.create_client(SetBool, 'recorrido_guardado')
    
    def recorrido(self):
        global inicio
        if inicio:
            if not self.cliente.wait_for_service(timeout_sec=1.0):
                self.get_logger().warn('Esperando por el servicio...')
                return
            request = SetBool.Request()
            request.data = True
            future = self.cliente.call_async(request)
            future.add_done_callback(self.funcion)
        else:
            self.funcion(None)
    
    def funcion(self, future):
        global cont, inicio, datos, acumular1, tiempo, acumular2
        print("valorm inicio: " + str(inicio))
        if inicio:
            
            try:
                response = future.result()
                # Nombre fijo del archivo que buscamos
                archivo_nombre = "recorrido.txt"
                # Ruta del directorio de descargas
                descargas_dir = os.path.join(os.path.expanduser("~"), "Descargas")
                # Ruta completa al archivo
                archivo_ruta = os.path.join(descargas_dir, archivo_nombre)
                # Verifica si el archivo existe y léelo
                if os.path.exists(archivo_ruta):

                    with open(archivo_ruta, 'r') as archivo:
                        datos = [line.strip() for line in archivo.readlines()]
                        inicio = False
                        self.get_logger().info(f"Archivo {archivo_nombre} leído correctamente.")
                else:
                    self.get_logger().error(f"El archivo {archivo_ruta} no fue encontrado.")
            except Exception as e:
                self.get_logger().error('Servicio fallido ' + str(e))
        else:
            
            msg = Float32MultiArray()
        
            if 0 <= cont < len(datos):
                x = datos[cont]
                valor = x.split(',')
                acumular1.append(valor[0])
                acumular2.append(valor[1])
                msg.layout.dim = [MultiArrayDimension(label='cmd_vel_time', size=3, stride=3)]
                if (acumular1[-1]==0 and acumular1[-2]!=0) or (acumular2[-1]==0 and acumular2[-2]!=0):
                    tiempo=0
                else:
                    tiempo+=0.0513
                    msg.data = [float(valor[0]), float(valor[1]), tiempo]
                self.get_logger().info(f"Velocidad lineal: {msg.data[0]}")
                self.get_logger().info(f"Velocidad angular: {msg.data[1]}")
                self.get_logger().info(f"tiempo: {msg.data[2]}")
                self.publisher_.publish(msg)
                cont += 1
                print(f"Linea No. {cont} de {len(datos)}")
				

def main(args=None):
    rclpy.init(args=args)
    node = TurtleBotPlayerNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == "__main__":
    main()
