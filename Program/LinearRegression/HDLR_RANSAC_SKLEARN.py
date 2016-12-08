"""

"""

import os
import numpy as np
import pandas as pd
from sklearn.cross_validation import train_test_split
from sklearn import linear_model

def main(input_data_dir, model_storage_dir):

    model_data_frame_storage_file_name = 'df_test.csv'
    # Check to see if the model exists already:
    if model_data_frame_storage_file_name not in os.listdir(model_storage_dir):
        print("Model stored in DataManipulation\df_test.csv not found! Generating new model...")
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
        # Extract x_train and y_train from the design matrix as np.array's endog and exog:
        endog_train = np.log(df_train['MPD'].values)
        df_train = df_train.copy()
        df_train['intercept'] = 1
        exog_train = df_train[['LOCDIR', 'HID', 'intercept']].values
        # Create OLS Regression model post-outlier removal:
        sklearn_ols_model = linear_model.LinearRegression()
        sklearn_ols_model.fit(X=exog_train, y=endog_train)
        # Extract x_test and y_test from the design matrix as np.array's endog and exog:
        endog_test = np.log(df_test['MPD'].values)
        exog_test = df_test[['LOCDIR','HID','intercept']].values
        # Predict y-pred using the test data:
        y_pred = sklearn_ols_model.predict(X=endog_test)
        y_pred = np.exp(y_pred)
        print("OLS model results:")
        print(sklearn_ols_model.coef_)
        # Add a column to the test data frame for the MPD predicted by the model:
        df_test = df_test.copy()
        df_test['OLS_MPD_PRED'] = y_pred
        df_train = df_train.copy()
        df_train['intercept'] = 1
        endog_train = np.log(df_train['MPD'].values)
        exog_train = df_train[['LOCDIR', 'HID', 'intercept']].values
        # Create the design matrix from the df_test dataframe:
        rlm_model = sm.RLM(endog=endog_train, exog=exog_train, M=sm.robust.norms.LeastSquares())
        rlm_results = rlm_model.fit()
        df_test.to_csv("df_test.csv")
    else:
        print("Stored model found, loading and utilizing saved model...")
        df_test = pd.read_csv("df_test.csv", index_col=0)

if __name__ == '__main__':
    hiker_journal_entry_csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'Data/HikerData/'))
    storage_dir = os.path.dirname(__file__)
    main(input_data_dir=hiker_journal_entry_csv_path,model_storage_dir=storage_dir)
