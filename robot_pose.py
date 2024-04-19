# #!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# import RPi.GPIO as GPIO
# import time
# from std_msgs.msg import Float32MultiArray, MultiArrayDimension
# import math

# tiempo=0

# class PoseNode(Node):
    
#     def __init__(self):
#         super().__init__('Pose_node')
#         self.publisher_ = self.create_publisher(Twist, "/turtlebot_position", 10)
       
#         self.subscription_velocity = self.create_subscription(
#             Float32MultiArray, '/turtlebot_cmdVel2', self.velocity_callback, 10)
#         self.x = 0
#         self.y = 0
#         self.theta = 0
#         self.timer_period = 0.1  # Publicar la posición cada 0.1 segundos (ajuste según sea necesario)
#         self.timer = self.create_timer(self.timer_period, self.publish_position)

#     def velocity_callback(self, twist_msg):
#         # Aquí deberías calcular los cambios en la posición (delta_x y delta_y) basados en la velocidad recibida
#         # Por ejemplo, si estás asumiendo un tiempo constante entre mensajes, podrías hacer algo como esto:
#         # Esto es solo un ejemplo y deberás ajustarlo a tu aplicación específica
#         delta_time = twist_msg.data[2]  # Suponiendo que los mensajes llegan cada 1 segundo

#         delta_x = ((twist_msg.data[0]+twist_msg.data[1])/2)* delta_time

#         theta_local= (( twist_msg.data[0]-twist_msg.data[1])/19)*delta_time

#         delta_y =0
#         print(delta_x,delta_y,theta_local*(180/math.pi),delta_time)
#         # Actualizar la pose global del robot
#         self.update_global_position(delta_x, delta_y,theta_local,twist_msg)

#     def update_global_position(self, delta_x, delta_y,theta_local,twist_msg):
        
#         #Calcular el cambio global basado en la orientación del robot
   
#         self.theta=theta_local
#         print (self.theta)
#         delta_x_global = delta_x * math.cos(self.theta) - delta_y * math.sin(self.theta)
#         delta_y_global = delta_x * math.sin(self.theta) + delta_y * math.cos(self.theta)
        
#         # Actualizar la posición global
#         self.x += delta_x_global
#         self.y += delta_y_global
       
#         #self.get_logger().info(f'Nueva posición: x={self.x}, y={self.y}')
#     def publish_position(self):
#         msg = Twist()
#         msg.linear.x = float(self.x)
#         msg.linear.y = float(self.y)
#         self.publisher_.publish(msg)
        

# def main(args=None):
#     rclpy.init(args=args)
#     node = PoseNode()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         GPIO.cleanup()
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()

#########################################################################################3
#!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist
# import RPi.GPIO as GPIO
# import time
# from std_msgs.msg import Float32MultiArray, MultiArrayDimension
# import math

# tiempo=0
# class PoseNode(Node):
    
#     def __init__(self):
#         super().__init__('Pose_node')
#         self.publisher_ = self.create_publisher(Twist, "/turtlebot_position", 10)
       
#         self.subscription_velocity = self.create_subscription(
#             Float32MultiArray, '/turtlebot_cmdVel2', self.velocity_callback, 10)
#         self.x = 0
#         self.y = 0
#         self.theta = 0
#         self.timer_period = 0.001  # Publicar la posición cada 0.1 segundos (ajuste según sea necesario)
#         self.timer = self.create_timer(self.timer_period, self.publish_position)

#     def velocity_callback(self, twist_msg):
#         # Aquí deberías calcular los cambios en la posición (delta_x y delta_y) basados en la velocidad recibida
#         # Por ejemplo, si estás asumiendo un tiempo constante entre mensajes, podrías hacer algo como esto:
#         # Esto es solo un ejemplo y deberás ajustarlo a tu aplicación específica
#         delta_time = twist_msg.data[2]  # Suponiendo que los mensajes llegan cada 1 segundo
#         R = 4.4
#         w_r = twist_msg.data[0] / R
#         w_l = twist_msg.data[1] / R
#         angular_r = w_r*delta_time
#         angular_l = w_l*delta_time

        
#         # Actualizar la pose global del robot
#         # Calcular el cambio global basado en la orientación del robot
#         # delta_x_global = delta_x * math.cos(theta) - delta_y * math.sin(theta)
#         # delta_y_global = delta_x * math.sin(theta) + delta_y * math.cos(theta)
      
