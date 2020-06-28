import time

start_time = time.time()


def start_timer():
    global start_time
    start_time = time.time()


def end_timer():
    global start_time
    elapsed_time = time.time() - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    return "Time passed: {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
