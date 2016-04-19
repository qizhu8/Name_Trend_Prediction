#!/usr/python/env env
import MySQLdb
import os
from scipy import signal
import matplotlib.pyplot as ply
import numpy as np
dbUser     = ""
dbPwd      = ""
dbName     = ""
conn       = -1
cursor     = -1
INSERT_SQL = """INSERT INTO DATA(state, gender, year, name, occurence) values ("{state}", "{gender}", "{year}", "{name}", {occurence}); """
name_list  = []

# initial connection and the cursor
def f_initConn(user, passwd, db):
	global conn
	global cursor
	global dbUser
	global dbPwd
	global dbName
	conn   = MySQLdb.connect(user = user, passwd = passwd, db = db)
	cursor = conn.cursor()
	dbUser = user
	dbPwd  = passwd
	dbName = db
	print  "initial connection finished"

# execute .sql file
def f_executeScriptsFromFile(filename):
	for line in open(filename).read().split(';\n'):
	    cursor.execute(line)

# read all the data files and insert the info into the database
def f_readDate(filename):
	fid = open(filename, "r")
	data = fid.read()
	data_list = data.split("\r\n")
	for i in range(0, len(data_list)-1):
		data_tmp = data_list[i].split(",")
		comment_sql = INSERT_SQL.format(\
			state = data_tmp[0], \
			gender = data_tmp[1], \
			year = data_tmp[2],\
			name = data_tmp[3],\
			occurence = data_tmp[4])
		cursor.execute(comment_sql)
	conn.commit()

# read all files and insert data to database
def f_run():
	if conn == -1:
		print "please initialize the connection use 'f_initConn' function"
		return
	prefix = "namesbystate/"
	file_lists = os.listdir(prefix)
	for filename_index in range(len(file_lists)):
		filename = file_lists[filename_index]
		print round(filename_index * 100.0 / (len(file_lists))),"% reading " + filename
		if filename[filename.find('.')+1:] == "TXT":
			f_readDate(prefix + filename)

# insert
def f_insert(sql):
	cursor.execute(sql)
	conn.commit()

# custom search interface
def f_search(sql):
	cursor.execute(sql)
	searchResult = np.array(cursor.fetchall())
	return searchResult

# form the "name" table from "data" table
def f_formNameTable():
	cursor.execute("delete from name;")
	conn.commit()
	sql_ = "insert into name (gender, name, occurence, beginyear, endyear) select gender, name, sum(occurence), min(year), max(year) from data group by name, gender order by sum(occurence) DESC;"
	cursor.execute(sql_)
	conn.commit()
	print "insert finished"

# form the "nameinfo" table from "data" table
def f_formNameInfoTable():
	sql_ = """insert into nameinfo (gender, year, name, occurence) select gender, year, name, sum(occurence) from data where year = {year} group by name, gender;"""
	for year in range(1910, 2015):
		print round((year - 1910.0) * 100 / (2015-1910)), "%, ", year
		cursor.execute(sql_.format(year = year))
		conn.commit()
	print "insert finished"

# get number of male & female from 1910 
def f_getMaleFemailEachYear():
	sql_ = """select year, sum(occurence) from data where gender="{gender}" group by year;"""
	
	querySet = f_search(sql_.format(gender = "F"))
	female_num = querySet.T[1].astype(np.int)

	yearList = querySet.T[0].astype(np.int)

	querySet = f_search(sql_.format(gender = "M"))
	male_num = querySet.T[1].astype(np.int)
	return yearList, male_num, female_num

# get some typical data from database or file
def f_loadVar(type, prefix="./var/"):
	if type == "MaleFemailEachYear":
		yearList, male_num, female_num = f_getMaleFemailEachYear()
		return yearList, male_num, female_num
	elif type == "DistinctName":
		malename, femalename = f_getDistinctName()
		return malename, femalename
	else:
		return

# get distinct name for male and female
def f_getDistinctName(constrain = ""):
	# grab data from Name table
	sql_ = """select name, occurence from name where gender = "{gender}" {constrain};""";
	querySet = f_search(sql_.format(gender = "F", constrain = constrain))
	female_name = querySet.T[0]

	querySet = f_search(sql_.format(gender = "M", constrain = constrain))
	male_name = querySet.T[0]
	return male_name, female_name

