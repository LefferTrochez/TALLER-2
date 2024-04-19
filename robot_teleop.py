#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from pynput import keyboard
from std_msgs.msg import Float32MultiArray, MultiArrayDimension
import threading
import time

class TurtleBotTeleopNode(Node):
    def __init__(self):
        super().__init__("turtle_bot_teleop")
        self.publisher_ = self.create_publisher(Float32MultiArray, "turtlebot_cmdVel", 10)
        self.linear_in = float(input("What is the Linear Velocity?: "))
        self.angular_in = float(input("What is the Angular Velocity?: "))
        self.key_mapping = {
            'w': (1, 0),
            's': (-1, 0),
            'a': (0, 1),
            'd': (0, -1),
        }
        self.pressed_keys = set()
        self.key_press_times = {}

def on_press(key, node: TurtleBotTeleopNode):
    try:
        key_char = key.char
    except AttributeError:
        return

    if key_char in node.key_mapping and key_char not in node.pressed_keys:
        node.pressed_keys.add(key_char)
        node.key_press_times[key_char] = time.time()

def on_release(key, node: TurtleBotTeleopNode):
    try:
        key_char = key.char
    except AttributeError:
        return

    if key_char in node.key_mapping and key_char in node.pressed_keys:
        
        node.pressed_keys.remove(key_char)
        elapsed_time = time.time() - node.key_press_times[key_char]
        node.get_logger().info(f"Tiempo presionado {key_char}: {elapsed_time:.2f} seg")
        update_velocity(key_char, False, elapsed_time, node)

def update_velocity(key, pressing, elapsed_time, node: TurtleBotTeleopNode):
    linear_factor, angular_factor = node.key_mapping[key]
    msg = Float32MultiArray()
    msg.layout.dim.append(MultiArrayDimension())
    msg.layout.dim[0].label = "cmd_vel_time"
    msg.layout.dim[0].size = 3
    msg.layout.dim[0].stride = 3

    if pressing:
        msg.data = [linear_factor * node.linear_in, angular_factor * node.angular_in, elapsed_time]  # No elapsed time when key is pressed
    else:
        msg.data = [0.0, 0.0, elapsed_time]  # Include elapsed time on release
    node.publisher_.publish(msg)
    
def main(args=None):
    rclpy.init(args=args)
    turtle_bot_teleop_node = TurtleBotTeleopNode()
    turtle_bot_teleop_node.get_logger().info('"Now, to move the robot you have to press: \n w | a | s | d"')

    processing_thread = threading.Thread(target=process_keys, args=(turtle_bot_teleop_node,), daemon=True)
    processing_thread.start()

    spin_thread = threading.Thread(target=rclpy.spin, args=(turtle_bot_teleop_node,), daemon=True)
    spin_thread.start()

    with keyboard.Listener(
        on_press=lambda key: on_press(key, turtle_bot_teleop_node),
        on_release=lambda key: on_release(key, turtle_bot_teleop_node)
    ) as listener:
        listener.join()

    rclpy.shutdown()

def process_keys(node: TurtleBotTeleopNode):
    while rclpy.ok():
        current_time = time.time()
        for key in list(node.pressed_keys):  # Usar list() para copiar porque el conjunto puede cambiar
            start_time = node.key_press_times[key]
            elapsed_time = current_time - start_time
            update_velocity(key, True, elapsed_time, node)
        time.sleep(0.05)  # Determina la rapidez con la que se repite la acció
if __name__ == '__main__':
    main()
