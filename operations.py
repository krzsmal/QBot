from abc import ABC, abstractmethod
import time
import ctypes
from pynput.mouse import Button
from pynput.keyboard import Key, KeyCode
from pynput.keyboard import Listener as KListener
from pynput.mouse import Listener as MListener
from constants import KEY_NAMES
from utils import on_move_get_coordinates, on_key_press_recording, on_key_press_get_coordinates, on_key_press_get_key, on_key_press_append_key_to_hotkey, on_move_append_action, on_click_append_action


class Operation(ABC):
    def get_name(self):
        return self.__class__.__name__

    @abstractmethod
    def get_dict(self):
        pass

    @abstractmethod
    def execute(self, mouse, keyboard):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @classmethod
    @abstractmethod
    def create_from_user_input(cls):
        pass


class Pause(Operation):
    def __init__(self, duration):
        assert isinstance(duration, float), "Pause: duration must be float."
        assert duration > 0, "Pause: duration must be greater than 0."
        self.__duration = duration

    def get_duration(self):
        return self.__duration

    def get_dict(self):
        return {"type": self.get_name(), "duration": self.get_duration()}

    def execute(self, mouse, keyboard):
        time.sleep(self.__duration)

    def __repr__(self):
        return "Pause(" + str(self.__duration) + ")"

    @classmethod
    def create_from_user_input(cls):
        while True:
            duration = input("Enter duration of pause: ")
            if duration == '':
                return cls(float(1))
            else:
                try:
                    duration = float(duration)
                    if duration > 0:
                        return cls(duration)
                    else:
                        print("Duration must be greater than zero.\n")
                except ValueError:
                    print("Duration must be instance of int or float\n.")


class MoveMouseToPoint(Operation):
    def __init__(self, x, y):
        assert isinstance(x, int), "MouseMoveToPoint: x must be int."
        assert isinstance(y, int), "MouseMoveToPoint: x must be int."
        assert 0 <= x <= ctypes.windll.user32.GetSystemMetrics(
            0), "MouseMoveToPoint: x must be between 0 and width of your screen."
        assert 0 <= y <= ctypes.windll.user32.GetSystemMetrics(
            1), "MouseMoveToPoint: y must be between 0 and height of your screen."
        self.__x = x
        self.__y = y

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_dict(self):
        return {"type": self.get_name(), "x": self.get_x(), "y": self.get_y()}

    def execute(self, mouse, keyboard):
        mouse.position = (self.__x, self.__y)

    def __repr__(self):
        return "MoveMouseToPoint(X:" + str(self.__x) + ", Y:" + str(self.__y) + ")"

    @classmethod
    def create_from_user_input(cls):
        print("Press any key to save mouse position:")
        position = []

        with KListener(on_press=lambda key: on_key_press_get_coordinates(position)) as listener:
            listener.join()

        print("Saved position:", position[0])
        return cls(*position[0])


class ReplicateMouseMovement(Operation):
    def __init__(self, positions):
        assert isinstance(positions, list), "Positions must be a list."
        assert all(
            isinstance(item, tuple) and
            isinstance(item[0], int) and
            isinstance(item[1], int) and
            0 <= item[0] <= ctypes.windll.user32.GetSystemMetrics(0) and
            0 <= item[1] <= ctypes.windll.user32.GetSystemMetrics(1)
            for item in positions
        ), "ReplicateMouseMovement: Positions must contain tuples or lists: (x, y) where x is between 0 and width of your screen, and y is between 0 and height of your screen."
        self.__positions = positions

    def get_positions(self):
        return self.__positions

    def get_dict(self):
        return {"type": self.get_name(), "positions": self.get_positions()}

    def execute(self, mouse, keyboard):
        for coordinates in self.__positions:
            mouse.position = coordinates
            time.sleep(0.001)

    def __repr__(self):
        return "ReplicateMouseMovement(POSITIONS:" + str(len(self.__positions)) + ")"

    @classmethod
    def create_from_user_input(cls):
        recorded_mouse_movement = []
        state = [False]

        print("Press any key to start recording, then press any key to stop recording.")
        with MListener(on_move=lambda x, y: on_move_get_coordinates(x, y, state, recorded_mouse_movement)) as listener, KListener(on_press=lambda key: on_key_press_recording(key, state)) as keyboard_listener:
            keyboard_listener.join()

        print(f'Recorded {len(recorded_mouse_movement)} positions.')
        return cls(recorded_mouse_movement)


