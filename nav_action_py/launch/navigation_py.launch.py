from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # run server in backgroungd
        Node(
            package='nav_action_py',
            executable='server',
            name='navigation_server_py',
            output='screen'
        ),
        
        # open xterm 
        Node(
            package='nav_action_py',
            executable='client',
            name='navigation_client_py',
            output='screen',
            prefix=['xterm -e']  
        )
    ])