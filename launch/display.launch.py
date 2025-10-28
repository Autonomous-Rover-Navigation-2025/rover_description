from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue   # <-- ADD THIS
import os


def generate_launch_description():
    pkg_share = FindPackageShare(package='rover_description').find('rover_description')
    default_model_path = os.path.join(pkg_share, 'src', 'description', 'rover_description.urdf')
    default_rviz_config_path = os.path.join(pkg_share, 'rviz', 'config.rviz')
    robot_localization_config = os.path.join(pkg_share, 'config', 'robot_localization.yaml')

    # Build robot_description once so both nodes use the same string
    robot_description = ParameterValue(
        Command(['xacro ', LaunchConfiguration('model')]),  # xacro can handle plain .urdf or .xacro
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}],
        output='screen',
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        parameters=[{'robot_description': robot_description}],  # <-- wrap as string too
        condition=UnlessCondition(LaunchConfiguration('gui')),
        output='screen',
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(LaunchConfiguration('gui')),
        output='screen',
    )

    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[robot_localization_config],
        remappings=[('odometry/filtered', 'odom')],
        # arguments=['--ros-args', '--log-level', 'debug'],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )

    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='True',
            description='Flag to enable joint_state_publisher_gui'),
        DeclareLaunchArgument('model', default_value=default_model_path,
            description='Absolute path to robot model file'),
        DeclareLaunchArgument('rvizconfig', default_value=default_rviz_config_path,
            description='Absolute path to rviz config file'),
        joint_state_publisher_node,
        joint_state_publisher_gui_node,
        robot_state_publisher_node,
        robot_localization_node,
        rviz_node,
    ])
