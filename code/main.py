#!/usr/python/env env
import MySQLdb
import os
import numpy as np
import matplotlib.pyplot as ply
from functionSet import *

validGapNum = 13  # if gap contains too less points, we could not get a good fit for this figure.
pattenLen = 9

spareYearLen = 5

def main():
	imgPrefix = './figure/num/'
	f_initConn("root", "admin", "eecs564")
	print "save the result for slope detector"
	numOfFigureToSave = 3
	print "only save " + str(numOfFigureToSave) + " figures each"
	f_saveFigureForEachName("M", numOfFigureToSave, "trendNum")
	f_saveFigureForEachName("F", numOfFigureToSave, "trendNum")
	print "predict p for each name. This may take 20-40 minutes"
	f_updateP_estAndVar(validGapNum, pattenLen)

	f_drawP_estPDF()
	print "this may take 40-60 minutes"
	for predictYear in range(1, 1+spareYearLen):
		print "predict ", predictYear, " of", spareYearLen
		f_getPredictionError(predictYear, spareYearLen, validGapNum, pattenLen)

	maleError = np.zeros(spareYearLen)
	femaleError = np.zeros(spareYearLen)
	loadedData = np.loadtxt("./predictError/error_female_"+ str(validGapNum) +"_"+ str(pattenLen) +"_" + str(1) + ".csv")
	ply.plot(loadedData*100, 'b-x', label = "error for each predictable name" )
	ply.plot(range(len(loadedData)), np.mean(np.abs(loadedData)*100) * np.ones(len(loadedData)), 'r-', label = "average error" );
	ply.grid()
	ply.legend()
	ply.xlabel("index of name")
	ply.ylabel("error %")
	ply.savefig("predict_error_for_female")
	ply.show()
	for predictLen in range(spareYearLen):

		loadedData = np.loadtxt("./predictError/error_female_"+ str(validGapNum) +"_"+ str(pattenLen) +"_" + str(predictLen+1) + ".csv")
		loadedData[loadedData > 5] = np.mean(loadedData)
		femaleError[predictLen] = np.mean(loadedData)

		loadedData = np.loadtxt("./predictError/error_female_"+ str(validGapNum) +"_"+ str(pattenLen) +"_" + str(predictLen+1) + ".csv")
		loadedData[loadedData > 5] = np.mean(loadedData)
		maleError[predictLen]= np.mean(loadedData)

	ply.plot(range(1, spareYearLen+1), maleError * 100, 'b-o', label = "Male")
	ply.plot(range(1, spareYearLen+1), femaleError * 100, 'g-x', label = "Female")
	ply.legend()
	ply.xlabel("# of predict year")
	ply.ylabel("error %")
	ply.grid()
	ply.savefig("prediction_error")
	ply.show()

if __name__ == "__main__":
	main()

