cmake_minimum_required(VERSION 3.8)
project(nav_action_server)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies required for the project
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(nav_action_interfaces REQUIRED)

# --- Component Configuration ---

# 1. Add the component as a SHARED library
add_library(navigation_server_component SHARED
  src/navigation_server.cpp
)

# 2. Specify the include directories
target_include_directories(navigation_server_component PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# 3. Link the required dependencies to the library
ament_target_dependencies(navigation_server_component
  "rclcpp"
  "rclcpp_components"
  "rclcpp_action"
  "geometry_msgs"
  "nav_msgs"
  "nav_action_interfaces"
)

# 4. Register the node programmatically as a Plugin
rclcpp_components_register_node(navigation_server_component 
  PLUGIN "nav_components::NavigationServer" 
  EXECUTABLE navigation_server_exe
)

# 5. Export targets so other packages can use this component
ament_export_targets(export_${PROJECT_NAME}_navigation_server_component)

# 6. Install the executable and libraries in the correct paths
install(TARGETS navigation_server_component
  EXPORT export_${PROJECT_NAME}_navigation_server_component
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(DIRECTORY include/
  DESTINATION include
)
# --------------------------------------------------

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Install the launch directory
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)
ament_package()