#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import RPi.GPIO as GPIO
import time
from std_msgs.msg import Float32MultiArray, MultiArrayDimension
from std_msgs.msg import Float64 
global tiempo
global pulse_count_A
global pulse_count_B
global listapula
global listavela
global listavelb
listavela=[]
listavelb=[]
listapula=[]
global listapulb
listapulb=[]
tiempo=0
# Variables globales
motorAPin2 = 15
motorAPin1 = 13
motorAPWMPin = 32
motorBPin2 = 7
motorBPin1 = 11
motorBPWMPin = 33
standbyPin = 16

encoderA_pins = [23, 19]
encoderB_pins = [22, 18]

GPIO.setmode(GPIO.BOARD)
GPIO.setup([motorAPin1, motorAPin2, motorAPWMPin, motorBPin1, motorBPin2, motorBPWMPin, standbyPin], GPIO.OUT)
for pin in encoderA_pins + encoderB_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variables para contar pulsos
pulse_count_A = 0
pulse_count_B = 0

# Circunferencia de la rueda en cm
wheel_circumference_A = 3.14159 * 8.8
wheel_circumference_B = 3.14159 * 8.8

# Resolución del Encoder
encoder_resolution = 74.8

# Callbacks para contar pulsos
def count_pulse_A(channel):
    global pulse_count_A
    pulse_count_A += 1

def count_pulse_B(channel):
    global pulse_count_B
    pulse_count_B += 1

# Configurar interrupciones para encoders
GPIO.add_event_detect(encoderA_pins[0], GPIO.RISING, callback=count_pulse_A)
GPIO.add_event_detect(encoderB_pins[0], GPIO.RISING, callback=count_pulse_B)

