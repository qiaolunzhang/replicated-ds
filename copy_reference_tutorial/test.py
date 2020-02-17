def reassign(list, vec_dic):
  list = [0, 1]
  vec_dic["2"] = "ok"

def append(list, vec_dic):
  list.append(1)
  vec_dic["3"] = "OOOKKK"

list = [0]
print(list)

vec_dic = {"2":"test"}
reassign(list, vec_dic)
print(list)
print(vec_dic)

append(list, vec_dic)
print(list)
print(vec_dic)