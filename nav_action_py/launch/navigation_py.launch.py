from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='nav_action_py',
            executable='server',
            name='navigation_server_py',
            output='screen'
        )
    ])