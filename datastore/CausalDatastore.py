import threading
import time
import logging
import concurrent.futures

class CausalDataStore:
    def __init__(self):
        # keeps some key value in the memory
        self.value_dic = {}
        # keeps keys of the values needed to be stored in the database
        # stores the changes made by the local client
        self.local_changed_value_dic = {}
        # stores both changes made bby the local client and the replica
        #self.changed_value_dic = {}
        self.lock = threading.Lock()

    def locked_load_value(self, name):
        # todo: load value from database to self.value_dict
        # password: password
        pass

    def locked_store_to_db(self):
        # todo write to database
        pass

    def write(self, name, value):
        #logging.info("Thread Ts: starting write", name)
        self.value_dic[name] = value
        #self.changed_value_dic[name] = value
        self.local_changed_value_dic[name] = value

    def write_from_replica(self, name, value):
        self.value_dic[name] = value
        #self.changed_value_dic[name] = value

    def locked_write(self, name, value):
        # write value for a key
        logging.info("Thread %s: starting update", name)
        with self.lock:
            self.value_dic[name] = value
            #self.changed_value_dic[name] =value
            self.local_changed_value_dic[name] = value

    def locked_write_from_replica(self, name, value):
        with self.lock:
            self.value_dic[name] = value
            #self.changed_value_dic[name] = value

    def locked_read(self, name):
        with self.lock:
            if name in self.value_dic.keys():
                return self.value_dic[name]
            else:
                return ""

    def read(self, name):
        if name in self.value_dic.keys():
            return self.value_dic[name]
        else:
            return ""

    def locked_propagate_to_replica(self):
        with self.lock:
            changed_value_dic = self.changed_value_dic
            #self.changed_value_dic = {}
            self.local_changed_value_dic = {}
            return changed_value_dic

    def check_local_change(self):
        """
        check whether there are changes from local clients
        :return:
        """
        if bool(self.local_changed_value_dic):
            return True
        else:
            return False


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