class ReplicateMouseActions(Operation):
    def __init__(self, actions):
        assert isinstance(actions, list), "ReplicateMouseActions: actions must be a list."
        assert all(
            isinstance(item, tuple) and
            (
                    (
                            item[0] == 'm' and isinstance(item[1], tuple) and
                            isinstance(item[1][0], int) and isinstance(item[1][1], int) and
                            0 <= item[1][0] <= ctypes.windll.user32.GetSystemMetrics(0) and
                            0 <= item[1][1] <= ctypes.windll.user32.GetSystemMetrics(1)
                    ) or
                    (item[0] in ['p', 'r'] and isinstance(item[1], Button))
            )
            for item in actions
        ), "ReplicateMouseActions: actions are invalid."
        self.__actions = actions

    def get_actions(self):
        return self.__actions

    def get_dict(self):
        actions = []
        for action in self.get_actions():
            if action[0] == 'm':
                actions.append(action)
            else:
                actions.append((action[0], str(action[1])))
        return {"type": self.get_name(), "actions": actions}

    def execute(self, mouse, keyboard):
        for action in self.__actions:
            if action[0] == "m":
                mouse.position = action[1]
            elif action[0] == "p":
                mouse.press(action[1])
            elif action[0] == "r":
                mouse.release(action[1])
            time.sleep(0.001)

    def __repr__(self):
        return "ReplicateMouseActions(ACTIONS:" + str(len(self.__actions)) + ")"

    @classmethod
    def create_from_user_input(cls):
        recorded_actions = []
        state = [False]

        print("Press any key to start recording, than press any key to stop recording.")
        with MListener(on_move=lambda x, y: on_move_append_action(x, y, state, recorded_actions), on_click=lambda x, y, button, pressed: on_click_append_action(x, y, button, pressed, state, recorded_actions)) as listener, KListener(
                on_press=lambda key: on_key_press_recording(key, state)) as keyboard_listener:
            keyboard_listener.join()

        buttons_state = {"l": False, "m": False, "r": False}
        for action in recorded_actions:
            btn = None
            match action[1]:
                case Button.left:
                    btn="l"
                case Button.right:
                    btn="r"
                case Button.middle:
                    btn="m"
            if action[0] == "p":
                buttons_state[btn] = True
            else:
                buttons_state[btn] = False
        if buttons_state["l"]:
            recorded_actions.append(('r', Button.left))
        if buttons_state["m"]:
            recorded_actions.append(('r', Button.middle))
        if buttons_state["r"]:
            recorded_actions.append(('r', Button.right))

        print(f'Recorded {len(recorded_actions)} actions.')
        return cls(recorded_actions)


class ClickMouse(Operation):
    def __init__(self, x, y, button, clicks):
        assert isinstance(x, int), "ClickMouse: x must be int."
        assert isinstance(y, int), "ClickMouse: x must be int."
        assert 0 <= x <= ctypes.windll.user32.GetSystemMetrics(
            0), "ClickMouse: x must be between 0 and width of your screen."
        assert 0 <= y <= ctypes.windll.user32.GetSystemMetrics(
            1), "ClickMouse: y must be between 0 and height of your screen."
        assert isinstance(button, Button), "ClickMouse: button must be instance of Button."
        assert isinstance(clicks, int), "ClickMouse: clicks must be int."
        assert 0 < clicks <= 10000, "ClickMouse: clicks must be in range (0, 10000]."
        self.__x = x
        self.__y = y
        self.__button = button
        self.__clicks = clicks

    def get_x(self):
        return self.__x

    def get_y(self):
        return self.__y

    def get_button(self):
        return self.__button

    def get_clicks(self):
        return self.__clicks

    def get_dict(self):
        return {"type": self.get_name(), "x": self.get_x(), "y": self.get_y(), "button": str(self.get_button()), "clicks": self.get_clicks()}

    def execute(self, mouse, keyboard):
        mouse.position = (self.__x, self.__y)
        mouse.click(self.__button, self.__clicks)

    def __repr__(self):
        return "ClickMouse(X:" + str(self.__x) + ", Y:" + str(self.__y) + ", BTN: " + str(
            self.__button) + ", CLICKS: " + str(
            self.__clicks) + ")"

    @classmethod
    def create_from_user_input(cls):
        btn = None
        while btn not in ['L', 'M', 'R', '']:
            btn = input("Enter mouse button (L/M/R): ").upper()
        if btn == 'R':
            btn = Button.right
        elif btn == 'M':
            btn = Button.middle
        else:
            btn = Button.left

        clicks = input("Enter number of clicks: ")
        if clicks == '':
            clicks = 1
        else:
            while not clicks.isdigit() or not (1 <= int(clicks) <= 10000):
                clicks = input("Enter number of clicks: ")
        clicks = int(clicks)

        print("Press any key to save mouse position:")
        position = []

        with KListener(on_press=lambda key: on_key_press_get_coordinates(position)) as listener:
            listener.join()

        print("Saved position:", position[0])
        x, y = position[0]
        return cls(x, y, btn, clicks)