#         l = 19
#         self.theta+=(( twist_msg.data[0]-twist_msg.data[1])/19)*delta_time
#         self.x +=(R/2)*(angular_r + angular_l)*math.cos(self.theta)
#         self.y +=(R/2)*(angular_r + angular_l)*math.sin(self.theta)
        
#         # # Actualizar la posición global
#         # self.x += delta_x_global
#         # self.y += delta_y_global
       
#         #self.get_logger().info(f'Nueva posición: x={self.x}, y={self.y}')
#     def publish_position(self):
#         msg = Twist()
#         msg.linear.x = float(self.x)
#         msg.linear.y = float(self.y)
#         self.publisher_.publish(msg)
        

# def main(args=None):
#     rclpy.init(args=args)
#     node = PoseNode()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         GPIO.cleanup()
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()

##########################################################

#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import RPi.GPIO as GPIO
import time
from std_msgs.msg import Float32MultiArray, MultiArrayDimension
import math

tiempo=0
global lista
lista=[0,0]
class PoseNode(Node):
    
    def __init__(self):
        super().__init__('Pose_node')
        self.publisher_ = self.create_publisher(Float32MultiArray, "/turtlebot_position", 10)
       
        self.subscription_velocity = self.create_subscription(
            Float32MultiArray, '/turtlebot_cmdVel2', self.velocity_callback, 10)
        self.x = 0
        self.y = 0
        self.theta = 0
        self.velocidad1=0
        self.velocidad2=0
        self.timer_period = 0.1  # Publicar la posición cada 0.1 segundos (ajuste según sea necesario)
        self.timer = self.create_timer(self.timer_period, self.publish_position)

    def velocity_callback(self, twist_msg):
        global lista
        print(" ")
        
        delta_time = twist_msg.data[2] 
        lista.append(delta_time) # Suponiendo que los mensajes llegan cada 1 segundo
        self.velocidad1=twist_msg.data[0]
        self.velocidad2=twist_msg.data[1]
        R = 4.4
        w_r = twist_msg.data[0] / R
        w_l = twist_msg.data[1] / R
        angular_r = w_r*delta_time
        angular_l = w_l*delta_time
        if lista[-2]>lista[-1]:
            lista[-2]=0
        print("resta: " + str(lista[-1]-lista[-2]))
       
        self.theta+= (( twist_msg.data[1]-twist_msg.data[0])/19)*(lista[-1]-lista[-2])        
        delta_y =0
        print("vel_r: "+str(round(w_r,3))+" ,     vel_l: "+str(round(w_l,3)))
        # Actualizar la pose global del robot
        self.update_global_position(angular_l,angular_r)

    def update_global_position(self, angular_l, angular_r):
        R = 4.4
        #Calcular el cambio global basado en la orientación del robot
        self.x +=(R/2)*(angular_r + angular_l)*math.cos(self.theta)
        self.y +=(R/2)*(angular_r + angular_l)*math.sin(self.theta)
        print("x: " +str(round((self.x),3)) + ",   y: " + str(round((self.y),3))+ " ,    theta:"+ str(round((self.theta)*180/math.pi,3)))

    def publish_position(self):
        msg = Float32MultiArray()
        msg.layout.dim = [MultiArrayDimension(label='cmd_vel_time', size=4, stride=4)]
        msg.data=[self.x,self.y,self.velocidad1,self.velocidad2]
        self.publisher_.publish(msg)
        
def main(args=None):
    rclpy.init(args=args)
    node = PoseNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
