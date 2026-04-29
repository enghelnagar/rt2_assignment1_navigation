cmake_minimum_required(VERSION 3.8)
project(nav_action_client)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find required dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(nav_action_interfaces REQUIRED)

# --- Component Configuration ---

# 1. Add the component as a SHARED library
add_library(navigation_client_component SHARED
  src/navigation_client.cpp
)

# 2. Specify the include directories
target_include_directories(navigation_client_component PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

# 3. Link the required dependencies to the library
ament_target_dependencies(navigation_client_component
  "rclcpp"
  "rclcpp_components"
  "rclcpp_action"
  "nav_action_interfaces"
)

# 4. Register the node programmatically as a Plugin
rclcpp_components_register_node(navigation_client_component 
  PLUGIN "nav_components::NavigationClient" 
  EXECUTABLE navigation_client_exe
)

# 5. Export targets so other packages can use this component
ament_export_targets(export_${PROJECT_NAME}_navigation_client_component)

# 6. Install the executable and libraries in the correct paths
install(TARGETS navigation_client_component
  EXPORT export_${PROJECT_NAME}_navigation_client_component
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

ament_package()