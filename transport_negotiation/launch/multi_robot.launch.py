from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    robot_ids = ['robot_0', 'robot_1', 'robot_2']

    robot_nodes = [
        Node(
            package='transport_negotiation',
            executable='robot_agent',
            name=rid,
            parameters=[{'robot_id': rid}],
            output= 'screen'
        )
        for rid in robot_ids
    ]
    task_gen_node = Node(
        package='transport_negotiation',
        executable='task_generator',
        name='task_generator',
        output= 'screen'
    )

    return LaunchDescription(robot_nodes + [task_gen_node])