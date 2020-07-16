# The script MUST contain a function named azureml_main
# which is the entry point for this module.

# imports up here can be used to
import requests
import json
import re
import pandas as pd

API_ENDPOINT = '<YOUR ENDPOINT>'
headers = {'content-type': 'application/json'}


# The entry point function MUST have two input arguments.
# If the input port is not connected, the corresponding
# dataframe argument will be None.
#   Param<dataframe1>: a pandas.DataFrame
#   Param<dataframe2>: a pandas.DataFrame
def azureml_main(dataframe1 = None, dataframe2 = None):

    
    # Execution logic goes here
    print(f'Input pandas.DataFrame #1: {dataframe1}')

    
    dataframe1.index = range(len(dataframe1))
    start_idx = 0
    batch_size = 1000
    df_len = len(dataframe1)

    end_idx = min(df_len, start_idx + batch_size)

    all_results = []
    dataframe1.replace({"NULL":"NaN"}, inplace=True)

    while start_idx < df_len:
            
        try:
            list_data = []
            for i in range(start_idx, end_idx):
                list_data.append(dataframe1.loc[i].fillna("NaN").to_dict())
            data_pt = re.sub("\'", "\"", str({ 'data': list_data}))
            
            t = requests.post(API_ENDPOINT, headers=headers, data = data_pt)
            
            all_results.extend(json.loads(t.json())['result'])
        except Exception as e:
            print ("----------- EXCEPTION ------------", e, start_idx, end_idx, data_pt)
            raise e
            
        
        start_idx += batch_size
        end_idx = min(end_idx+batch_size, df_len)

    df = pd.DataFrame({"predictions": all_results})
    
    dataframe1["predictions"] = df["predictions"].astype(str)
    
    # dataframe1["predictions"] = df["predictions"]

    # If a zip file is connected to the third input port,
    # it is unzipped under "./Script Bundle". This directory is added
    # to sys.path. Therefore, if your zip file contains a Python file
    # mymodule.py you can import it using:
    # import mymodule

    # Return value must be of a sequence of pandas.DataFrame
    # E.g.
    #   -  Single return value: return dataframe1,
    #   -  Two return values: return dataframe1, dataframe2
    return dataframe1,
