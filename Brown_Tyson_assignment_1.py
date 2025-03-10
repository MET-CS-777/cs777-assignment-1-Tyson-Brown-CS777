from __future__ import print_function

import os
import sys
import requests
from operator import add

from pyspark import SparkConf,SparkContext
from pyspark.streaming import StreamingContext

from pyspark.sql import SparkSession
from pyspark.sql import SQLContext

from pyspark.sql.types import *
from pyspark.sql import functions as func
from pyspark.sql.functions import *


#Exception Handling and removing wrong datalines
def isfloat(value):
    try:
        float(value)
        return True
 
    except:
         return False

#Function - Cleaning
#For example, remove lines if they don’t have 16 values and 
# checking if the trip distance and fare amount is a float number
# checking if the trip duration is more than a minute, trip distance is more than 0 miles, 
# fare amount and total amount are more than 0 dollars
def correctRows(p):
    if(len(p)==17):
        if(isfloat(p[5]) and isfloat(p[11])):
            if(float(p[4])> 60 and float(p[5])>0 and float(p[11])> 0 and float(p[16])> 0):
                return p

#Main
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: main_task1 <file> <output> ", file=sys.stderr)
        exit(-1)
    
    sc = SparkContext(appName="Assignment-1")
    rdd = sc.textFile(sys.argv[1])
    
    #Task 1
    #Your code goes here
    trips = rdd.map(lambda x: x.split(','))

    # calling isfloat and correctRows functions to cleaning up data
    taxilinesCorrected = trips.filter(correctRows)

    # get only the first two columns, take distinct taxi and driver and then add 1 to each taxi, then reduce key
    # avoiding group by key
    results = taxilinesCorrected.map(lambda x: (x[0], x[1]))\
    .distinct()\
    .map(lambda x: (x[0], 1))\
    .reduceByKey(lambda x,y: x+y)\
    .top(10, lambda x: x[1])

    results_1 = sc.parallelize(results)
    results_1.coalesce(1).saveAsTextFile(sys.argv[2])


    #Task 2
    
    results2 = taxilinesCorrected.map(lambda p: (p[1], (float(p[16]), float(p[4])/60)))\
    .reduceByKey(lambda x,y: (x[0]+y[0], x[1] + y[1]))\
    .map(lambda x: (x[0], x[1][0]/x[1][1]))\
    .top(10, lambda x: x[1])

    results_2 = sc.parallelize(results2)
    #savings output to argument
    results_2.coalesce(1).saveAsTextFile(sys.argv[3])


    #Task 3 - Optional 
    #Your code goes here

    #Task 4 - Optional 
    #Your code goes here


    sc.stop()