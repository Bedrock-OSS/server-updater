from os import _exit
import threading
import time

def restart():
    def exit():
        time.sleep(0.5)
        _exit(1)
    threading.Thread(target=exit).start()
    return "Processing", 202