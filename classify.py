def readline(file0):
	#read a line, split on whitespace, yield the line
	lines = file0.readlines()
	for line in lines:	
		yield line.split()

def tf(arg, print_flag):
	dictpos = {}
	dictneg = {}
	dictionary = {}
	with open(arg) as df, open('tf.csv', 'w+') as csvfile:
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
						dictionary[word][0] += 1
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

		#print('debug: total words: %d' % len(third))

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
	if(print_flag):
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

	print("tfgrep: confusion matrix for training data:\nTP  FN | %d  %d\nFP  TN | %d %d" % (tp, fn, fp, tn))
	print("accuracy: " + str(100 * ((tp + tn)/(tp+fp+tn+fn))) + '%')
	
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

	print("tfgrep: confusion matrix for testing data:\nTP  FN | %d  %d\nFP  TN | %d %d" % (tp, fn, fp, tn))
	print("accuracy: " + str(100 * ((tp + tn)/(tp+fp+tn+fn))) + '%')
	
	return mdw

def priors(arg):
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
	ret = [pos_pct, neg_pct]

	if(arg):
		print("class 1 accounts for %f of the data, class -1 accounts for %f of the data." % (pos_pct, neg_pct))

		print("priors: confusion matrix for training data:\nTP  FN | %d  %d\nFP  TN | %d %d" % (tp, fn, fp, tn))
		print("accuracy: " + str(100 * ((tp + tn)/(tp+fp+tn+fn))) + '%')

	tp = 0
	tn = 0
	fp = 0
	fn = 0

	with open(testfile) as tf:
		lines = readline(tf)
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

	if(arg):
		print("priors: confusion matrix for testing data:\nTP  FN | %d  %d\nFP  TN | %d %d" % (tp, fn, fp, tn))
		print("accuracy: " + str(100 * ((tp + tn)/(tp+fp+tn+fn))) + '%')

	return([pos_ctr, neg_ctr, total])

def mnb():
	temp = priors(False)

	prob_pos = temp[0] / temp[2]
	prob_neg = temp[1] / temp[2]

	tp = 0
	tn = 0
	fp = 0
	fn = 0

	cpost = 0
	cnegt = 0
	
	dictionary = {}
	with open('tf.csv', 'r') as csvfile:
		rdr = csv.reader(csvfile, delimiter = ',')

		#get total word count for each class
		for row in rdr:
			cpost += int(row[1])
			cnegt += int(row[2])
			dictionary[str(row[0])] = [int(row[1]), int(row[2])]

	#print("debug: cpost: %d\tcnegt: %d" % (cpost, cnegt))

	with open(datafile) as df:
		lines = readline(df)
		for line in lines:
			linedict = {}
			words = line[1:]			
			sumclass1 = abs(math.log(prob_pos))
			sumclass2 = abs(math.log(prob_neg))

			for word in words:							#for each line, make a dict out of its words
				if(word in linedict):
					linedict[word] += 1
				else:
					linedict[word] = 1

			for word in linedict:
					sumclass1 += (math.log((1 + dictionary[word][0])/(1 + cpost)) * linedict[word])
					sumclass2 += (math.log((1 + dictionary[word][1])/(1 + cnegt)) * linedict[word])

			if(sumclass1 >= sumclass2):
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
		print("accuracy: " + str(100 * ((tp + tn)/(tp+fp+tn+fn))) + '%')
	tf(testfile, False)
	temp = priors(False)

	prob_pos = temp[0] / temp[2]
	prob_neg = temp[1] / temp[2]

	tp = 0
	tn = 0
	fp = 0
	fn = 0

	cpost = 0
	cnegt = 0
	
	dictionary = {}
	with open('tf.csv', 'r') as csvfile:
		rdr = csv.reader(csvfile, delimiter = ',')

		#get total word count for each class
		for row in rdr:
			cpost += int(row[1])
			cnegt += int(row[2])
			dictionary[str(row[0])] = [int(row[1]), int(row[2])]

	#print("debug: cpost: %d\tcnegt: %d" % (cpost, cnegt))

	with open(testfile) as df:
		lines = readline(df)
		for line in lines:
			linedict = {}
			words = line[1:]			
			sumclass1 = abs(math.log(prob_pos))
			sumclass2 = abs(math.log(prob_neg))

			for word in words:							#for each line, make a dict out of its words
				if(word in linedict):
					linedict[word] += 1
				else:
					linedict[word] = 1

			for word in linedict:
					sumclass1 += (math.log((1 + dictionary[word][0])/(1 + cpost)) * linedict[word])
					sumclass2 += (math.log((1 + dictionary[word][1])/(1 + cnegt)) * linedict[word])

			if(sumclass1 >= sumclass2):
				if(line[0] == "1"):
					tp += 1
				else:
					fp += 1
			else:
				if(line[0] == "-1"):
					tn += 1
				else:
					fn += 1
		
		print("confusion matrix for testing data:\nTP  FN | %d  %d\nFP  TN | %d %d" % (tp, fn, fp, tn))
		print("accuracy: " + str(100 * ((tp + tn)/(tp+fp+tn+fn))) + '%')
