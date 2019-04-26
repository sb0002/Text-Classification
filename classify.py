def readline(file0):
	#read a line, split on whitespace, yield the line
	lines = file0.readlines()
	for line in lines:	
		yield line.split()

def tf():
	dictpos = {}
	dictneg = {}
	dictionary = {}
	with open(datafile) as df, open('tf.csv', 'w+') as csvfile:
		lines = readline(df)
		for line in lines:
			words = line[1:]
			if(line[0] == "1"):
				for word in words:
					if word not in dictpos:
						dictpos[word] = 1
						dictionary[word] = [1, 0]
					else:
						dictpos[word] += 1
						dictionary[word][1] += 1
			if(line[0] == "-1"):
				for word in words:
					if word not in dictneg:
						dictneg[word] = 1
						dictionary[word] = [0, 1]
					else:
						dictneg[word] += 1
						dictionary[word][1] += 1

		largestpos = sorted(dictpos.items(), key = lambda item: item[1], reverse=True)
		largestneg = sorted(dictneg.items(), key = lambda item: item[1], reverse=True)

		first = list(dictpos.keys())
		second = list(dictneg.keys())
		third = sorted(list(set(first + second)))

		print('debug: total words: %d' % len(third))

		dp = 0
		dn = 0
		wtr = csv.writer(csvfile)
		for word in third:
			if(word not in dictpos):
				dp = 0
			else:
				dp = dictpos[word]
			if(word not in dictneg):
				dn = 0
			else:
				dn = dictneg[word]
			wtr.writerow([word, str(dp), str(dn)])

	print("Class 1:")
	for pos in largestpos[:5]:
		print(str(pos))

	print("Class -1:")
	for neg in largestneg[:5]:
		print(str(neg))

	return(dictionary)

def tfgrep():
	mdc = ""
	with open('tf.csv', 'r') as csvfile:
		rdr = csv.reader(csvfile, delimiter=',')

		allrows = []
		compare_row = 0
		row_with_biggest = 0
		
		it = 0

		for row in rdr:
			allrows.append(row)
		
		maximum = abs(int(allrows[0][1]) - int(allrows[0][2]))
		for comparison_row in allrows:
			maybe_maximum = abs(int(comparison_row[1]) - int(comparison_row[2]))
			if(maybe_maximum > maximum):
				maximum = maybe_maximum
				row_with_biggest = compare_row
			compare_row += 1
			it += 1

		
		mdw = allrows[row_with_biggest][0]
		print("best word is %s with discrimination %d" % (mdw, maximum))
	tp = 0
	fp = 0
	tn = 0
	fn = 0

	with open(datafile) as df:
		lines = readline(df)
		for line in lines:
			if(mdw in line):
				if(line[0] == "1"):
					tp += 1
				else:
					fp += 1
			else:
				if(line[0] == "-1"):
					tn += 1
				else:
					fn += 1

	print("confusion matrix for training data:\nTP  FN | %d  %d\nFP  TN | %d %d" % (tp, fn, fp, tn))

	tp = 0
	fp = 0
	tn = 0
	fn = 0

	with open(testfile) as df:
		lines = readline(df)
		for line in lines:
			if(mdw in line):
				if(line[0] == "1"):
					tp += 1			#it's in class 1 and we thought it was
				else:
					fp += 1			#it's in class 1 and we didn't think it was
			else:
				if(line[0] == "-1"):
					tn += 1			#it's in not in class 1 and we realized it wasn't
				else:
					fn += 1			#it's not in class 1 but we thought it was

	print("confusion matrix for testing data:\nTP  FN | %d  %d\nFP  TN | %d %d" % (tp, fn, fp, tn))
	return mdw

def priors():
	pos_ctr = 0
	neg_ctr = 0
	total = 0
	lines = []

	tp = 0
	tn = 0
	fp = 0
	fn = 0	

	with open(datafile) as df:
		lines = readline(df)
		for line in lines:
			if(line[0] == "1"):
				pos_ctr += 1
				tp += 1
			else:
				neg_ctr += 1
				fp += 1
			total += 1

	pos_pct = pos_ctr / total
	neg_pct = neg_ctr / total

	print("class 1 accounts for %f of the data, class -1 accounts for %f of the data." % (pos_pct, neg_pct))

	print("confusion matrix for training data:\nTP  FN | %d  %d\nFP  TN | %d %d" % (tp, fn, fp, tn))
	
	return([pos_pct, neg_pct])

def mnb():
	temp = priors()
	temp2 = tf()

	prob_pos = temp[0]
	prob_neg = temp[1]

	dictionary = temp2

	total_pos = 0
	total_neg = 0

	cpost = 0
	cnegt = 0

	line_class_prediction = {}

	with open('tf.csv', 'r') as csvfile:
		rdr = csv.reader(csvfile, delimiter = ',')

		#get total word count for each class
		for row in rdr:
			cpost += int(row[1])
			cnegt += int(row[2])

	print("debug: c1t: %d\tc-1t: %d" % (cpost, cnegt))

	with open(datafile) as df, open('tf.csv', 'w+') as csvfile:
		lines = readline(df)
		numerator = 0.0
		demominator = 0.0
		for line in lines:
			line_dict = {}
			for word in line:	#assemble a [word] : count dictionary for the line-doc
				if(word == "1" or word == "-1"):
					continue
				if word in line_dict:
					line_dict[word] += 1
				else:
					line_dict[word] = 1

		
			for word in line_dict.keys():
				#print(dictionary[word])
				numerator += (line_dict[word] * math.log10((1 + dictionary[word][0])/(1 + cpost)))
				demominator += (line_dict[word] * math.log10((1 + dictionary[word][1])/(1 + cnegt)))
			result = (prob_pos * numerator)/(prob_neg * demominator)
			#print("result = ", result)
			if(result < 1):
				pass
				#predict class 1
			if(result > 1):
				#predict class -1
				pass
def df(arg):
	pass

def nb(arg):
	pass

def mine(arg):
	pass

#it's ya boi main
if __name__ == '__main__':
	import sys
	import csv
	import ast
	import math

	if(len(sys.argv) <= 3):
		#print out help stuff
		print("Usage:\nfunction\twhat it do\n-------------------------------------------\ntf\t\tcalculates term frequencies")
		print("tfgrep\t\tcalculates most discriminating term")
		#TODO: help message for all functions
		sys.exit(0)

	datafile = sys.argv[1]
	testfile = sys.argv[2]
	func = sys.argv[3]

	if func == 'tf':
		tf()
	elif func == 'tfgrep':
		tfgrep()
	elif func == 'priors':
		priors()
	elif func == 'mnb':
		mnb()
	else:
		sys.exit(0)
