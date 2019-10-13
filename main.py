from controller.main_controller import MainController
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

if __name__ == '__main__':
    logging.info("Starting __main__.")
    c = MainController()
    c.run()