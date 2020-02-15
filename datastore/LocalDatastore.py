import threading
import time
import logging
import concurrent.futures

class LocalDataStore:
    def __init__(self):
        self.value_dic = {}

    def load_value(self, name):