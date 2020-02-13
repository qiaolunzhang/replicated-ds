#!/usr/bin/python
"""
https://realpython.com/intro-to-python-threading/
What threads are
How to create threads and wait for them to finish
How to use a ThreadPoolExecutor
How to avoid race conditions
How to use the common tools that Python threading provides
Tasks that spend  much of their time waiting for external events are
generally good candidates for threading. Problems that require heavy
CPU computation and spend little time waiting for external events
might not run faster at all(for python because the interactions with
the GIL
"""
import logging
import threading
import time

def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    #print(format)
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    logging.info("Main    : before creating thread")
    # a daemon thread can be interrupted
    #x = threading.Thread(target=thread_function, args=(1,), daemon=True)
    x = threading.Thread(target=thread_function, args=(1,))
    logging.info("Main    : before running thread")
    x.start()
    logging.info("Main    : wait for the thread to finish")
    # to tell one thread to wait for another thread to finish
    # x.join()
    logging.info("Main    : all done")
