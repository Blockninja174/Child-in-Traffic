import os
import sys
import time
import psutil
import subprocess

processes = psutil.process_iter()

def get_Game():
    for process in processes:
        if process.name() == "DodgingTraffic.py":
            return process
    return None
    
while True:
    if get_Game() == None:
        subprocess.call(["python.exe", "DodgingTraffic.py"])
        time.sleep(.5)
    