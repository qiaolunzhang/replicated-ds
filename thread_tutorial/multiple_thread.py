import logging
import threading
import time


def thread_function(name, test_list):
    logging.info("Thread %s: starting", name)
    test_list.append(name)
    time.sleep(0.2)
    logging.info("Thread %s: finishing", name)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format,level=logging.INFO,
                        datefmt="%H:%M:%S")
    threads = list()
    test_list = []
    for index in range(3):
        logging.info("Main: create and start thread %d.", index)
        x = threading.Thread(target=thread_function, args=(index, test_list))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        logging.info("Main: before joining thread %d.", index)
        thread.join()
        logging.info("Main: thread %d done", index)

    time.sleep(5)
    print(test_list)

