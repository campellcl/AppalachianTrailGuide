"""

"""

import os
import numpy as np
import pandas as pd
from sklearn.cross_validation import train_test_split
import statsmodels.formula.api as smf
import statsmodels.api as sm

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
        '''
        ols_model = smf.ols(formula='np.log(MPD) ~ LOCDIR + HID + 1', data=df_train).fit()
        '''
        # Extract x_test and y_test from the design matrix as np.array's endog and exog:
        endog_test = np.log(df_test['MPD'].values)
        exog_test = df_test[['LOCDIR','HID']].values
        # Predict y-pred using the test data:
        '''
        y_pred = ols_model.predict(df_test)
        y_pred = np.exp(y_pred)
        print("OLS model params:")
        print(ols_model.params)
        print("OLS model summary:")
        print(ols_model.summary())
        '''
        # TODO: Convert data to categorical data:
        categorical_cols_to_retain = ['LOCDIR','HID']
        categorical_df = df_train[categorical_cols_to_retain]
        categorical_dict = categorical_df.T.to_dict().values()

        # Create the design matrix from the df_test data frame:
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