class PrsRlsMouse(Operation):
    def __init__(self, button):
        assert isinstance(button, Button), f"{self.get_name()}: button must be instance of Button."
        self.__button = button

    def get_button(self):
        return self.__button

    def get_dict(self):
        return {"type": self.get_name(), "button": str(self.get_button())}

    @classmethod
    def create_from_user_input(cls):
        btn = None
        while btn not in ['L', 'M', 'R', '']:
            btn = input("Enter mouse button (L/M/R): ").upper()
        if btn == 'R':
            btn = Button.right
        elif btn == 'M':
            btn = Button.middle
        else:
            btn = Button.left
        return cls(btn)

    def __repr__(self):
        return f"{self.get_name()}(" + str(self.__button) + ")"


class PressMouse(PrsRlsMouse):
    def execute(self, mouse, keyboard):
        mouse.press(self.get_button())


class ReleaseMouse(PrsRlsMouse):
    def execute(self, mouse, keyboard):
        mouse.release(self.get_button())


class TypeText(Operation):
    def __init__(self, text):
        assert isinstance(text, str), "TypeText: text must be instance of str."
        self.__text = text

    def get_text(self):
        return self.__text

    def get_dict(self):
        return {"type": self.get_name(), "text": self.get_text()}

    def execute(self, mouse, keyboard):
        try:
            keyboard.type(self.__text)
        except ctypes.ArgumentError:
            print("Operation: TypeText('" + str(
                self.__text) + "') contains illegal characters. You can change or delete this operation.")

    def __repr__(self):
        return "TypeText('" + str(self.__text) + "')"

    @classmethod
    def create_from_user_input(cls):
        text = input("Enter text: ")
        return cls(text)


class KeyOperations(Operation):
    def __init__(self, key):
        assert (isinstance(key, Key) or (isinstance(key, KeyCode) and key.vk in KEY_NAMES.keys())), f"{self.get_name()}: invalid key."
        self.__key = key

    def get_key(self):
        return self.__key

    def get_dict(self):
        if isinstance(self.get_key(), Key):
            return {"type": self.get_name(), "key": str(self.get_key())}
        else:
            return {"type": self.get_name(), "key": self.get_key().vk}

    def __repr__(self):
        if isinstance(self.__key, Key):
            return f"{self.get_name()}(" + str(self.__key) + ")"
        else:
            key_name = KEY_NAMES.get(self.__key.vk, "Unknown key")
            return f"{self.get_name()}(" + str(key_name) + ")"

    @classmethod
    def create_from_user_input(cls):
        print("Press key:")
        keys_pressed = []

        with KListener(on_press=lambda key: on_key_press_get_key(key, keys_pressed)) as listener:
            listener.join()

        print("Registered key:", keys_pressed[0])

        return cls(keys_pressed[0])


class ClickKey(KeyOperations):
    def execute(self, mouse, keyboard):
        keyboard.tap(self.get_key())


class PressKey(KeyOperations):
    def execute(self, mouse, keyboard):
        keyboard.press(self.get_key())


class ReleaseKey(KeyOperations):
    def execute(self, mouse, keyboard):
        keyboard.release(self.get_key())


class UseHotkey(Operation):
    def __init__(self, *args):
        assert (isinstance(args, tuple) and
                2 <= len(args) <= 5 and
                all(
                    isinstance(item, Key) or
                    (isinstance(item, KeyCode) and item.vk in KEY_NAMES.keys())
                    for item in args
                )
                ), "UseHotKey: args must be a tuple of 2, 3, 4 or 5 keys."
        self.__keys = args

    def get_keys(self):
        return self.__keys

    def get_dict(self):
        keys = []
        for key in self.get_keys():
            if isinstance(key, Key):
                keys.append(str(key))
            else:
                keys.append(key.vk)
        return {"type": self.get_name(), "keys": keys}

    def execute(self, mouse, keyboard):
        for key in self.__keys:
            keyboard.press(key)
        for key in self.__keys:
            keyboard.release(key)

    def __repr__(self):
        keys_str = []
        for key in self.__keys:
            if isinstance(key, Key):
                keys_str.append(str(key))
            else:
                key_name = KEY_NAMES.get(key.vk, "Unknown key")
                keys_str.append(str(key_name))
        return "UseHotkey(" + ", ".join(map(str, keys_str)) + ")"

    @classmethod
    def create_from_user_input(cls):
        number = ''
        while not number.isdigit() or not (2 <= int(number) <= 5):
            number = input("Enter number of keys (2, 3, 4, 5): ")

        num = int(number)
        print("Press key:")
        keys_pressed = []

        with KListener(on_press=lambda key: on_key_press_append_key_to_hotkey(key, keys_pressed, num)) as listener:
            listener.join()

        print("Registered keys: " + ", ".join(map(str, keys_pressed)))
        return cls(*keys_pressed)