# get the # of user and correpond index for one name 
def f_getNameInfo(name, gender):
	Sql_ = """select gender, year, name, occurence from NameInfo where name = "{name}" and gender = "{gender}";"""
	result = f_search(Sql_.format(name = name, gender = gender))
	# print result
	num_name = result[:, 3].astype(np.float)
	year_range = result[:, 1].astype(np.int) - 1910
	return num_name, year_range


def f_saveFigureForEachName(gender, totalNumber, par = "number", prefix = "./figure/"):
	if gender == "M": 
		directName = "Male"
		targetName, _ = f_getDistinctName()
	else:
		directName = "Female"
		_, targetName = f_getDistinctName()
	if par == "number":
		if not os.path.exists(prefix + "num/" + directName + '/'):
			os.makedirs(prefix + "num/" + directName + '/')
		for index in range(totalNumber):
			print index+1, "of", totalNumber, gender
			name = targetName[index]
			nameNum, yearRange = f_getNameInfo(name, gender)
			yearindex = yearRange-1910
			ply.plot(yearRange, nameNum, 'bo-', label=name)
			ply.xlabel("Year")
			ply.ylabel("number of people")
			ply.legend(loc=2)
			ply.savefig(prefix + "num/" + directName + '/' + str(index) + name)
			ply.close()
	elif par == "proportion":
		if not os.path.exists(prefix + "num/" + directName + '/'):
			os.makedirs(prefix + "num/" + directName + '/')
		yearList, malenum, femalenum = f_loadVar("MaleFemailEachYear")
		for index in range(totalNumber):
			print index+1, "of", totalNumber, gender
			name = targetName[index]
			nameNum, yearRange = f_getNameInfo(name, gender)
			# print result
			yearindex = yearRange-1910
			nameProp = num_name/malenum[yearindex]
			
			ply.plot(yearRange, nameProp, 'bo-', label = name)
			ply.xlabel("Year")
			ply.ylabel("Proportion of the Name")
			ply.legend(loc=2)
			ply.savefig(prefix + "prop/" + directName + '/' + str(index) + name)
			ply.close()
	elif par == "trendNum":
		if not os.path.exists(prefix + "num/" + directName + '/'):
			os.makedirs(prefix + "num/" + directName + '/')
		for index in range(totalNumber):
			print index+1, "of", totalNumber, gender
			name = targetName[index]
			nameNum, yearRange = f_getNameInfo(name, gender)
			yearindex = yearRange-1910
			trend = f_getTrend(nameNum, yearRange, 9)
			ply.plot(yearRange, nameNum, 'bo-', label=name)
			for scanIndex in range(len(trend)-1):
				if trend[scanIndex] != trend[scanIndex+1]:
					x = (yearRange[scanIndex] + yearRange[scanIndex+ 1])/2.0
					ply.plot([x, x], [min(nameNum), max(nameNum)], 'r-')
			ply.xlabel("Year")
			ply.ylabel("number of people")
			ply.legend(loc=2)
			ply.savefig(prefix + "num/" + directName + '/' + str(index) + name)
			ply.close()


# interpolating data by linear model
def f_interpolation(data, index, expectedIndex):
	if len(expectedIndex) == len(index):
		# no need to process
		return data, index
	elif len(index) < 2: # could not fix
		return data, index
	else:
		data_n = -np.ones(len(expectedIndex)) # number of usage is impossible to be negative
		data_n[index] = data
		missing = False # if we found the begin of the missing point -> true, not found -> false
		startIndex, endIndex = 0, 0
		for scan_index in range(len(expectedIndex)):
			if data_n[scan_index] == -1 and not missing: # the begining of missing period
				missing = True
				startIndex = scan_index
			elif data_n[scan_index] != -1 and missing: # the ending of missing period
				endIndex = scan_index; # note that endIndex -> the data after the missing one
				# linear interpolation
				if startIndex != 0:
					missingIndex = endIndex - startIndex + 1
					gap = (data_n[endIndex] - data_n[startIndex-1] + 0.0) / missingIndex
					for fixIndex in range(startIndex, endIndex):
						data_n[fixIndex] = round(data_n[startIndex-1] + gap * (fixIndex - startIndex + 1))
				else:
					gap = (data[endIndex+1] - data_n[endIndex] + 0.0) / (index[endIndex+1] - endIndex)
					for fixIndex in range(endIndex):
						data_n[endIndex - fixIndex -1] = round(data_n[endIndex] - (fixIndex + 1) * gap)
				missing = False
		if missing == True: # missing the last couples of points
			gap = (data_n[startIndex-1] - data_n[0] + 0.0) / (startIndex)
			for fixIndex in range(startIndex, len(expectedIndex)):
				data_n[fixIndex] = round(data_n[startIndex-1] + gap * (fixIndex - startIndex + 1))
			missing = False
	return data_n, expectedIndex

