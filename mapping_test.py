import csv
import numpy as np
from copy import deepcopy

with open("patent.csv", "rb") as patent_file:
	patent_reader = csv.reader(patent_file, delimiter=',')
	patent_list = []
	for row in patent_reader:
		patent_list.append(row)
	patent_array = np.array(patent_list, dtype=int)

arg_list = []
for i in range(1, 31):
	arg_list.append([])
	for j in range(8):
		col = patent_array[:, j]
		value = int(col[i])
		arg1 = np.nonzero(col==((value-1)%32))
		arg2 = np.nonzero(col==((value+1)%32))
		arg_list[-1].append(arg1[-1].item(0))	
		arg_list[-1].append(arg2[-1].item(0))

for i in range(30):
	arg_list[i] = set(arg_list[i])
	print len(arg_list[i])

inverse_list = deepcopy(patent_list)
for inverse in inverse_list:
	print inverse
for j in range(8):
	for i in range(32):
		patent_value = int(patent_list[i][j])
		inverse_list[patent_value][j] = i

with open("patent_inverse.csv", "wb") as patent_file:
	patent_writer = csv.writer(patent_file, delimiter=',')
	for row in inverse_list:
		patent_writer.writerow(row)