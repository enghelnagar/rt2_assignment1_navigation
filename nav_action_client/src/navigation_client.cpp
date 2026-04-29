#include "nav_action_client/navigation_client.hpp"
#include <rclcpp_components/register_node_macro.hpp>
#include <iostream>

namespace nav_components
{

NavigationClient::NavigationClient(const rclcpp::NodeOptions & options)
: Node("navigation_client", options), running_(true)
{
  // 1. Initialize the action client
  client_ptr_ = rclcpp_action::create_client<NavigateRobot>(this, "navigate_robot");

  // 2. Start the User Interface in a separate thread to avoid blocking ROS2 callbacks
  ui_thread_ = std::thread(&NavigationClient::ui_loop, this);
  
  RCLCPP_INFO(this->get_logger(), "Navigation Action Client Component Initialized.");
  RCLCPP_INFO(this->get_logger(), "UI Thread started. Waiting for commands...");
}

NavigationClient::~NavigationClient()
{
  running_ = false;
  if (ui_thread_.joinable()) {
    ui_thread_.join();
  }
}

void NavigationClient::ui_loop()
{
  while (running_ && rclcpp::ok()) {
    std::cout << "\n--- Robot Navigation Menu ---\n";
    std::cout << "1. Send a new goal (x, y, theta)\n";
    std::cout << "2. Cancel the current goal\n";
    std::cout << "Enter your choice (1 or 2): ";
    
    int choice;
    if (!(std::cin >> choice)) {
      std::cin.clear();
      std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
      continue;
    }

    if (choice == 1) {
      double x, y, theta;
      std::cout << "Enter X: ";
      std::cin >> x;
      std::cout << "Enter Y: ";
      std::cin >> y;
      std::cout << "Enter Theta (radians): ";
      std::cin >> theta;
      
      send_goal(x, y, theta);
    } 
    else if (choice == 2) {
      cancel_goal();
    } 
    else {
      std::cout << "Invalid choice. Please try again.\n";
    }
  }
}

void NavigationClient::send_goal(double x, double y, double theta)
{
  using namespace std::placeholders;

  if (!client_ptr_->wait_for_action_server(std::chrono::seconds(5))) {
    RCLCPP_ERROR(this->get_logger(), "Action server not available after waiting");
    return;
  }

  auto goal_msg = NavigateRobot::Goal();
  goal_msg.x = x;
  goal_msg.y = y;
  goal_msg.theta = theta;

  RCLCPP_INFO(this->get_logger(), "Sending goal: x=%.2f, y=%.2f, theta=%.2f", x, y, theta);

  auto send_goal_options = rclcpp_action::Client<NavigateRobot>::SendGoalOptions();
  
  send_goal_options.goal_response_callback =
    std::bind(&NavigationClient::goal_response_callback, this, _1);
    
  send_goal_options.feedback_callback =
    std::bind(&NavigationClient::feedback_callback, this, _1, _2);
    
  send_goal_options.result_callback =
    std::bind(&NavigationClient::result_callback, this, _1);

  // Send the goal asynchronously
  client_ptr_->async_send_goal(goal_msg, send_goal_options);
}

void NavigationClient::cancel_goal()
{
  if (!current_goal_handle_) {
    RCLCPP_WARN(this->get_logger(), "No active goal to cancel.");
    return;
  }
  
  RCLCPP_INFO(this->get_logger(), "Sending cancel request to the server...");
  client_ptr_->async_cancel_goal(current_goal_handle_);
}

void NavigationClient::goal_response_callback(const GoalHandleNavigateRobot::SharedPtr & goal_handle)
{
  if (!goal_handle) {
    RCLCPP_ERROR(this->get_logger(), "Goal was rejected by server");
    current_goal_handle_ = nullptr;
  } else {
    RCLCPP_INFO(this->get_logger(), "Goal accepted by server, waiting for result");
    current_goal_handle_ = goal_handle;
  }
}

void NavigationClient::feedback_callback(
  GoalHandleNavigateRobot::SharedPtr,
  const std::shared_ptr<const NavigateRobot::Feedback> feedback)
{
  RCLCPP_INFO(this->get_logger(), "Feedback received: Distance remaining = %.2f meters", 
    feedback->distance_remaining);
}

void NavigationClient::result_callback(const GoalHandleNavigateRobot::WrappedResult & result)
{
  current_goal_handle_ = nullptr;
  switch (result.code) {
    case rclcpp_action::ResultCode::SUCCEEDED:
      RCLCPP_INFO(this->get_logger(), "Goal succeeded!");
      break;
    case rclcpp_action::ResultCode::ABORTED:
      RCLCPP_ERROR(this->get_logger(), "Goal was aborted");
      break;
    case rclcpp_action::ResultCode::CANCELED:
      RCLCPP_WARN(this->get_logger(), "Goal was canceled");
      break;
    default:
      RCLCPP_ERROR(this->get_logger(), "Unknown result code");
      break;
  }
}

}  // namespace nav_components

// Register the class as a component plug-in
RCLCPP_COMPONENTS_REGISTER_NODE(nav_components::NavigationClient)