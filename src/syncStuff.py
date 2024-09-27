import threading
import src.network as network

# does a ping every 10 minutes
def my_function():
    network.doPing()

def run_function():
    thread = threading.Timer(10 * 60.0, run_function)
    thread.start()
    my_function()

def do_something():
    run_function() # start the timer