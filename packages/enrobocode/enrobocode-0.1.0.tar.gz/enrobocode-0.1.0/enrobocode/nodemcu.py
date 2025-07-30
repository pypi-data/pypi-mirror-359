def move_forward(distance):
    print(f"[NodeMCU] Moving forward {distance} cm")

def move_backward(distance):
    print(f"[NodeMCU] Moving backward {distance} cm")

def turn_left(angle):
    print(f"[NodeMCU] Turning left {angle} degrees")

def turn_right(angle):
    print(f"[NodeMCU] Turning right {angle} degrees")

def stop():
    print("[NodeMCU] Stopping")

def beep():
    print("[NodeMCU] Beep!")

def set_speed(value):
    print(f"[NodeMCU] Setting speed to {value}")

def read_distance():
    print("[NodeMCU] Reading distance...")
    return 42  # Placeholder

def wait(seconds):
    print(f"[NodeMCU] Waiting for {seconds} seconds")

def get_command_wifi(ssid, password):
    print(f"[NodeMCU] Connecting to Wi-Fi network '{ssid}' with password '{password}' and waiting for command...")
    return "example_command_from_wifi"

def get_command_usb(port):
    print(f"[NodeMCU] Listening on USB port '{port}' for command...")
    return "example_command_from_usb"

def balance_upright(kp=1.0, ki=0.0, kd=0.0, target_angle=0.0):
    print("[NodeMCU] Starting upright balancing using PID...")
    print(f"PID constants: kp={kp}, ki={ki}, kd={kd}")
    print(f"Target angle: {target_angle}°")

    current_angle = 10.0  # example start
    error = target_angle - current_angle
    integral = 0.0
    last_error = error

    for _ in range(5):  # simulate 5 balancing steps
        error = target_angle - current_angle
        integral += error
        derivative = error - last_error

        output = kp * error + ki * integral + kd * derivative

        print(f"[NodeMCU] Angle: {current_angle:.2f}°, Error: {error:.2f}, Output: {output:.2f}")

        current_angle -= output * 0.1  # simulate correction
        last_error = error

    print("[NodeMCU] Finished simulation of balancing loop.")
