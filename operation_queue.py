import os
import time
import msvcrt
import operations
import copy
from pynput.keyboard import Key, KeyCode
import json
from pynput.mouse import Button
from utils import on_key_press_stop_queue, on_key_release_stop_queue,on_key_press_append_key_to_hotkey
from pynput.keyboard import Listener as KListener


class OperationQueue:
    # Initialize the operation queue and define default stop key combination
    def __init__(self):
        self.__queue = []
        self.__stop_combination = {Key.ctrl_l, Key.alt_l, 88}

    # Print the current operation queue
    def print_queue(self):
        os.system('cls')
        if len(self.__queue) != 0:
            print("Queue: ")
            for i in range(0, len(self.__queue)):
                print(f" {i}. {self.__queue[i]}")
            print()
        else:
            print("Queue is empty!\n")

    # Add an operation to the end of the queue and print the updated queue
    def append_operation(self, operation):
        self.__queue.append(operation)
        self.print_queue()

    # Check the queue for invalid operations
    def __check_queue(self):
        currently_pressed_keys = set()
        currently_pressed_keys_by_bot = set()

        for operation in self.__queue:
            if operation.get_name() == "PressKey":
                if isinstance(operation.get_key(), Key):
                    key = operation.get_key()
                else:
                    key = operation.get_key().vk
                currently_pressed_keys.add(key)
            elif operation.get_name() == "ReleaseKey":
                if isinstance(operation.get_key(), Key):
                    key = operation.get_key()
                else:
                    key = operation.get_key().vk
                if key in currently_pressed_keys:
                    currently_pressed_keys.remove(key)
            elif operation.get_name() == "UseHotkey":
                for key in operation.get_keys():
                    if isinstance(key, KeyCode):
                        key = key.vk
                    if key not in currently_pressed_keys:
                        currently_pressed_keys_by_bot.add(key)
                        currently_pressed_keys.add(key)
            elif operation.get_name() == "ClickKey":
                if isinstance(operation.get_key(), Key):
                    key = operation.get_key()
                else:
                    key = operation.get_key().vk
                if key not in currently_pressed_keys:
                    currently_pressed_keys_by_bot.add(key)
                    currently_pressed_keys.add(key)

            if all(k in currently_pressed_keys for k in self.__stop_combination):
                return False

            if len(currently_pressed_keys_by_bot) != 0:
                for key in currently_pressed_keys_by_bot:
                    currently_pressed_keys.remove(key)
            currently_pressed_keys_by_bot.clear()

        return True

    # Run all operations in the queue and monitor for stop combination
    def run(self, mouse, keyboard):
        if len(self.__queue) != 0:
            if self.__check_queue():
                stop_execution = [False]
                currently_pressed = set()
                currently_pressed_by_bot = set()
                print("Start of queue execution. Press CTRL_L+ALT_L+X (or changed combination) to stop execution.")
                with KListener(on_press=lambda key: on_key_press_stop_queue(key, stop_execution, currently_pressed, self.__stop_combination), on_release=lambda key: on_key_release_stop_queue(key, currently_pressed)) as listener:
                    for operation in self.__queue:
                        if stop_execution[0]:
                            print("Execution stopped!\n")
                            break

                        time.sleep(0.1)
                        print(f' {operation}')
                        operation.execute(mouse, keyboard)

                        if operation.get_name() == "PressKey":
                            if isinstance(operation.get_key(), Key):
                                key = operation.get_key()
                            else:
                                key = operation.get_key().vk
                            currently_pressed_by_bot.add(key)
                        elif operation.get_name() == "ReleaseKey":
                            if isinstance(operation.get_key(), Key):
                                key = operation.get_key()
                            else:
                                key = operation.get_key().vk
                            if key in currently_pressed_by_bot:
                                currently_pressed_by_bot.remove(key)
                        elif operation.get_name() == "PressMouse":
                            currently_pressed_by_bot.add(operation.get_button())
                        elif operation.get_name() == "ReleaseMouse":
                            if operation.get_button() in currently_pressed_by_bot:
                                currently_pressed_by_bot.remove(operation.get_button())
                    else:
                        print("Execution finished!\n")

                    for action in currently_pressed_by_bot:
                        if isinstance(action, int):
                            keyboard.release(KeyCode.from_vk(action))
                        elif isinstance(action, Key):
                            keyboard.release(action)
                        elif isinstance(action, Button):
                            mouse.release(action)
            else:
                print("Your queue is invalid. Don't use key combination that can stop execution of queue.\n")
        else:
            print("Queue is empty!\n")

    # Remove an operation from the queue by its index
    def remove_operation(self):
        if len(self.__queue) == 0:
            print("Queue is empty!\n")
        else:
            self.print_queue()
            index = ''
            while not index.isdigit() or not (0 <= int(index) < len(self.__queue)):
                index = input("Enter index of operation which you want to remove: ")
            self.__queue.pop(int(index))
            self.print_queue()

    # Move an operation to a different position in the queue
    def move_operation(self):
        if len(self.__queue) == 0 or len(self.__queue) == 1:
            print("Queue is empty or has only 1 operation!\n")
        else:
            self.print_queue()
            index1 = ''
            while not index1.isdigit() or not (0 <= int(index1) < len(self.__queue)):
                index1 = input("Enter index of operation which you want to move: ")
            index2 = ''
            while not index2.isdigit() or not (0 <= int(index2) <= len(self.__queue)):
                index2 = input("Enter index of operation in which place you want to move selected operation: ")
            if index1 != index2:
                cp = copy.deepcopy(self.__queue[int(index1)])
                self.__queue.pop(int(index1))
                self.__queue.insert(int(index2), cp)
                self.print_queue()
            else:
                os.system('cls')
                print("Nothing has changed, indexes were the same!\n")

    # Clear the operation queue
    def clear_queue(self):
        self.__queue.clear()
        self.print_queue()

    # Insert an operation at a specific index in the queue
    def insert_operation(self, operation):
        self.print_queue()
        index = ''
        while msvcrt.kbhit():
            msvcrt.getch()
        while not index.isdigit() or not (0 <= int(index) <= len(self.__queue)):
            index = input("Enter index on which you want to insert operation: ")
        self.__queue.insert(int(index), operation)
        self.print_queue()

    # Copy an existing operation in the queue
    def copy_operation(self):
        if len(self.__queue) == 0:
            print("Queue is empty!\n")
        else:
            self.print_queue()
            index = ''
            while not index.isdigit() or not (0 <= int(index) < len(self.__queue)):
                index = input("Enter index of operation which you want to copy: ")
            cp = copy.deepcopy(self.__queue[int(index)])
            self.insert_operation(cp)

    # Save the queue to a JSON file
    def write_queue_to_file(self):
        serialized_queue = []

        if len(self.__queue) == 0:
            print("Queue is empty!\n")
        else:
            for obj in self.__queue:
                serialized_queue.append(obj.get_dict())

            file = input("Enter name of file (without extension): ")
            file += ".json"
            try:
                with open(file, 'w') as json_file:
                    json.dump(serialized_queue, json_file, indent=4)
                print(f'Saved queue to {file} file.\n')
            except Exception as error:
                print(f'Problem with the file while saving. {type(error).__name__}: {error}\n')

    # Load a queue from a JSON file
    def read_queue_from_file(self):
        file = input("Enter the file name (without extension): ") + ".json"
        new_queue = []

        try:
            with open(file, 'r') as json_file:
                loaded_queue = json.load(json_file)
        except Exception as error:
            print(f"Error reading file: {type(error).__name__}: {error}")
            return

        try:
            for obj in loaded_queue:
                operation_type = obj["type"]
                if operation_type in ["Pause", "MoveMouseToPoint", "TypeText"]:
                    args = {k: v for k, v in obj.items() if k != "type"}
                    new_queue.append(getattr(operations, operation_type)(*args.values()))
                elif operation_type == "ReplicateMouseMovement":
                    positions = [tuple(pos) for pos in obj["positions"]]
                    new_queue.append(operations.ReplicateMouseMovement(positions))
                elif operation_type == "ReplicateMouseActions":
                    actions = [(a[0], tuple(a[1]) if a[0] == 'm' else getattr(Button, a[1][7:])) for a in
                               obj["actions"]]
                    new_queue.append(operations.ReplicateMouseActions(actions))
                elif operation_type == "ClickMouse":
                    new_queue.append(
                        operations.ClickMouse(obj["x"], obj["y"], getattr(Button, obj["button"][7:]), obj["clicks"]))
                elif operation_type in ["PressMouse", "ReleaseMouse"]:
                    new_queue.append(getattr(operations, operation_type)(getattr(Button, obj["button"][7:])))
                elif operation_type in ["ClickKey", "PressKey", "ReleaseKey"]:
                    key = getattr(Key, obj["key"][4:]) if obj["key"].startswith("Key.") else KeyCode.from_vk(obj["key"])
                    new_queue.append(getattr(operations, operation_type)(key))
                elif operation_type == "UseHotkey":
                    keys = [getattr(Key, k[4:]) if isinstance(k, str) and k.startswith("Key.") else KeyCode.from_vk(k)
                            for k in obj["keys"]]
                    new_queue.append(operations.UseHotkey(*keys))
                else:
                    raise ValueError("Unknown operation type.")

            self.__queue.clear()
            self.__queue = new_queue
            print(f"Loaded queue from {file}.")
            self.print_queue()

        except Exception as error:
            print(f"Error in file content: {type(error).__name__}: {error}")

    # Change the key combination used to stop the execution of the queue
    def change_stop_combination(self):
        number = ''
        while not number.isdigit() or not (1 <= int(number) <= 5):
            number = input("Enter number of keys (1, 2, 3, 4, 5): ")

        num = int(number)
        print("Press key:")
        pressed_keys = []

        with KListener(on_press=lambda key: on_key_press_append_key_to_hotkey(key, pressed_keys, num)) as listener:
            listener.join()

        new_combination = []
        for key in pressed_keys:
            if isinstance(key, KeyCode):
                key = key.vk
            new_combination.append(key)
        self.__stop_combination = tuple(new_combination)
        print("The new stop combination saved.\n")