# use patten to tell whether it is increasing or decreasing
def f_getTrend(data, yearRange, pattenLen = 9):
	patten = np.array(range(pattenLen)) - (pattenLen-1.0)/2 # a decreasing patten (for match filter, the patten will flip)
	# convResult = np.convolve(data, patten[::-1])
	convResult = signal.convolve(data, patten[::-1], 'same')
	return np.sign(convResult)

def f_getDistForName():
	sql_ = """select occurence from name;"""
	querySet = f_search(sql_)
	print len(number)
	ply.hist(number, bins=100)
	ply.show()

def f_getCDFOfName(occuranceRange = range(4,10000, 100)):
	sql_ = """select count(*) from name where occurence <= {occurence};"""
	cdfForName = np.zeros(len(occuranceRange))
	for numOfName_index in range(len(occuranceRange)):
		querySet = f_search(sql_.format(occurence = occuranceRange[numOfName_index]))
		cdfForName[numOfName_index] = querySet[0, 0]
	return cdfForName, occuranceRange

# get the range for valid increasing or decreasing range
# trend is [+1, +1, -1, -1, -1] means increase two years and decrease three years
# validRangeLen is the length of range which will take into count, we will ignore too short range
# increaseTrend True: increasing. False: decreasing
def f_getValidTrendRange(nameTrend, validRangeLen, increaseTrend = True): 
	if increaseTrend:
		detector = 1
	else:
		detector = -1
	startIndex, endIndex = 0, 0
	foundFlag = False
	validRange = [];
	for index in range(len(nameTrend)):
		if nameTrend[index] == detector and not foundFlag:
			# start point
			startIndex = index
			foundFlag = True
		elif nameTrend[index] == -detector and foundFlag:
			# end point
			endIndex = index - 1
			foundFlag = False
			if index - startIndex >= validRangeLen:
				validRange.append((startIndex, endIndex))

	if foundFlag and index - startIndex >= validRangeLen:
		validRange.append((startIndex, index))
	return validRange

def f_getP_est(name, nameNum, peopleNum, yearRange, validGapNum, pattenLen):
	nameTrend = f_getTrend(nameNum, yearRange, pattenLen)
	validRange = f_getValidTrendRange(nameTrend, validGapNum)
	if len(validRange):
		nameNum_range = range(validRange[0][0], validRange[0][1]+1)
		p_est = np.zeros(len(nameNum_range)-1)
		for index in range(len(nameNum_range)-1):
			tmpIndex = validRange[0][0] + index
			p_est[index] = nameNum[tmpIndex+1] / (peopleNum[tmpIndex] * nameNum[tmpIndex] + 0.0)
		return p_est
	else:
		return

def f_updateP_estAndVar(validGapNum = 13, pattenLen = 9):
	yearList, maleNum, femaleNum = f_loadVar("MaleFemailEachYear")
	malename, femalename = f_getDistinctName("and (endyear - beginyear)>" + str(validGapNum + pattenLen - 1) + " and occurence > " + str((pattenLen + validGapNum-1) * 5))
	sql_update = """update name set p_est = {p_est}, var = {var} where name = "{name}" and gender = "{gender}"; """
	gender = "M";
	for index in range(len(malename)):
		print index, gender, len(malename),
		name = malename[index]
		nameNum, yearRange = f_getNameInfo(name, gender)
		p_est = f_getP_est(name, nameNum, maleNum, yearRange, validGapNum, pattenLen)
		if p_est is not None:
			f_insert(sql_update.format(p_est = p_est[-1], var = np.var(p_est), name = name, gender = gender))
			print p_est[-1], np.var(p_est)
		else:
			print "not apply"

	gender = "F";
	for index in range(len(femalename)):
		print index, gender, len(femalename),
		name = femalename[index]
		nameNum, yearRange = f_getNameInfo(name, gender)
		p_est = f_getP_est(name, nameNum, femaleNum, yearRange, validGapNum, pattenLen)
		if p_est is not None:
			f_insert(sql_update.format(p_est = p_est[-1], var = np.var(p_est), name = name, gender = gender))
			print p_est[-1], np.var(p_est)
		else:
			print "not apply"

