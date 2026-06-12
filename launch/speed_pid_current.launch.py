"""속도 PID → 전류 제어 변환 노드 단독 launch.

ackermann_to_vesc_node(속도→eRPM) 대신 띄움. vesc_driver / vesc_to_odom /
simple_mux 등 나머지는 기존 low_level_mac 그대로 사용.

사용:
  # ackermann_to_vesc 끄고 이걸 띄우려면 low_level_mac 에서 ackermann_to_vesc
  # 노드만 빼거나, 아래 launch 를 별도로 실행 (토픽이 같아 동시 실행 금지!)
  ros2 launch vesc_current_control speed_pid_current.launch.py

주의: ackermann_to_vesc_node 와 동시에 띄우면 /commands/motor/speed 와
/commands/motor/current 가 둘 다 나가 VESC 거동이 충돌합니다. 반드시 택일.
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    cfg = LaunchConfiguration('pid_config')
    return LaunchDescription([
        DeclareLaunchArgument(
            'pid_config',
            default_value=PathJoinSubstitution([
                FindPackageShare('vesc_current_control'), 'config', 'speed_pid.yaml',
            ]),
            description='Speed-PID-to-current config YAML.',
        ),
        Node(
            package='vesc_current_control',
            executable='speed_pid_to_current',
            name='speed_pid_to_current_node',
            output='screen',
            parameters=[cfg],
        ),
    ])
