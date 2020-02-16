import threading
import logging


class VectorHandlerThread(threading.Thread):
    """
    Actually we may not need it
    This class will loop forever.
    It is blocked by threading.event
    Once we receive a new vector from the server, we will check all the vector clock
    """
