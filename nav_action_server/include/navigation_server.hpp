#ifndef NAV_ACTION_SERVER__NAVIGATION_SERVER_HPP_
#define NAV_ACTION_SERVER__NAVIGATION_SERVER_HPP_

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "nav_action_interfaces/action/navigate_robot.hpp"

// Using a namespace is best practice for components to avoid conflicts
namespace nav_components
{

class NavigationServer : public rclcpp::Node
{
public:
  using NavigateRobot = nav_action_interfaces::action::NavigateRobot;
  using GoalHandleNavigateRobot = rclcpp_action::ServerGoalHandle<NavigateRobot>;

  // Constructor must take NodeOptions to be dynamically loaded as a component
  explicit NavigationServer(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());

private:
  // Action server to handle navigation goals
  rclcpp_action::Server<NavigateRobot>::SharedPtr action_server_;

  // Publisher for robot velocity (cmd_vel)
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;

  // Subscriber for robot position (odom)
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;

  // Callbacks required for the action server operations
  rclcpp_action::GoalResponse handle_goal(
    const rclcpp_action::GoalUUID & uuid,
    std::shared_ptr<const NavigateRobot::Goal> goal);

  rclcpp_action::CancelResponse handle_cancel(
    const std::shared_ptr<GoalHandleNavigateRobot> goal_handle);

  void handle_accepted(const std::shared_ptr<GoalHandleNavigateRobot> goal_handle);

  void execute(const std::shared_ptr<GoalHandleNavigateRobot> goal_handle);

  // Callback to update current robot position
  void odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg);

  // Variables to store current robot pose
  double current_x_;
  double current_y_;
  double current_theta_;
};

}  // namespace nav_components

#endif  // NAV_ACTION_SERVER__NAVIGATION_SERVER_HPP_