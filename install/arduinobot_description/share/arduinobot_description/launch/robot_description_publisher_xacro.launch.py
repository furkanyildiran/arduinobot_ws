import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
import xacro


def generate_launch_description():

    pkg_ros_gz_sim_demos = get_package_share_directory('arduinobot_description')
    
    # Parse robot description from xacro
    robot_description_file = os.path.join(pkg_ros_gz_sim_demos, 'urdf', 'rrbot.xacro')
    robot_description_config = xacro.process_file(
        robot_description_file
    )
    robot_desc = {'robot_description': robot_description_config.toxml()}

    # Robot state publisher
    params = {'use_sim_time': True, 'robot_description': robot_desc}
    robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
     #        output='screen',
	    output='both',  #sil
            parameters=[robot_desc],
            )

    # Gazebo Sim
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # RViz
    pkg_ros_gz_sim_demos = get_package_share_directory('arduinobot_description')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=[
            '-d',
            os.path.join(pkg_ros_gz_sim_demos, 'rviz', 'joint_states.rviz')
        ]
    )

    # Spawn
    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
                    '-name', 'rrbot',
                    '-x', '1.2',
                    '-z', '2.3',
                    '-y', '3.4',
                    '-topic', 'robot_description'],
                 output='screen')
                 
    # Gz - ROS Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Clock (IGN -> ROS2)
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Joint states (IGN -> ROS2)
            '/world/empty/model/rrbot/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        remappings=[
            ('/world/empty/model/rrbot/joint_state', 'joint_states'),
        ],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo,
        spawn,
        bridge,
        robot_state_publisher,
        rviz,
  
    ])
