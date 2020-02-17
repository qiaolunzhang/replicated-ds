import threading


class VectorClock:
    """
    This class is used by two threads: PropagateThread and VectorHandlerThread
    - PropagateThread will increase it when sending messages to other replica
    - VectorHandlerThread may change the vector clock value when receiving vector_clock from
    other replica
    """
    def __init__(self, num_replica, _id):
        self.id = _id
        self.num_replica = num_replica
        #self.vector_clock = [0 for i in range(self.num_replica)]
        self.vector_clock_dic = {}
        self.lock = threading.Lock()
        # the format of the element is:
        # sender_id:id1:value:id2:value:id3:value|x:3:y:4:z:5
        self.received_vc_dict = {}
        # todo: the following received_vector_clocks need to be replaced by the above dict
        # store all the received vector_clock from other replica
        # when we add/remove a new replica, this function need to be changed
        # e.g. [[id1, [2, 3, 5]], [id2, [4, 5, 6]]
        self.received_vector_clocks = []
        self.replica_dic = {}
        self.lock = threading.Lock()

    def init_vector_clock_dic(self, vc_dic, local_id):
        print("Initing vector clock")
        # set the local id here
        self.id = local_id
        self.num_replica = 1
        # set the vector clock for local id
        self.vector_clock_dic[self.id] = 0
        for k, v in vc_dic.items():
            # replica_dic[replica_id] = [replica_ip, replica_port]
            # replica_id is int, replica_ip is string, replica_port is int
            # stores the id, ip, port of each replica
            self.replica_dic[k] = v
            # initialize the vector_clock
            self.vector_clock_dic[k] = 0
            self.num_replica += 1
        print(self.replica_dic)

    def locked_add_received_vc(self, new_vc_key, new_vc_value):
        with self.lock:
            # sender_id:id1:value:id2:value:id3:value|x:3:y:4:z:5
            # new_vc_key is: sender_id:id1:value:id2:value:id3:value
            # new_vc_value is: x:3:y:4:z:5
            self.received_vc_dict[new_vc_key] = new_vc_value
            self.received_vector_clocks.append([new_vc_key, new_vc_value])

    def locked_add_replica_info(self, replica_ip, replica_port, replica_id):
        with self.lock:
            self.replica_dic[replica_id] = [replica_ip, replica_port]

    """
    def locked_add_received_vector_clock(self, vector_clock):
        with self.lock:
            self.received_vector_clocks.append(vector_clock)
    """

    def locked_send_vector_clock(self):
        try:
            # if there is new item changed, we do this operation
            with self.lock:
                self.vector_clock_dic[self.id] = self.vector_clock_dic[self.id] + 1
                return self.vector_clock_dic
        except Exception as e:
            print(e)

    def get_vector_clock_message_to_accept(self):
        """
        first change the vector clock, then change  the value, because there
        is only one thread that is handling the vector clock
        # sender_id:id1:value:id2:value:id3:value|x:3:y:4:z:5
        :return: the message that we need to update
        """
        try:
            #flag = True
            #accepted_vc_id = ""
            for k, v in self.received_vc_dict.items():
                flag = True
                # compare the vector in k with self.vector_clock_dic
                # todo: recheck the datatype here
                key_to_received_vc_dict = k
                k = k.split(":")
                k = [int(e) for e in k]
                vc_id = k[0]
                vc_list = k[1:]
                for i in range(len(vc_list) // 2):
                    id_tmp = vc_list[2*i]
                    clock_tmp = vc_list[2*i+1]
                    if id_tmp == vc_id:
                        if clock_tmp != self.vector_clock_dic[id_tmp] + 1:
                            flag = False
                    elif clock_tmp > self.vector_clock_dic[id_tmp]:
                        flag = False
                    if not flag:
                        break
                if flag:
                    # pop actually moves the item from the dict
                    self.vector_clock_dic[vc_id] = self.vector_clock_dic[vc_id] + 1
                    return self.received_vc_dict.pop(key_to_received_vc_dict)
            return ""
        except Exception as e:
            print(e)


"""
    def locked_accept_vector_clock(self):
        # todo: reset the vector_clock function
        with self.lock:
            # todo: change received_vector_clocks to dict
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
"""
