import threading
import time
import logging
import concurrent.futures

# The lock in Python is the mutex in other programming languages
# A lock is an object that acts like a hall pass
# only one thread at a time can have the lock
# the other thread that wants the lock must wait
# my_lock.acquire()
# my_lock.release()

class LockFakeDatabase:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def locked_update(self, name):
        logging.info("Thread %s: starting update", name)
        logging.debug("Thread %s about to lock", name)
        with self._lock:
            logging.debug("Thread %s has lock", name)
            local_copy = self.value
            local_copy += 1
            time.sleep(0.1)
            self.value = local_copy
            logging.debug("Thread %s after release", name)
            logging.info("Thread %s: finishing update", name)

if __name__ == "__main__":
    format = "%s(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)

    database = LockFakeDatabase()
    logging.info("Testing update. Starting value is %d.", database.value)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for index in range(2):
            executor.submit(database.locked_update, index)
    logging.info("Testing update. Ending value is %d", database.value)
