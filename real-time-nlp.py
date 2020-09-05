# The script MUST contain a function named azureml_main
# which is the entry point for this module.

# imports up here can be used to
import re
import pandas as pd

# The entry point function MUST have two input arguments.
# If the input port is not connected, the corresponding
# dataframe argument will be None.
#   Param<dataframe1>: a pandas.DataFrame
#   Param<dataframe2>: a pandas.DataFrame
def azureml_main(dataframe1 = None, dataframe2 = None):

    # Execution logic goes here
    print(f'Input pandas.DataFrame #1: {dataframe1}')

    test_columns = dataframe2.columns

    test_ngrams = list(filter(lambda x: re.findall('Preprocessed.[^\.]*\.\[.[^\]]*\]',  x), test_columns))
    test_vocab = [re.sub("[\[\]]", "", re.findall('\[.[^\]]*\]', x)[0]) for x in test_ngrams]

    train_vocab = dataframe1["NGram"][:-1].values
    train_vocab_full_format = [re.sub(test_vocab[0], new_col, test_ngrams[0]) for new_col in train_vocab]
    need_to_add = list(set(train_vocab_full_format) - set(test_ngrams))
    need_to_delete = list(set(test_ngrams) - set(train_vocab_full_format))
    
    dataframe2.drop(need_to_delete, axis=1, inplace=True)
    for new_col in need_to_add:
        dataframe2[new_col] = 0

    test_new_cols = []
    for x in test_columns:
        if (x not in train_vocab_full_format) and (x not in test_ngrams):
            test_new_cols.append(x)

    test_new_cols.extend(train_vocab_full_format)
    new_test_df = dataframe2[test_new_cols]
    # If a zip file is connected to the third input port,
    # it is unzipped under "./Script Bundle". This directory is added
    # to sys.path. Therefore, if your zip file contains a Python file
    # mymodule.py you can import it using:
    # import mymodule

    # Return value must be of a sequence of pandas.DataFrame
    # E.g.
    #   -  Single return value: return dataframe1,
    #   -  Two return values: return dataframe1, dataframe2
    return new_test_df,
