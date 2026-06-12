# vesc_current_control

VESC 속도 PID → 전류 변환 노드 + 벤치 테스트 툴 (ROS2 Jazzy).

기존 `ackermann_to_vesc`(속도→eRPM, VESC 내부 RPM PID) 대신, ROS 단에서
목표 속도를 PID로 받아 **전류[A]** 로 변환해 `/commands/motor/current` 로 보낸다.

## 노드 / 실행

| executable | 설명 |
|---|---|
| `speed_pid_to_current` | `/ackermann_cmd`(목표속도) + `/sensors/core`(실측) → 100Hz PID → `/commands/motor/current`. 조향 servo 변환 포함. |
| `bench_gui` | 슬라이더 GUI: 전류/속도(±5 m/s)/조향 + **PID 게인(kp/ki/kd) 라이브 튜닝** + E-STOP + 실시간 텔레메트리. python_qt_binding. 게인 슬라이더는 `speed_pid_to_current_node` 에 파라미터로 즉시 반영(`add_on_set_parameters_callback`). |
| `bench_console` | 동일 기능 터미널 버전. |

```bash
colcon build --packages-select vesc_current_control --symlink-install
source install/setup.bash

ros2 launch vesc_current_control speed_pid_current.launch.py   # PID 노드
ros2 run vesc_current_control bench_gui                        # GUI
```

## 설정 — `config/speed_pid.yaml`

- PID gain (`kp/ki/kd`), 전류 한계(`current_max/min`, 음수=회생제동), `current_sign`(전류부호↔진행방향, 벤치 확인 후 조정), `speed_to_erpm_gain`(기본 3423).

## 의존성

`rclpy`, `std_msgs`, `ackermann_msgs`, `vesc_msgs`, `python_qt_binding`.
HW(serial/vesc_driver) 의존 없음 — 어디서나 빌드/테스트 가능.

## 실차 미확인 사항

- `current_sign`: 결선 의존. 벤치에서 `bench_gui` CURRENT 모드 `+2A` 로 전진 방향 확인 후 필요시 `-1.0`.
- `vesc_config.yaml` 의 driver `current_min` 이 0 이면 음전류(회생제동) 잘림 → 음수로 풀어야 함.
- PID gain 실차 튜닝 필요.
