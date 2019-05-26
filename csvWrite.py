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

def cameraCount(total):
    ttl = total
    print("ttl: " + str(ttl))

    # current time and print it
    dt = str(datetime.datetime.now())
    print("dt: " + str(dt))

    row = [dt, ttl]

    with open('camera.csv', 'a') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(row)

    writeFile.close()
