import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

def generate_launch_description():
    """
    Launch file to load both the Navigation Server and Navigation Client
    into the same Component Container as required by the assignment.
    """
    container = ComposableNodeContainer(
        name='navigation_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        prefix=['xterm', ' -e'],
        composable_node_descriptions=[
            # 1. Load the Action Server Component
            ComposableNode(
                package='nav_action_server',
                plugin='nav_components::NavigationServer',
                name='navigation_server_node'
            ),
            # 2. Load the Action Client (UI) Component
            ComposableNode(
                package='nav_action_client',
                plugin='nav_components::NavigationClient',
                name='navigation_client_node'
            )
        ],
        output='screen',
    )

    return launch.LaunchDescription([container])