import make_list

path = 'lfn.txt'
lfn = open(path,'w')
for item in make_list.headlist:
  lfn.write("%s\n" % item)
lfn.close()

path = 'input.txt'
input = open(path,'w')
for item in make_list.headinput:
  input.write("%s\n" % item)
input.close()

path = 'days.txt'
days = open(path,'w')
for item in make_list.day:
  days.write("%s\n" % item)
days.close()
