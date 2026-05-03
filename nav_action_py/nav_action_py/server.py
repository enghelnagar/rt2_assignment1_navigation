import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor

from nav_action_interfaces.action import NavigateRobot 
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math

class NavigationServer(Node):
    def __init__(self):
        super().__init__('navigation_server_py')
        
        # Initialize the Action Server
        self._action_server = ActionServer(
            self,
            NavigateRobot, 
            'navigate_robot',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback)
        
        # Publisher to control the robot's velocity
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscriber to get the robot's current position from Odometry
        self.subscription = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        
        self.current_pos = None
        self.get_logger().info('Python Navigation Action Server has been started.')

    def odom_callback(self, msg):
        # Continuously update the current position
        self.current_pos = msg.pose.pose

    def goal_callback(self, goal_request):
        # Accept all new goal requests
        self.get_logger().info('Received a new goal request.')
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        # Accept cancellation requests
        self.get_logger().info('Received a cancel request.')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')
        

        feedback_msg = NavigateRobot.Feedback()
        result = NavigateRobot.Result()

        target_x = goal_handle.request.x
        target_y = goal_handle.request.y
        target_theta = goal_handle.request.theta

        # Main control loop
        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.stop_robot()
                self.get_logger().warn('Goal execution canceled.')
                return result

            if self.current_pos is not None:
                current_x = self.current_pos.position.x
                current_y = self.current_pos.position.y
                
                # Calculate distance to target
                dist = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
                
                # Convert Quaternion to Euler angles to get Yaw (theta)
                q = self.current_pos.orientation
                siny_cosp = 2 * (q.w * q.z + q.x * q.y)
                cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
                current_yaw = math.atan2(siny_cosp, cosy_cosp)

                # Publish feedback
                feedback_msg.distance_remaining = dist
                goal_handle.publish_feedback(feedback_msg)

                # Simple proportional control logic
                vel = Twist()
                if dist > 0.2:
                    # Adjust heading and move forward
                    angle_to_target = math.atan2(target_y - current_y, target_x - current_x)
                    vel.angular.z = 0.5 * (angle_to_target - current_yaw)
                    vel.linear.x = 0.2
                elif abs(target_theta - current_yaw) > 0.1:
                    # Reached point, adjust final orientation
                    vel.linear.x = 0.0
                    vel.angular.z = 0.3 * (target_theta - current_yaw)
                else:
                    # Goal fully reached
                    break
                
                self.publisher_.publish(vel)

            # Allow node to process other callbacks
            rclpy.spin_once(self, timeout_sec=0.1)

        self.stop_robot()
        goal_handle.succeed()
        result.success = True
        self.get_logger().info('Goal reached successfully!')
        return result

    def stop_robot(self):
        # Publish zero velocity to stop
        empty_vel = Twist()
        self.publisher_.publish(empty_vel)

def main(args=None):
    rclpy.init(args=args)
    node = NavigationServer()
    # Use MultiThreadedExecutor to handle callbacks and actions concurrently
    executor = MultiThreadedExecutor()
    rclpy.spin(node, executor=executor)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()