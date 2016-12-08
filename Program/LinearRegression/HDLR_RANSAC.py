"""
HDLR_RANSAC.py
Implementation of the Random Sample Consensus (RANSAC) Hiker Distance Linear Regression algorithm for predicting hiker
    distance in miles-per-day along the Appalachian Trail.
:author: Chris Campell
:version: 11/15/2016
"""
__author__ = "Chris Campell"
__version__ = "11/15/2016"

import os
import numpy as np
import pandas as pd
from sklearn.cross_validation import train_test_split
import statsmodels.formula.api as smf
import statsmodels.api as sm
from statsmodels.tools.eval_measures import rmse
import matplotlib.pyplot as plt

def main(input_data_dir, model_storage_dir):

    model_data_frame_storage_file_name = 'df_test.csv'
    # Check to see if the model exists already:
    if model_data_frame_storage_file_name not in os.listdir(model_storage_dir):
        print("Model stored in LinearRegression\df_test.csv not found! Generating new model...")
        df = pd.read_csv(input_data_dir + "\DistancePrediction.csv")
        # Perform filtering on the data frame; remove any training data MPD less than zero or greater than 50:
        df = df[df['MPD'] > 0]
        df = df[df['MPD'] <= 50]
        # Perform filtering on the data frame; remove any entries with a location and no associated direction:
        df = df.loc[~df['LOCDIR'].str.endswith("UD")]
        # Perform dtype conversions so that the model does not treat categorical data as a numeric predictor:
        df['LOCDIR'] = df['LOCDIR'].astype('category')
        df['HID'] = df['HID'].astype('category')
        # Update the representation of the data frame in memory:
        df = df.copy()
        # Partition the data frame into train-test splits:
        df_train, df_test = train_test_split(df, test_size=0.4, random_state=0)
        # Create OLS Regression model post-outlier removal:
        ols_model = smf.ols(formula='np.log(MPD) ~ LOCDIR + HID + 1', data=df_train).fit()
        y_pred = ols_model.predict(df_test)
        y_pred = np.exp(y_pred)
        # Add a column to the test data frame for the MPD predicted by the model:
        df_test = df_test.copy()
        df_test['OLS_MPD_PRED'] = y_pred
        df_train = df_train.copy()
        df_train['intercept'] = 1
        endog_train = np.log(df_train['MPD'].values)
        exog_train = df_train[['LOCDIR', 'HID', 'intercept']].values
        # Create the design matrix from the df_test dataframe:
        # rlm_model = sm.RLM(endog=endog_train, exog=exog_train, M=sm.robust.norms.LeastSquares())
        # rlm_results = rlm_model.fit()
        df_test.to_csv("df_test.csv")
        df_train.to_csv("df_train.csv")
        root_mean_squared_error = rmse(y_pred, df_test['MPD'])
        print("Model RMSE (In Miles-Per-Day): %d" % root_mean_squared_error)
    else:
        print("Stored model found, loading and utilizing saved model...")
        df_test = pd.read_csv("df_test.csv", index_col=0)
        df_train = pd.read_csv("df_train.csv", index_col=0)
        df_test.plot(kind='scatter', x='MPD', y='OLS_MPD_PRED')
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

if __name__ == '__main__':
    hiker_journal_entry_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    storage_dir = os.path.dirname(__file__)
    main(input_data_dir=hiker_journal_entry_csv_path,model_storage_dir=storage_dir)
