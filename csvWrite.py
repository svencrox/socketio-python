#!/usr/bin/env python
import csv
import random
import time
import datetime

def saveToFile(csv_data):
    # print numbers between 1 - 100 and assign to rand
    db = str(csv_data['data'])

    # current time and print it
    ts = str(datetime.datetime.now())
    print("ts: " + str(ts))

    with open(csv_data['routing'] + '.csv', 'a') as writeFile:
        writeFile.write(ts + ',' + db + '\n')

    writeFile.close()