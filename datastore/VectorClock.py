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
        self.LOCALHOST = "127.0.0.1"
        self.PORT = 8080
        self.num_replica = num_replica
        self.is_partition = True
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
        self.new_id_list = []
        self.lock = threading.Lock()
        # {id1:[ip1, port1], id2:[ip2, port2]}
        # assume that we have only one leader
        self.leader_dic = {}
        self.follower_dic = {}

    def put_leader_dic(self, id_val, ip_val, port_val):
        self.leader_dic[id_val] = [ip_val, port_val]

    def put_follower_dic(self, id_val, ip_val, port_val):
        self.follower_dic[id_val] = [ip_val, port_val]

    def get_leader_dic(self):
        return self.leader_dic

    def get_follower_dic(self):
        return self.follower_dic

    def get_new_replica_str_leader(self):
        new_replica_tuple = self.leader_dic.popitem()
        replica_str = str(new_replica_tuple[0]) + ":" + new_replica_tuple[1][0]
        replica_str = replica_str + ":" + str(new_replica_tuple[1][1])
        return replica_str

    def get_new_replica_str_follower(self):
        new_replica_tuple = self.follower_dic.popitem()
        replica_str = str(new_replica_tuple[0]) + ":" + new_replica_tuple[1][0]
        replica_str = replica_str + ":" + new_replica_tuple[1][1]
        return replica_str

    def get_local_id(self):
        return self.id

    def assign_new_id(self):
        # the id and port are both integer
        ids_now = self.replica_dic.keys()
        tmp_id = 1
        while tmp_id in ids_now or tmp_id in self.new_id_list:
            tmp_id = tmp_id + 1
        self.new_id_list.append(tmp_id)
        # it's an int
        return tmp_id

    def add_new_replica_to_vector_clock(self, id_val, clock_val, host_val, port_val):
        self.num_replica = self.num_replica + 1
        self.replica_dic[id_val] = [host_val, port_val]
        self.vector_clock_dic[id_val] = clock_val

    def set_host_port(self, host, port):
        self.LOCALHOST = host
        self.PORT = port

    def get_host_port(self):
        return self.LOCALHOST, self.PORT

    def init_vector_clock_dic(self, vc_dic, local_id):
        print("Initing vector clock")
        # set the local id here
        self.id = local_id
        self.num_replica = 1
        # set the vector clock for local id
        self.vector_clock_dic[self.id] = 0
        if bool(self.vector_clock_dic):
            self.is_partition = False
        for k, v in vc_dic.items():
            # replica_dic[replica_id] = [replica_ip, replica_port]
            # replica_id is int, replica_ip is string, replica_port is int
            # stores the id, ip, port of each replica
            self.replica_dic[k] = v
            # initialize the vector_clock
            self.vector_clock_dic[k] = 0
            self.num_replica += 1
        print(self.replica_dic)

    def set_partition_state(self, is_partition):
        # if is_partition is True, the replica is disconnected with all other replica
        # otherwise, it is connected with other replica
        self.is_partition = is_partition

    def check_is_partition(self):
        return self.is_partition

    def get_replica_str(self):
        replica_str_list = []
        replica_str_tmp = str(self.id) + ":" + str(self.LOCALHOST)
        replica_str_tmp = replica_str_tmp + ":" + str(self.PORT)
        replica_str_list.append(replica_str_tmp)

        for k, v in self.replica_dic.items():
            replica_str_tmp = str(k) + ":" + str(v[0])
            replica_str_tmp = replica_str_tmp + ":" + str(v[1])
            replica_str_list.append(replica_str_tmp)
        replica_str = "|".join(replica_str_list)
        return replica_str

    def get_replica_dic(self):
        return self.replica_dic

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

    def locked_get_send_vector_clock_str(self):
        """
        :return: a string 2:0:0:1:1:2:1, the first number is the id of the replica,
                the following number is the id: clock
        """
        try:
            # if there is new item changed, we do this operation
            with self.lock:
                self.vector_clock_dic[self.id] = self.vector_clock_dic[self.id] + 1
                send_vector_clock_str = str(self.id)
                for k, v in self.vector_clock_dic.items():
                    send_vector_clock_str = send_vector_clock_str + ":" + str(k) + ":" + str(v)
                return send_vector_clock_str
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
