"""
HikerDistanceLinearRegression2.py
TODO: Document header.
:author: Chris Campell
:version: 11/13/2016
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split
import statsmodels.api as sm
import statsmodels.formula.api as smf

def main(input_dir, request_new_model):
    df = pd.read_csv(input_dir + "\DistancePrediction.csv")
    # Filter the data frame removing any entries with negative miles-per-day or zero-miles per day:
    df = df[df['MPD'] > 2]
    # Filter the data frame removing outliers:
    df = df[df['MPD'] <= 50]
    # Filter the data frame removing any entries with a location and no associated direction:
    df = df.loc[~df['LOCDIR'].str.endswith("UD")]
    # Convert the "LOCDIR" column from dytpe-object to dtype-category for C optimizations:
    df['LOCDIR'] = df['LOCDIR'].astype('category')
    df['HID'] = df['HID'].astype('category')
    df = df.copy()
    df_train, df_test = train_test_split(df, test_size=0.4, random_state=0)
    if request_new_model:
        ols_model = smf.ols(formula="np.log(MPD) ~ LOCDIR + HID + 1", data=df_train).fit()
        # TODO: Perform cross validation to see how accurate the model is. Use standard deviations to change opacity of
        #   overlay based on model's estimation.
        print(ols_model.params)
        print(ols_model.summary())
        y_pred = ols_model.predict(df_test)
        y_pred = np.exp(y_pred)
        # Add a column for pred_y and then use df.plot to plot the column headers. MPD vs y_pred MPD.
        df_test = df_test.copy()
        df_test['MPD_PRED'] = y_pred
        df_test.to_csv("df_test.csv")
        df_train = df_train.copy()
        df_train['MPD_PRED'] = np.exp(ols_model.predict(df_train))
        df_train.to_csv("df_train.csv")
    else:
        df_test = pd.read_csv("df_test.csv", index_col=0)
        df_train = pd.read_csv("df_train.csv", index_col=0)

        df_train.plot(kind='scatter', x='MPD', y='MPD_PRED')
        plt.title("Training Data")
        plt.show()

        df_test.plot(kind='scatter', x='MPD', y='MPD_PRED')
        plt.title("Test Data")
        plt.show()

        plt.clf()
        x_bin_edges = np.arange(0, 51, 1)
        y_bin_edges = np.arange(0, 51, 1)
        plt.hist2d(x=df_train.MPD_PRED, y=df_train.MPD, bins=[x_bin_edges, y_bin_edges], hold=True)
        plt.axis("square")
        plt.colorbar()
        ols_line_best_fit = smf.ols(formula='MPD ~ MPD_PRED + 1', data=df_train).fit()
        regression_y_max = ols_line_best_fit.predict({'MPD_PRED': max(df_train.MPD_PRED)})
        regression_y_min = ols_line_best_fit.predict({'MPD_PRED': min(df_train.MPD_PRED)})
        print("pred_reg_y_max: %d" % regression_y_max)
        print("pred_reg_y_min: %d" % regression_y_min)
        plt.plot([min(df_train.MPD_PRED), max(df_train.MPD_PRED)], [regression_y_min, regression_y_max], c='red', linewidth=2)
        plt.plot([0, 51], [0, 51], c='green', linewidth=2)
        plt.title("Training Data")
        plt.show()

        x_bin_edges = np.arange(0, 50, 1)
        y_bin_edges = np.arange(0, 25, 1)
        plt.hist2d(x=df_test.MPD, y=df_test.MPD_PRED, bins=[x_bin_edges, y_bin_edges], hold=True)
        plt.title("Test Data")
        plt.colorbar()

        ols_line_best_fit = smf.ols(formula='MPD_PRED ~ MPD + 1', data=df_test).fit()
        pred_regression_y_max = ols_line_best_fit.predict({'MPD': max(df_test.MPD)})
        pred_regression_y_min = ols_line_best_fit.predict({'MPD': min(df_test.MPD)})
        print("pred_reg_y_max: %d" % pred_regression_y_max)
        print("pred_reg_y_min: %d" % pred_regression_y_min)
        plt.plot([min(df_test.MPD), max(df_test.MPD)], [pred_regression_y_min, pred_regression_y_max], c='red', linewidth=2)
        # plt.plot([0, 50], [0, 25], c='green', linewidth=2)
        plt.show()
        # Ransac 'random subset....' can be used for removing outliers.

if __name__ == '__main__':
    hiker_journal_entry_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    main(input_dir=hiker_journal_entry_csv, request_new_model=True)
