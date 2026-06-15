"""실차 벤치 (휠 공중) — 진짜 VESC 로 전류제어 테스트.

vesc_driver(시리얼) + speed_pid_to_current 만 띄운다. ackermann_to_vesc(속도→eRPM,
충돌) / fake_vesc 는 안 띄움. 조작은 bench_gui 로.

  터미널1:  ros2 launch vesc_current_control bench_real.launch.py
  터미널2:  ros2 run   vesc_current_control bench_gui

⚠️ 안전 / 미확인 (실차 처음 전원인가 전 반드시 확인):
  - **바퀴를 들고(휠 공중)** 시작. CURRENT 모드 +2A 로 회전 방향부터 확인.
  - 게인/전류 기본값은 일부러 보수적(작게). GUI 로 올려가며 튜닝.
  - 회생제동(음전류)을 실제 모터까지 보내려면 vesc_driver 의 current_min 이
    음수여야 함 → 여기서 driver_current_min 인자로 override (기본 vesc_config 는 0).
  - 이 launch 는 HW 없이 검증 못함 → 차에서 처음 돌릴 때 토픽/거동 확인할 것.

인자(override 예): ros2 launch ... bench_real.launch.py kp:=3.0 pid_current_max:=10.0
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    vesc_config = LaunchConfiguration('vesc_config')
    drv_imin = LaunchConfiguration('driver_current_min')
    drv_imax = LaunchConfiguration('driver_current_max')
    pid_imax = LaunchConfiguration('pid_current_max')
    pid_imin = LaunchConfiguration('pid_current_min')
    gain = LaunchConfiguration('speed_to_erpm_gain')
    kp = LaunchConfiguration('kp')
    ki = LaunchConfiguration('ki')
    kd = LaunchConfiguration('kd')

    return LaunchDescription([
        # vesc_config: 시리얼 포트/servo/gain 등 실차 파라미터 (스택의 vesc_config.yaml)
        DeclareLaunchArgument(
            'vesc_config',
            default_value=PathJoinSubstitution([
                FindPackageShare('vesc_driver_mac'), 'config', 'vesc_config.yaml']),
            description='실차 vesc_config.yaml 경로 (포트/servo/gain).'),
        # 드라이버 전류 한계 — 회생 위해 min 음수. 처음엔 보수적으로.
        DeclareLaunchArgument('driver_current_min', default_value='-15.0',
                              description='vesc_driver current_min [A]. 음수=회생 허용.'),
        DeclareLaunchArgument('driver_current_max', default_value='30.0',
                              description='vesc_driver current_max [A].'),
        # PID 노드 출력 전류 한계 (드라이버 한계 안쪽)
        DeclareLaunchArgument('pid_current_max', default_value='12.0'),
        DeclareLaunchArgument('pid_current_min', default_value='-8.0'),
        DeclareLaunchArgument('speed_to_erpm_gain', default_value='3423.0'),
        # 보수적 시작 게인 (fake plant 의 28/55 와 무관 — 실차는 낮게 시작해 올림)
        DeclareLaunchArgument('kp', default_value='3.0'),
        DeclareLaunchArgument('ki', default_value='6.0'),
        DeclareLaunchArgument('kd', default_value='0.0'),

        # ── 진짜 VESC 드라이버 (시리얼). current_min/max override 로 회생 허용 ──
        Node(
            package='vesc_driver', executable='vesc_driver_node',
            name='vesc_driver_node', output='screen',
            parameters=[vesc_config, {
                'current_min': drv_imin,
                'current_max': drv_imax,
            }],
        ),
        # ── 우리 속도 PID → 전류 노드 ──
        Node(
            package='vesc_current_control', executable='speed_pid_to_current',
            name='speed_pid_to_current_node', output='screen',
            parameters=[{
                'kp': kp, 'ki': ki, 'kd': kd,
                'current_max': pid_imax, 'current_min': pid_imin,
                'speed_to_erpm_gain': gain,
                'speed_sign': -1.0,
                'current_sign': 1.0,   # ★ 벤치에서 방향 확인 후 필요시 -1.0
                # servo 변환 (vesc_config 와 동일값)
                'steering_angle_to_servo_gain': 0.5135,
                'steering_angle_to_servo_offset': 0.445,
                'servo_max': 0.85, 'servo_min': 0.15,
            }],
        ),
    ])
