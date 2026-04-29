#ifndef NAV_ACTION_CLIENT__NAVIGATION_CLIENT_HPP_
#define NAV_ACTION_CLIENT__NAVIGATION_CLIENT_HPP_

#include "rclcpp/rclcpp.hpp"
#include "rclcpp_action/rclcpp_action.hpp"
#include "nav_action_interfaces/action/navigate_robot.hpp"
#include <thread>
#include <atomic>

namespace nav_components
{

class NavigationClient : public rclcpp::Node
{
public:
  using NavigateRobot = nav_action_interfaces::action::NavigateRobot;
  using GoalHandleNavigateRobot = rclcpp_action::ClientGoalHandle<NavigateRobot>;

  // Constructor must take NodeOptions to act as a ROS2 Component
  explicit NavigationClient(const rclcpp::NodeOptions & options = rclcpp::NodeOptions());
  
  // Destructor to safely join the UI thread
  ~NavigationClient();

private:
  // Action client pointer
  rclcpp_action::Client<NavigateRobot>::SharedPtr client_ptr_;
  
  // Pointer to track the current active goal
  GoalHandleNavigateRobot::SharedPtr current_goal_handle_;

  // Thread and flag for the user interface loop
  std::thread ui_thread_;
  std::atomic<bool> running_;

  // Core functions for user interaction
  void ui_loop();
  void send_goal(double x, double y, double theta);
  void cancel_goal();

  // Callbacks for the action client
  void goal_response_callback(const GoalHandleNavigateRobot::SharedPtr & goal_handle);
  
  void feedback_callback(
    GoalHandleNavigateRobot::SharedPtr,
    const std::shared_ptr<const NavigateRobot::Feedback> feedback);
    
  void result_callback(const GoalHandleNavigateRobot::WrappedResult & result);
};

}  // namespace nav_components

#endif  // NAV_ACTION_CLIENT__NAVIGATION_CLIENT_HPP_