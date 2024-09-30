from pynput.keyboard import KeyCode
import ctypes
import math
from pynput.mouse import Controller as MController


# Ensure that the mouse coordinates are within the screen boundaries
def check_x_y(x, y):
    max_x = ctypes.windll.user32.GetSystemMetrics(0)
    max_y = ctypes.windll.user32.GetSystemMetrics(1)
    x = max(0, min(x, max_x))
    y = max(0, min(y, max_y))

    return x, y


# Handle key press events for stopping an operation queue based on a key combination
def on_key_press_stop_queue(key, stop_flag, current_combination, stop_combination):
    if isinstance(key, KeyCode):
        key = key.vk
    if key in stop_combination and key not in current_combination:
        current_combination.add(key)
        if stop_combination.issubset(current_combination):
            stop_flag[0] = True


# Handle key release events by removing the key from the current combination
def on_key_release_stop_queue(key, current_combination):
    if isinstance(key, KeyCode):
        key = key.vk
    if key in current_combination:
        try:
            current_combination.remove(key)
        except KeyError:
            pass


# Record mouse movement
def on_move_get_coordinates(x, y, state, recorded_mouse_movement):
    if state[0]:
        x, y = check_x_y(x, y)
        if len(recorded_mouse_movement) == 0 or math.sqrt((recorded_mouse_movement[-1][0] - x) ** 2 + (recorded_mouse_movement[-1][1] - y) ** 2) > 6:
            recorded_mouse_movement.append((x, y))


# Toggle the recording state when a key is pressed
def on_key_press_recording(key, state):
    state[0] = not state[0]
    if not state[0]:
        print("Stopped recording.")
        return False
    else:
        print("Started recording.")


# Capture and print the current mouse coordinates when a key is pressed
def on_key_press_get_coordinates(position):
    mouse = MController()
    x, y = check_x_y(*mouse.position)
    print(x, y)
    position.append((x, y))
    return False


# Record the pressed key and add it to the keys list
def on_key_press_get_key(key, keys):
    keys.append(key)
    return False


# Append keys to a hotkey list until the desired number of keys has been recorded
def on_key_press_append_key_to_hotkey(key, hotkey, number):
    print(key)
    hotkey.append(key)
    if len(hotkey) == number:
        return False


# Record mouse movements as actions
def on_move_append_action(x, y, state, recorded_actions):
    if state[0]:
        x, y = check_x_y(x, y)
        last_coordinates = None
        for action in reversed(recorded_actions):
            if action[0] == "m":
                last_coordinates = action[1]
                break

        if last_coordinates is None or math.sqrt((last_coordinates[0] - x)**2 + (last_coordinates[1] - y)**2) > 6:
            recorded_actions.append(("m", (x, y)))


# Record mouse click actions (pressed or released)
def on_click_append_action(x, y, button, pressed, state, recorded_actions):
    if state[0]:
        action = "p" if pressed else "r"
        recorded_actions.append((action, button))
