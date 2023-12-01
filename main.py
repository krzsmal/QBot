from pynput.mouse import Controller as MController
from pynput.keyboard import Controller as KController
import msvcrt
import os
from constants import TITLE, MAIN_MENU, OPERATIONS
import operations
import operation_queue


if __name__ == '__main__':

    operation_queue = operation_queue.OperationQueue()
    mouse_controller = MController()
    keyboard_controller = KController()

    os.system('cls')
    print(TITLE)
    while True:
        print(MAIN_MENU)
        while msvcrt.kbhit():
            msvcrt.getch()
        option = input(" Select an option: ")
        os.system('cls')

        match option:
            case "1" | "2":
                if option == "1":
                    print("Choose operation to append:")
                else:
                    print("Choose operation to insert:")
                while True:
                    print(OPERATIONS)
                    operation = input(" Select an operation: ")
                    os.system('cls')
                    match operation:
                        case "1":
                            new_operation = operations.Pause.create_from_user_input()
                        case "2":
                            new_operation = operations.MoveMouseToPoint.create_from_user_input()
                        case "3":
                            new_operation = operations.ReplicateMouseMovement.create_from_user_input()
                        case "4":
                            new_operation = operations.ReplicateMouseActions.create_from_user_input()
                        case "5":
                            new_operation = operations.ClickMouse.create_from_user_input()
                        case "6":
                            new_operation = operations.PressMouse.create_from_user_input()
                        case "7":
                            new_operation = operations.ReleaseMouse.create_from_user_input()
                        case "8":
                            new_operation = operations.TypeText.create_from_user_input()
                        case "9":
                            new_operation = operations.ClickKey.create_from_user_input()
                        case "0":
                            new_operation = operations.PressKey.create_from_user_input()
                        case "q":
                            new_operation = operations.ReleaseKey.create_from_user_input()
                        case "w":
                            new_operation = operations.UseHotkey.create_from_user_input()
                        case "e":
                            os.system('cls')
                            print()
                            break
                        case _:
                            os.system('cls')
                            continue
                    if option == "1":
                        operation_queue.append_operation(new_operation)
                    else:
                        operation_queue.insert_operation(new_operation)
                    break
            case "3":
                operation_queue.remove_operation()
            case "4":
                operation_queue.move_operation()
            case "5":
                operation_queue.print_queue()
            case "6":
                operation_queue.run(mouse_controller, keyboard_controller)
            case "7":
                operation_queue.clear_queue()
            case "8":
                operation_queue.copy_operation()
            case "9":
                operation_queue.write_queue_to_file()
            case "0":
                operation_queue.read_queue_from_file()
            case "q":
                operation_queue.change_stop_combination()
            case "e":
                exit()
            case _:
                print()
