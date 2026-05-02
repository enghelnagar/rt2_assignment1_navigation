#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
import math

class DistanceMonitor(Node):
    def __init__(self):
        super().__init__('distance_monitor')
        
        # --- Subscribers to get positions ---
        self.create_subscription(Pose, '/turtle1/pose', self.update_pose_turtle1, 10)
        self.create_subscription(Pose, '/turtle2/pose', self.update_pose_turtle2, 10)

        # --- Publishers to stop robots ---
        self.pub_vel_turtle1 = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub_vel_turtle2 = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)

        # --- Publisher for distance ---
        self.pub_distance = self.create_publisher(Float32, '/distance', 10)

        # Variables to store positions
        self.pose_t1 = None
        self.pose_t2 = None

        # Thresholds
        self.min_distance_threshold = 1.5 # Minimum allowed distance
        self.lower_bound = 1.0            # Wall limit (min)
        self.upper_bound = 10.0           # Wall limit (max)

        self.get_logger().info("Distance Monitor Node Started!")

    def update_pose_turtle1(self, msg):
        self.pose_t1 = msg
        self.perform_checks()

    def update_pose_turtle2(self, msg):
        self.pose_t2 = msg
        self.perform_checks()

    def perform_checks(self):
        # We need both positions to calculate distance
        if self.pose_t1 is None or self.pose_t2 is None:
            return

        # 1. Calculate Euclidean Distance
        dist_x = self.pose_t1.x - self.pose_t2.x
        dist_y = self.pose_t1.y - self.pose_t2.y
        distance = math.sqrt(dist_x**2 + dist_y**2)

        # 2. Publish Distance
        dist_msg = Float32()
        dist_msg.data = distance
        self.pub_distance.publish(dist_msg)

        # 3. Check Collision (Too Close)
        if distance < self.min_distance_threshold:
            self.get_logger().warn(f"TURTLES TOO CLOSE! Distance: {distance:.2f}")
            self.stop_turtle("turtle1")
            self.stop_turtle("turtle2")

        # 4. Check Boundaries (Walls) for Turtle 1
        if not (self.lower_bound < self.pose_t1.x < self.upper_bound) or \
           not (self.lower_bound < self.pose_t1.y < self.upper_bound):
            self.get_logger().warn("Turtle 1 hitting wall!")
            self.stop_turtle("turtle1")

        # 5. Check Boundaries (Walls) for Turtle 2
        if not (self.lower_bound < self.pose_t2.x < self.upper_bound) or \
           not (self.lower_bound < self.pose_t2.y < self.upper_bound):
            self.get_logger().warn("Turtle 2 hitting wall!")
            self.stop_turtle("turtle2")

    def stop_turtle(self, turtle_name):
        stop_msg = Twist()
        stop_msg.linear.x = 0.0
        stop_msg.angular.z = 0.0
        
        if turtle_name == "turtle1":
            self.pub_vel_turtle1.publish(stop_msg)
        elif turtle_name == "turtle2":
            self.pub_vel_turtle2.publish(stop_msg)

def main(args=None):
    rclpy.init(args=args)
    node = DistanceMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