def f_getPredictionError(predictYearLen = 1, spareYearLen = 5, validGapNum = 13, pattenLen = 9):
	yearList, maleNum, femaleNum = f_loadVar("MaleFemailEachYear")
	malename, femalename = f_getDistinctName("and p_est > 0")

	gender = "M";
	errorMale = np.zeros(len(malename))
	errorFemale = np.zeros(len(femalename))
	counterMale = 0
	counterFemale = 0
	if not os.path.exists("./predictError/"):
		os.makedirs("./predictError/")
	for nameIndex in range(len(malename)):
		print nameIndex, gender, len(malename)
		name = malename[nameIndex]
		nameNum, yearRange = f_getNameInfo(name, gender)

		nameTrend = f_getTrend(nameNum, yearRange, pattenLen)
		validRange = f_getValidTrendRange(nameTrend, validGapNum)

		if len(validRange):
			counterMale += 1
			nameNum_range = range(validRange[0][0], validRange[0][1]+1 - predictYearLen)
			p_est = np.zeros(len(nameNum_range)-1)
			for index in range(len(nameNum_range)-1):
				tmpIndex = validRange[0][0] + index
				p_est[index] = nameNum[tmpIndex+1] / (maleNum[tmpIndex] * nameNum[tmpIndex] + 0.0)
			targetP = p_est[-1]
			predictYear = range(validRange[0][1]+1 - spareYearLen , validRange[0][1]+1 - spareYearLen + predictYearLen)
			predictedNum = np.zeros(predictYearLen)
			for predictYear_index in range(predictYearLen):
				predictedNum[predictYear_index] = nameNum[predictYear[predictYear_index]-1] * targetP * maleNum[predictYear[predictYear_index]]
				errorMale[nameIndex] += (predictedNum[predictYear_index] - nameNum[predictYear[predictYear_index]]) / (predictYearLen + 0.0) / nameNum[predictYear[predictYear_index]]
		else:
			print "skip"
	np.savetxt("./predictError/error_male_"+str(validGapNum)+"_"+str(pattenLen)+"_"+str(predictYearLen)+".csv", errorMale)


	gender = "F"
	for nameIndex in range(len(femalename)):
		print nameIndex, gender, len(femalename)
		name = femalename[nameIndex]
		nameNum, yearRange = f_getNameInfo(name, gender)

		nameTrend = f_getTrend(nameNum, yearRange, pattenLen)
		validRange = f_getValidTrendRange(nameTrend, validGapNum)

		if len(validRange):
			counterMale += 1
			nameNum_range = range(validRange[0][0], validRange[0][1]+1 - predictYearLen)
			p_est = np.zeros(len(nameNum_range)-1)
			for index in range(len(nameNum_range)-1):
				tmpIndex = validRange[0][0] + index
				p_est[index] = nameNum[tmpIndex+1] / (femaleNum[tmpIndex] * nameNum[tmpIndex] + 0.0)
			targetP = p_est[-1]
			predictYear = range(validRange[0][1]+1 - spareYearLen , validRange[0][1]+1 - spareYearLen + predictYearLen)
			predictedNum = np.zeros(predictYearLen)
			for predictYear_index in range(predictYearLen):
				predictedNum[predictYear_index] = nameNum[predictYear[predictYear_index]-1] * targetP * femaleNum[predictYear[predictYear_index]]
				errorFemale[nameIndex] += (predictedNum[predictYear_index] - nameNum[predictYear[predictYear_index]]) / (predictYearLen + 0.0) / nameNum[predictYear[predictYear_index]]
		else:
			print "skip"
	np.savetxt("./predictError/error_female_"+str(validGapNum)+"_"+str(pattenLen)+"_"+str(predictYearLen)+".csv", errorFemale)

def f_drawP_estPDF():
	sql = "select p_est from name where gender = \"M\" and p_est > 0;"
	male_p_est = f_search(sql)

	sql = "select p_est from name where gender = \"F\" and p_est > 0;"
	female_p_est = f_search(sql)

	x, b = np.histogram(male_p_est, bins = 100, range=(0, 3e-6))
	y, bb = np.histogram(female_p_est, bins = 100, range=(0, 3e-6))
	x = x / (sum(x) + 0.0)
	y = y / (sum(y) + 0.0)
	ply.bar(b[:-1], x, width = b[1] - b[0], color = 'b', label="Male")
	ply.bar(bb[:-1], -y, width = bb[1] - bb[0], color = 'r', label = "Female")
	ply.grid()
	ply.legend()
	ply.xlabel("P")
	ply.ylabel("Probability")
	plt.savefig("pdf_for_p_est")
	ply.show()