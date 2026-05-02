#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
from assignment1_rt.msg import VelMessage  # Import our new custom message


class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')
        # Create publisher for the first turtle
        self.pub_turtle1 = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        # Create publisher for the second turtle
        self.pub_turtle2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.get_logger().info("Controller Node Started! Ready to send commands.")

         # [NEW] Publisher for the Custom Message
        self.pub_custom = self.create_publisher(VelMessage, '/robot_vel_status', 10)



    def send_command(self, turtle_name, velocity):
        # Prepare the message (Velocity)
        msg = Twist()
        msg.linear.x = float(velocity)
        msg.angular.z = 0.0 # No rotation, moving straight for simplicity

        # Determine which turtle will receive the command
        target_publisher = None
        if turtle_name == "turtle1":
            target_publisher = self.pub_turtle1
        elif turtle_name == "turtle2":
            target_publisher = self.pub_turtle2
        else:
            print("Unknown turtle name! Please verify.")
            return

        # 1. Send the movement command
        self.get_logger().info(f"Moving {turtle_name} with speed {velocity}...")
        target_publisher.publish(msg)

        # 2. Wait for 1 second (while the turtle moves)
        time.sleep(1.0)

        # 3. Send stop command (zero velocity)
        msg.linear.x = 0.0
        target_publisher.publish(msg)
        self.get_logger().info("Stopped.")

        # 4. [NEW] Publish Custom Message
        custom_msg = VelMessage()
        custom_msg.info = "velocity"          # The required string
        custom_msg.linear_x = float(lin_x)    # Linear velocity X
        custom_msg.angular_z = float(ang_z)   # Angular velocity Z
        
        self.pub_custom.publish(custom_msg)
        # self.get_logger().info(f"Published custom msg: {custom_msg.info}, {lin_x}, {ang_z}")


def main(args=None):
    rclpy.init(args=args)
    node = RobotController()

    try:
        while rclpy.ok():
            # Request input from the user
            print("\n--- Robot Control Interface ---")
            t_name = input("Enter turtle name (turtle1 or turtle2): ")
            
            # Exit the program if 'exit' is typed
            if t_name == 'exit':
                break
                
            try:
                vel = float(input("Enter velocity (e.g., 2.0): "))
                # Call the movement function
                node.send_command(t_name, vel)
            except ValueError:
                print("Invalid number! Please enter a numeric velocity.")

    except KeyboardInterrupt:
        pass
    finally:
    rclpy.init(args=args)
    node = ControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()

