"""
HikerDistanceLinearRegression.py
Creates a Linear Model using Least Squares Linear Regression for estimating hiker distance given a
    shelter, user-pace, and direction.
:author: Chris Campell
:version: 10/6/2016
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
main -Main method for HikerDistanceLinearRegression; calculates a Least Squares Regression Model for Hiker Distance
"""
def main(input_dir):
    df = pd.read_csv(input_dir + "\DistancePrediction.csv")
    # There should be a 1 in a column for each row.
    df = pd.DataFrame(data=df)
    print("Number of one's in each row: %s" % ((df == 1).sum(axis=1)))
    '''
    ones = ((df == 1).sum(axis=1))
    for row in ones:
        num_ones = 0
        for element in row:
            if element == 1:
                num_ones += 1
        print("Number of one's in row %d: " % num_ones)
    print(df.head())
    '''


if __name__ == '__main__':
    hiker_journal_entry_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    main(input_dir=hiker_journal_entry_csv)
