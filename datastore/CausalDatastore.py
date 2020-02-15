import threading
import time
import logging
import concurrent.futures

class CausalDataStore:
    def __init__(self):
        # keeps some key value in the memory
        self.value_dic = {}
        # keeps keys of the values needed to be stored in the database
        self.updatedKey = list()
        self.lock = threading.Lock()

    def locked_load_value(self, name):
        # todo: load value from database to self.value_dict
        # password: password
        pass

    def locked_store_to_db(self):
        pass

    def write(self, name, value):
        logging.info("Thread Ts: starting write", name)
        self.value_dic[name] = value

    def locked_write(self, name, value):
        # write value for a key
        logging.info("Thread %s: starting update", name)
        with self.lock:
            self.value_dic[name] = value


    def locked_read(self, name):
        with self.lock:
            return self.value_dic[name]

    def read(self, name):
        with self.lock:
            return self.value_dic[name]



def thread_function1(name):
    logging.info("Thread %s: starting", name)
    for i in range(100000):
        #datastore.locked_update("x", 1)
        datastore.lock.acquire()
        datastore.write("x", 1)
        datastore.lock.release()
    logging.info("Thread %s: finishing", name)


def thread_function2(name):
    logging.info("Thread %s: starting", name)
    for i in range(100000):
        #datastore.locked_update("x", -1)
        datastore.lock.acquire()
        datastore.write("x", -1)
        datastore.lock.release()
    logging.info("Thread %s: finishing", name)


if __name__ == "__main__":
    format = '%(asctime)s: %(message)s'
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    datastore = CausalDataStore()
    datastore.locked_write("x", 1)

    threads = list()
    for index in range(2):
        logging.info("Main: create and start thread %d.", index)
        x = threading.Thread(target=thread_function1, args=(index,))
        threads.append(x)
        x.start()

    for index in range(2,4,1):
        logging.info("Main: create and start thread %d.", index)
        x = threading.Thread(target=thread_function2, args=(index,))
        threads.append(x)
        x.start()

    for index, thread in enumerate(threads):
        logging.info("Main: before joining thread %d.", index)
        thread.join()
        logging.info("Main: thread %d done", index)
    print(datastore.value_dic["x"])
