import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient


from nav_action_interfaces.action import NavigateRobot 
import threading
import sys

class NavigationClient(Node):
    def __init__(self):
        super().__init__('navigation_client_py')
        
    
        self._action_client = ActionClient(self, NavigateRobot, 'navigate_robot')
        self._goal_handle = None

    def send_goal(self, x, y, theta):
        self.get_logger().info('Waiting for action server...')
        self._action_client.wait_for_server()

      
        goal_msg = NavigateRobot.Goal()
        goal_msg.x = x
        goal_msg.y = y
        goal_msg.theta = theta

        self.get_logger().info(f'Sending goal: X={x}, Y={y}, Theta={theta}')
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected by server.')
            return

        self.get_logger().info('Goal accepted by server. Executing...')
        self._goal_handle = goal_handle
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        # Print distance dynamically
        dist = feedback_msg.feedback.distance_remaining
        self.get_logger().info(f'Feedback: Distance remaining: {dist:.2f} meters')

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: Success = {result.success}')
        self._goal_handle = None

    def cancel_goal(self):
        if self._goal_handle is not None:
            self.get_logger().info('Sending cancel request...')
            cancel_future = self._goal_handle.cancel_goal_async()
            cancel_future.add_done_callback(self.cancel_done_callback)
        else:
            self.get_logger().info('No active goal to cancel.')

    def cancel_done_callback(self, future):
        cancel_response = future.result()
        if len(cancel_response.goals_canceling) > 0:
            self.get_logger().info('Goal successfully canceled.')
            self._goal_handle = None
        else:
            self.get_logger().info('Goal failed to cancel.')

def ui_thread_func(client_node):
    # Separate thread for the interactive User Interface
    while rclpy.ok():
        print("\n--- Python Navigation Menu ---")
        print("1. Send a new goal")
        print("2. Cancel the current goal")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            try:
                x = float(input("Enter target X: "))
                y = float(input("Enter target Y: "))
                theta = float(input("Enter target Theta: "))
                client_node.send_goal(x, y, theta)
            except ValueError:
                print("Invalid input! Please enter numeric values.")
        elif choice == '2':
            client_node.cancel_goal()
        elif choice == '3':
            print("Exiting...")
            rclpy.shutdown()
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")

def main(args=None):
    rclpy.init(args=args)
    client_node = NavigationClient()

    # Start the UI thread
    ui_thread = threading.Thread(target=ui_thread_func, args=(client_node,))
    ui_thread.daemon = True
    ui_thread.start()

    # Spin the ROS2 node in the main thread
    rclpy.spin(client_node)

    client_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()