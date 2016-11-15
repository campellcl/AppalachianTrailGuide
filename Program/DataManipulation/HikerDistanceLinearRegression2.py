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
    df = df[df['MPD'] > 0]
    # Filter the data frame removing any entries with a location and no associated direction:
    df = df.loc[~df['LOCDIR'].str.endswith("UD")]
    # Convert the "LOCDIR" column from dytpe-object to dtype-category for C optimizations:
    df['LOCDIR'] = df['LOCDIR'].astype('category')
    df['HID'] = df['HID'].astype('category')
    df = df.copy()
    df_train, df_test = train_test_split(df, test_size=0.4, random_state=0)
    if request_new_model:
        ols_model = smf.ols(formula="np.log(MPD) ~ LOCDIR + HID + 1", data=df_train).fit()
        y_pred = ols_model.predict(df_test)
        y_pred = np.exp(y_pred)
        # Add a column for pred_y and then use df.plot to plot the column headers. MPD vs y_pred MPD.
        df_test = df_test.copy()
        df_test['MPD_PRED'] = y_pred
        df_test.to_csv("df_test.csv")
    else:
        df_test = pd.read_csv("df_test.csv", index_col=0)
        df_test.plot(kind='scatter', x='MPD', y='MPD_PRED')
        # plt.plot(df_test.MPD, df_test.MPD_PRED, c='red', linewidth=2)
        plt.show()
        # TODO: Save the data that is plotted in the histogram for a quick load.
        plt.clf()
        # df.to_csv(df_test)
        # df = df.read_csv(df_test)
        x_bin_edges = np.arange(0, 50, 1)
        y_bin_edges = np.arange(0, 25, 1)
        plt.hist2d(x=df_test.MPD, y=df_test.MPD_PRED,bins=[x_bin_edges, y_bin_edges], hold=True)
        plt.colorbar()
        # plt.show()
        # plt.hold(True)
        ols_line_best_fit = smf.ols(formula='MPD_PRED ~ MPD + 1', data=df_test).fit()
        pred_regression_y_max = ols_line_best_fit.predict({'MPD': max(df_test.MPD)})
        pred_regression_y_min = ols_line_best_fit.predict({'MPD': min(df_test.MPD)})
        print("pred_reg_y_max: %d" % pred_regression_y_max)
        print("pred_reg_y_min: %d" % pred_regression_y_min)
        plt.plot([min(df_test.MPD), max(df_test.MPD)], [pred_regression_y_min, pred_regression_y_max], c='red', linewidth=2)
        # TODO: Predict y associated with min_x and max_x and draw a line between two points.
        plt.show()
        # Ransac 'random subset....' can be used for removing outliers.

if __name__ == '__main__':
    hiker_journal_entry_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    main(input_dir=hiker_journal_entry_csv, request_new_model=False)
