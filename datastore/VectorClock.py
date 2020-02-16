import threading


class VectorClock:
    """
    This class is used by two threads: PropagateThread and VectorHandlerThread
    - PropagateThread will increase it when sending messages to other replica
    - VectorHandlerThread may change the vector clock value when receiving vector_clock from
    other replica
    """
    def __init__(self, num_replica, id):
        self.id = id
        self.num_replica = num_replica
        self.vector_clock = [0 for i in range(self.num_replica)]
        self.lock = threading.Lock()
        # store all the received vector_clock from other replica
        # when we add/remove a new replica, this function need to be changed
        # e.g. [[id1, [2, 3, 5]], [id2, [4, 5, 6]]
        self.received_vector_clocks = []
        self.lock = threading.Lock()

    def locked_add_received_vector_clock(self, vector_clock):
        with self.lock:
            self.received_vector_clocks.append(vector_clock)

    def locked_send_vector_clock(self):
        with self.lock:
            self.vector_clock[self.id-1] = self.vector_clock[self.id-1] + 1
            return self.vector_clock

    def locked_accept_vector_clock(self):
        with self.lock:
            for vc in self.received_vector_clocks:
                flag = True
                id_check = vc[0]
                vc_check = vc[1]
                if vc_check[id_check] != self.vector_clock[id_check] + 1:
                    #flag = False
                    continue
                for index, clock in enumerate(vc_check):
                    if index != id_check and self.vector_clock[index] < clock:
                        flag = False
                        continue
                if flag:
                    self.vector_clock[id_check] = self.vector_clock[id_check] + 1
