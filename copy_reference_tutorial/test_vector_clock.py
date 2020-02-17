from datastore.VectorClock import VectorClock

vector_clock = VectorClock(3, 0)
vc_dic = {1:["192.168.68.1", 8888], 2:["192.168.68.2", 8888]}
# input the vc_dic and the id
vector_clock.init_vector_clock_dic(vc_dic, 0)
# the first element should be sender id rather than the IP address
#vc_tmp = "1:0:0:1:0:2:0|x:3:y:4:z:5"
vc_tmp = "1:0:0:1:1:2:0|x:3:y:4:z:5"
vc_tmp = vc_tmp.split("|")
vc_key_tmp = vc_tmp[0]
vc_value_tmp = vc_tmp[1]

vc_tmp1 = "2:0:0:1:1:2:1|x:4:y:5:z:6"
vc_tmp1 = vc_tmp1.split("|")
vc_key_tmp1 = vc_tmp1[0]
vc_value_tmp1 = vc_tmp1[1]

vector_clock.locked_add_received_vc(vc_key_tmp1, vc_value_tmp1)
value_to_accept = vector_clock.get_vector_clock_message_to_accept()
print(value_to_accept)

vector_clock.locked_add_received_vc(vc_key_tmp, vc_value_tmp)
value_to_accept = vector_clock.get_vector_clock_message_to_accept()
print(value_to_accept)
value_to_accept = vector_clock.get_vector_clock_message_to_accept()
print(value_to_accept)