def df(arg):
	with open(datafile) as df, open('df.csv', 'w+') as csvfile:
		class1 = {}
		class2 = {}
		class_all = {}
		lines = readline(df)
		for line in lines:
			words = line[1:]
			uniq = []
			if(line[0] == "1"):
				for word in words:
					if(word not in uniq):
						uniq.append(word)
						if(word not in class1):
							class1[word] = 1
							class_all[word] = [1, 0]
						else:
							class1[word] += 1
							class_all[word][0] += 1
			else:
				for word in words:
					if(word not in uniq):
						uniq.append(word)
						if(word not in class2):
							class2[word] = 1
							class_all[word] = [0, 1]
						else:
							class2[word] += 1
							class_all[word][1] += 1
		
		largestpos = sorted(class1.items(), key = lambda item: item[1], reverse=True)
		largestneg = sorted(class2.items(), key = lambda item: item[1], reverse=True)

		words = set()
		for word in class1:
			words.add(word)
		for word in class2:
			words.add(word)

		words = sorted(list(words))

		wtr = csv.writer(csvfile)
		wtr.writerow(["Term", "Class 1 Frequency", "Class -1 Frequency"])

		for word in words:
			to_write = [word]
			if(word in class1):
				to_write.append(class1[word])
			else:
				to_write.append(0)
			if(word in class2):
				to_write.append(class2[word])
			else:
				to_write.append(0)
			wtr.writerow(to_write)
		if(arg):
			print("Class 1:")
			for pos in largestpos[:5]:
				print(str(pos))

			print("Class -1:")
			for neg in largestneg[:5]:
				print(str(neg))
		return(class_all)
	
def nb():
	temp = priors(False)

	prob_pos = temp[0] / temp[2]
	prob_neg = temp[1] / temp[2]

	dict1 = {}
	dict2 = {}
	
	with open('df.csv') as dcsv:
		rdr = csv.reader(dcsv, delimiter = ',')
		for line in list(rdr)[1:]:
			if(line[1]):
				dict1[line[0]] = int(line[1])
			if(line[2]):
				dict2[line[0]] = int(line[2])

	tp = 0
	fp = 0
	tn = 0
	fn = 0

	cpost = 0
	cnegt = 0
	
	dictionary = {}
	with open('tf.csv', 'r') as csvfile:
		rdr = csv.reader(csvfile, delimiter = ',')

		#get total word count for each class
		for row in rdr:
			cpost += int(row[1])
			cnegt += int(row[2])
			dictionary[str(row[0])] = [int(row[1]), int(row[2])]

	with open(datafile) as df:
		lines = readline(df)
		for line in lines:
			linedict = {}
			words = line[1:]			
			sumclass1 = abs(math.log(prob_pos))
			sumclass2 = abs(math.log(prob_neg))

			for word in words:							#for each line, make a dict out of its words
				if(word in linedict):
					linedict[word] += 1
				else:
					linedict[word] = 1

			for word in linedict:
				sumclass1 += (math.log((1 + dict1[word])/(2 + cpost)))
				sumclass2 += (math.log((1 + dict2[word])/(2 + cnegt)))

			if(sumclass1 >= sumclass2):
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
	print("accuracy: " + str(100 * ((tp + tn)/(tp+fp+tn+fn))) + '%')

def mine(arg):
	pass

#it's ya boi main
if __name__ == '__main__':
	import sys
	import csv
	import ast
	import math
	import time

	if(len(sys.argv) <= 3):
		#print out help stuff
		print("Usage:\nfunction\twhat it do\n-------------------------------------------\ntf\t\tcalculates term frequencies")
		print("tfgrep\t\tcalculates most discriminating term")
		print("priors\t\tcalculates majority class in each file")
		print("mnb\t\tuses the multinomial naive bayes model to predict most likely class")
		sys.exit(0)

	datafile = sys.argv[1]
	testfile = sys.argv[2]
	func = sys.argv[3]

	if func == 'tf':
		tf(datafile, True)
	elif func == 'tfgrep':
		tfgrep()
	elif func == 'priors':
		priors(True)
	elif func == 'mnb':
		mnb()
	elif func == 'df':
		df(True)
	elif func == 'nb':
		nb()
	else:
		sys.exit(0)
