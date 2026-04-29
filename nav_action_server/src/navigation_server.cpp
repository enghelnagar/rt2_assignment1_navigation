#include "nav_action_server/navigation_server.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <thread>
#include <cmath>

namespace nav_components
{

NavigationServer::NavigationServer(const rclcpp::NodeOptions & options)
: Node("navigation_server", options), current_x_(0.0), current_y_(0.0), current_theta_(0.0)
{
  using namespace std::placeholders;

  // 1. Initialize publisher and subscriber as instructed in the assignment
  cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>("cmd_vel", 10);
  
  odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
    "odom", 10, std::bind(&NavigationServer::odom_callback, this, _1));

  // 2. Initialize the action server with the required callbacks
  action_server_ = rclcpp_action::create_server<NavigateRobot>(
    this,
    "navigate_robot",
    std::bind(&NavigationServer::handle_goal, this, _1, _2),
    std::bind(&NavigationServer::handle_cancel, this, _1),
    std::bind(&NavigationServer::handle_accepted, this, _1));
    
  RCLCPP_INFO(this->get_logger(), "Navigation Action Server Component Initialized.");
}

rclcpp_action::GoalResponse NavigationServer::handle_goal(
  const rclcpp_action::GoalUUID & uuid,
  std::shared_ptr<const NavigateRobot::Goal> goal)
{
  RCLCPP_INFO(this->get_logger(), "Received goal request: x=%.2f, y=%.2f", goal->x, goal->y);
  (void)uuid;
  // Accept all goals for this assignment
  return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
}

rclcpp_action::CancelResponse NavigationServer::handle_cancel(
  const std::shared_ptr<GoalHandleNavigateRobot> goal_handle)
{
  RCLCPP_INFO(this->get_logger(), "Received request to cancel goal. Processing...");
  (void)goal_handle;
  // Accept cancellation requests to prevent infinite execution
  return rclcpp_action::CancelResponse::ACCEPT;
}

void NavigationServer::handle_accepted(const std::shared_ptr<GoalHandleNavigateRobot> goal_handle)
{
  // Execution starts from here. 
  // We use a separate thread to avoid blocking the executor.
  std::thread{std::bind(&NavigationServer::execute, this, std::placeholders::_1), goal_handle}.detach();
}

void NavigationServer::execute(const std::shared_ptr<GoalHandleNavigateRobot> goal_handle)
{
  RCLCPP_INFO(this->get_logger(), "Executing navigation task...");
  rclcpp::Rate loop_rate(10); // 10 Hz control loop
  
  const auto goal = goal_handle->get_goal();
  auto feedback = std::make_shared<NavigateRobot::Feedback>();
  auto result = std::make_shared<NavigateRobot::Result>();
  auto twist_msg = geometry_msgs::msg::Twist();

  double distance_to_goal = std::hypot(goal->x - current_x_, goal->y - current_y_);

  // Control loop runs until the robot is close enough to the target (0.1 meters)
  while (rclcpp::ok() && distance_to_goal > 0.1) {
    
    // Check if the client requested a cancellation during execution
    if (goal_handle->is_canceling()) {
      twist_msg.linear.x = 0.0;
      twist_msg.angular.z = 0.0;
      cmd_vel_pub_->publish(twist_msg); // Stop the robot
      
      result->success = false;
      goal_handle->canceled(result);
      RCLCPP_INFO(this->get_logger(), "Goal canceled successfully. Robot stopped.");
      return;
    }

    // Update distance
    distance_to_goal = std::hypot(goal->x - current_x_, goal->y - current_y_);
    
    // Calculate heading error to align robot towards the goal
    double angle_to_goal = std::atan2(goal->y - current_y_, goal->x - current_x_);
    double angle_error = angle_to_goal - current_theta_;

    // Normalize the angle error to be within [-pi, pi]
    while (angle_error > M_PI) angle_error -= 2.0 * M_PI;
    while (angle_error < -M_PI) angle_error += 2.0 * M_PI;

    // Simple Proportional (P) controller for velocity
    twist_msg.linear.x = 0.5 * distance_to_goal;
    if (twist_msg.linear.x > 0.5) twist_msg.linear.x = 0.5; // Velocity saturation
    
    twist_msg.angular.z = 1.0 * angle_error;
    if (twist_msg.angular.z > 1.0) twist_msg.angular.z = 1.0;
    if (twist_msg.angular.z < -1.0) twist_msg.angular.z = -1.0;

    cmd_vel_pub_->publish(twist_msg);

    // Publish continuous feedback to the client
    feedback->distance_remaining = distance_to_goal;
    goal_handle->publish_feedback(feedback);

    loop_rate.sleep();
  }

  // Goal reached successfully
  if (rclcpp::ok()) {
    twist_msg.linear.x = 0.0;
    twist_msg.angular.z = 0.0;
    cmd_vel_pub_->publish(twist_msg); // Stop the robot
    
    result->success = true;
    goal_handle->succeed(result);
    RCLCPP_INFO(this->get_logger(), "Goal succeeded! Robot reached the target.");
  }
}

void NavigationServer::odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
{
  current_x_ = msg->pose.pose.position.x;
  current_y_ = msg->pose.pose.position.y;
  
  // Convert Quaternion to Euler (Yaw/Theta) for 2D plane navigation
  double q_x = msg->pose.pose.orientation.x;
  double q_y = msg->pose.pose.orientation.y;
  double q_z = msg->pose.pose.orientation.z;
  double q_w = msg->pose.pose.orientation.w;
  
  double siny_cosp = 2.0 * (q_w * q_z + q_x * q_y);
  double cosy_cosp = 1.0 - 2.0 * (q_y * q_y + q_z * q_z);
  current_theta_ = std::atan2(siny_cosp, cosy_cosp);
}

}  // namespace nav_components

// Register the class as a component plug-in
RCLCPP_COMPONENTS_REGISTER_NODE(nav_components::NavigationServer)