from pynput.keyboard import KeyCode
import ctypes
import math
from pynput.mouse import Controller as MController


def check_x_y(x, y):
    if x < 0:
        x = 0
    elif x > ctypes.windll.user32.GetSystemMetrics(0):
        x = ctypes.windll.user32.GetSystemMetrics(0)
    if y < 0:
        y = 0
    elif y > ctypes.windll.user32.GetSystemMetrics(1):
        y = ctypes.windll.user32.GetSystemMetrics(1)
    return x, y


def on_key_press_stop_queue(key, stop_flag, current_combination, stop_combination):
    if isinstance(key, KeyCode):
        key = key.vk
    if key in stop_combination and key not in current_combination:
        current_combination.add(key)
        if all(k in current_combination for k in stop_combination):
            stop_flag[0] = True


def on_key_release_stop_queue(key, current_combination):
    if isinstance(key, KeyCode):
        key = key.vk
    if key in current_combination:
        try:
            current_combination.remove(key)
        except KeyError:
            pass


def on_move_get_coordinates(x, y, state, recorded_mouse_movement):
    if state[0]:
        x, y = check_x_y(x, y)

        if len(recorded_mouse_movement) == 0 or math.sqrt((recorded_mouse_movement[-1][0] - x)**2 + (recorded_mouse_movement[-1][1] - y)**2) > 6:
            # print(x, y)
            recorded_mouse_movement.append((x, y))


def on_key_press_recording(key, state):
    state[0] = not state[0]
    if not state[0]:
        print("Stopped recording.")
        return False
    else:
        print("Started recording.")


def on_key_press_get_coordinates(position):
    mouse = MController()
    x, y = check_x_y(*mouse.position)
    print(x, y)
    position.append((x, y))
    return False


def on_key_press_get_key(key, keys):
    keys.append(key)
    return False


def on_key_press_append_key_to_hotkey(key, hotkey, number):
    print(key)
    hotkey.append(key)
    if len(hotkey) == number:
        return False


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


def on_click_append_action(x, y, button, pressed, state, recorded_actions):
    if state[0]:
        action = "p" if pressed else "r"
        recorded_actions.append((action, button))
