from сontroller.main_controller import MainController
import sys
import traceback


if __name__ == '__main__':
    try:
        c = MainController()
        sys.exit(c.run())
    except Exception as e:
        print("Exception occured!")
        print(traceback.format_exc())