class WheelsVelocityNode(Node):
    def __init__(self):
        super().__init__('wheels_velocity_node')
        self.subscription = self.create_subscription(Float32MultiArray, '/turtlebot_cmdVel', self.handle_twist, 10)
        self.publisher_velocity = self.create_publisher(Float32MultiArray, "/turtlebot_cmdVel2", 10)
        # self.subscription_time = self.create_subscription(Float64, 'turtlebot_time', self.forward, 10)
        # self.subscription_time_2 = self.create_subscription(Float64, 'turtlebot_time', self.backward, 10)
        # self.subscription_time_3 = self.create_subscription(Float64, 'turtlebot_time', self.righround, 10)
        # self.subscription_time_4 = self.create_subscription(Float64, 'turtlebot_time', self.leftround, 10)


    def handle_twist(self, msg):
        
        linear_vel = msg.data[0]
        angular_vel = msg.data[1]
        tiempo_real=msg.data[2]
        

        if linear_vel > 0:
            self.forward(abs(linear_vel),tiempo_real)
        elif linear_vel < 0:
            self.backward(abs(linear_vel),tiempo_real)
        elif angular_vel > 0:
            self.leftround(abs(angular_vel),tiempo_real)
        elif angular_vel < 0:
            self.righround(abs(angular_vel),tiempo_real)
        else:
            self.stop()

    def forward(self, speed,tiempo):
        global listapula,listapulb, listavela,listavelb
        if float(speed) != 0:
            print(" ")
            print("Forward: +" + str(speed))
            GPIO.output(motorAPin1, GPIO.LOW)
            GPIO.output(motorAPin2, GPIO.HIGH)
            motorA_PWM = GPIO.PWM(motorAPWMPin, 100)
            motorA_PWM.start(speed+20-1+14)  
            GPIO.output(motorBPin1, GPIO.LOW)
            GPIO.output(motorBPin2, GPIO.HIGH)
            motorB_PWM = GPIO.PWM(motorBPWMPin, 100)
            motorB_PWM.start(speed+20+10+15)
            listapula.append(pulse_count_A)
            listapulb.append(pulse_count_B)
            GPIO.output(standbyPin, GPIO.HIGH)
            start_time = time.time()
            duration = tiempo
            duration1=0.01
            if duration != 0 :
                velocity_A = (pulse_count_A / duration) * (wheel_circumference_A / encoder_resolution) # vel lineal
                velocity_B = (pulse_count_B / duration) * (wheel_circumference_B / encoder_resolution)
                print("Duracion pulso A: "+str(round(pulse_count_A,3)) + ", duracion: " +str(round(duration,3)))
                print("Duracion pulso B: "+str(round(pulse_count_B,3)) + ", duracion: " +str(round(duration,3)))
                if velocity_A < speed*(1.3) and velocity_B< speed*(1.3):
                    print(f"Velocidad Motor A: {round(velocity_A,3)} cm/s")
                    print(f"Velocidad Motor B: {round(velocity_B,3)} cm/s")
                    self.update_velocity(velocity_A, velocity_B, tiempo)
                else:
                    self.update_velocity(speed, speed, tiempo)
                try:
                    while time.time() - start_time < duration1:
                        time.sleep(0.04)  # Pequeña pausa para reducir la carga de la CPU
                finally:
                    pass     
        else:
            self.stop()
            
    def backward(self, speed,tiempo):
        
        if float(speed) != 0:
            print("Backward: -" + str(speed))
            GPIO.output(motorAPin1, GPIO.HIGH)
            GPIO.output(motorAPin2, GPIO.LOW)
            motorA_PWM = GPIO.PWM(motorAPWMPin, 100)
            motorA_PWM.start(speed+20+7.3)  # Offset de velocidad para equilibrar con Motor B
            GPIO.output(motorBPin1, GPIO.HIGH)
            GPIO.output(motorBPin2, GPIO.LOW)
            motorB_PWM = GPIO.PWM(motorBPWMPin, 100)
            motorB_PWM.start(speed+20+2+2)
            GPIO.output(standbyPin, GPIO.HIGH)
            start_time = time.time()
          
            duration = tiempo
            duration1=0.01
            if duration != 0 :
            
                velocity_A = -(pulse_count_A / duration) * (wheel_circumference_A / encoder_resolution)
                velocity_B = -(pulse_count_B / duration) * (wheel_circumference_B / encoder_resolution)
                
                if velocity_A < speed*(1.3) and velocity_B< speed*(1.3):
                    print(f"Velocidad Motor A: {round(velocity_A,3)} cm/s")
                    print(f"Velocidad Motor B: {round(velocity_B,3)} cm/s")
            
                    self.update_velocity(velocity_A, velocity_B, tiempo)
                else:
                    self.update_velocity(speed, speed, tiempo)
                    
                try:
                    while time.time() - start_time < duration1:
                        time.sleep(0.04)  # Pequeña pausa para reducir la carga de la CPU
                finally:
                    pass
            else: 
                pass
                    
        else:
            self.stop()


        
    def leftround(self, speed,tiempo):
        
        if float(speed) != 0:
            print("Leftround: -" + str(speed))
            GPIO.output(motorAPin1, GPIO.LOW)
            GPIO.output(motorAPin2, GPIO.HIGH)
            motorA_PWM = GPIO.PWM(motorAPWMPin, 100)
            motorA_PWM.start(speed*19/2)  # Offset de velocidad para equilibrar con Motor B
            GPIO.output(motorBPin1, GPIO.HIGH)
            GPIO.output(motorBPin2, GPIO.LOW)
            motorB_PWM = GPIO.PWM(motorBPWMPin, 100)
            motorB_PWM.start(speed*19/2)
            GPIO.output(standbyPin, GPIO.HIGH)
            start_time = time.time()
            duration = tiempo
            duration1=0.01
            if duration != 0 :
                print("Pulsos A: " +str(pulse_count_A))
                velocity_A = (pulse_count_A / duration) * (wheel_circumference_A / encoder_resolution)
                velocity_B = -(pulse_count_B / duration) * (wheel_circumference_B / encoder_resolution)
                print(f"Velocidad Motor A: {round(velocity_A,3)} cm/s")
                print(f"Velocidad Motor B: {round(velocity_B,3)} cm/s")
                if abs(velocity_A) < abs(speed)*(1.3) and abs(velocity_B)< abs(speed*(1.3)):
                    print(f"Velocidad Motor A: {round(velocity_A,3)} cm/s")
                    print(f"Velocidad Motor B: {round(velocity_B,3)} cm/s")
                    print(f"Velocidad angular: {round((velocity_A-velocity_B)/19,3)} cm/s")
                    self.update_velocity(velocity_A, velocity_B, tiempo)
                else:
                    self.update_velocity(-speed*19/2, speed*19/2, tiempo)
                    print(f"Velocidad angular: {round((velocity_A-velocity_B)/19,3)} cm/s")

                try:
                    while time.time() - start_time < duration1:
                        time.sleep(0.04)  # Pequeña pausa para reducir la carga de la CPU
                finally:
                    pass
            else: 
                pass
                    
        else:
            self.stop()
    def righround(self, speed,tiempo):
        
        if float(speed) != 0:
            print("Righround: -" + str(speed))
            GPIO.output(motorAPin1, GPIO.HIGH)
            GPIO.output(motorAPin2, GPIO.LOW)
            motorA_PWM = GPIO.PWM(motorAPWMPin, 100)
            motorA_PWM.start(speed*19/2)  # Offset de velocidad para equilibrar con Motor B
            GPIO.output(motorBPin1, GPIO.LOW)
            GPIO.output(motorBPin2, GPIO.HIGH)
            motorB_PWM = GPIO.PWM(motorBPWMPin, 100)
            motorB_PWM.start(speed*19/2)
            GPIO.output(standbyPin, GPIO.HIGH)
            start_time = time.time()
            duration = tiempo
            duration1=0.01
            if duration != 0 :
                print("")
                print(pulse_count_A)
                velocity_A = -(pulse_count_A / duration) * (wheel_circumference_A / encoder_resolution)
                velocity_B = (pulse_count_B / duration) * (wheel_circumference_B / encoder_resolution)
                print(f"Velocidad Motor A: {round(velocity_A,3)} cm/s")
                print(f"Velocidad Motor B: {round(velocity_B,3)} cm/s")
                if abs(velocity_A*19/2) < abs(speed*(1.3)*19/2) and abs(velocity_B*19)< abs(speed*(1.3)*19/2):
                    print(f"Velocidad Motor A: {round(velocity_A,3)} cm/s")
                    print(f"Velocidad Motor B: {round(velocity_B,3)} cm/s")
                    print(f"Velocidad angular: {round((velocity_A-velocity_B)/19,3)} cm/s")
                    self.update_velocity(velocity_A, velocity_B, tiempo)
                else:
                    self.update_velocity(speed*19/2, -speed*19/2, tiempo)
                    print(f"Velocidad angular: {round((velocity_A-velocity_B)/19,3)} cm/s")
                try:
                    while time.time() - start_time < duration1:
                        time.sleep(0.04)  # Pequeña pausa para reducir la carga de la CPU
                finally:
                    pass
            else: 
                pass
                    
        else:
            self.stop()
    def stop(self):
        global pulse_count_B
        pulse_count_B = 0
        global pulse_count_A
        pulse_count_A = 0
        print("Stop")
        print("____________________________________________")
        GPIO.output(standbyPin, GPIO.HIGH)
    def update_velocity(self,motor1,motor2,tiempo):
        msg = Float32MultiArray()
        msg.layout.dim = [MultiArrayDimension(label='cmd_vel_time', size=3, stride=3)]
        msg.data=[motor1,motor2,tiempo]
        self.publisher_velocity.publish(msg)
    



def main(args=None):
    rclpy.init(args=args)
    node = WheelsVelocityNode()
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
