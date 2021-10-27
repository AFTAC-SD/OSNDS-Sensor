import psutil
import time
while 1:
    print(psutil.virtual_memory().percent)
    time.sleep(60)