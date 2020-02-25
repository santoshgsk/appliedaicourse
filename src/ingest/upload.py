import re
import os
import pandas as pd
import numpy as np
import pyodbc 
from azure.storage.blob import BlockBlobService, PublicAccess

class UploadDataToSql:

    def __init__(self, server, database, username, password, driver):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.driver = driver
        self.BLOB_SOURCE = "BlobDataSource"
        
    def connect_to_db(self):
        conn_string = f'DRIVER={self.driver};PORT=1433;'
        conn_string += f'SERVER={self.server};DATABASE={self.database};'
        conn_string += f'UID={self.username};PWD={self.password}'
        cnxn = pyodbc.connect(conn_string)
        cursor = cnxn.cursor()
        return cursor
    
    def extract_table_name(self, filename, ignore_keywords):
        
        filename = filename.split(os.path.sep)[-1]
        filename = filename.split('.')[0]
        for keyword in ignore_keywords:
            filename = re.sub(f'[-_]?{keyword}[-_]?', "", filename)
        return filename

    def find_dtype(self, df, col):
        try:
            float_val = df[col].astype(float)

            try:
                int_val = df[col].astype(int)
                if sum(float_val-int_val) == 0:
                    return df[col].astype(int)
            except:
                return df[col].astype(float)
        except:
            try:
                c = pd.to_datetime(df[col])
                return c
            except:
                try:
                    d = pd.to_timedelta(df[col])
                    return d
                except:
                    return df[col].astype(str)
    

    def get_sql_for_creation(self, table_name, df, varchar_limit):
        create_table_sql = '''IF NOT EXISTS (select * 
            from information_schema.tables where table_type='base table'
            and table_catalog='{0}' and table_name='{1}')
            BEGIN '''.format(self.database, table_name)
        create_table_sql += f'CREATE TABLE {table_name} ('
        for c in df.columns:
            if df[c].dtype == np.dtype('<M8[ns]'):
                create_table_sql += f'{c} DATETIME2,'
            elif df[c].dtype == np.dtype('object'):
                create_table_sql += f'{c} VARCHAR({varchar_limit}),'
            elif df[c].dtype == np.dtype('int64'):
                create_table_sql += f'{c} INT,'
            elif df[c].dtype == np.dtype('float64'):
                create_table_sql += f'{c} FLOAT,'
        create_table_sql += ') END'
        return create_table_sql

    def create_table(self, table_name, df, varchar_limit):
        sql = self.get_sql_for_creation(table_name, df, varchar_limit)
        print ("sql ", sql)
        cursor = self.connect_to_db()
        cursor.execute(sql)
        cursor.commit()
        cursor.close()
    
    def bulk_upload(self, table, filename):
        bulk_insert = '''BULK INSERT {table} 
                    FROM '{filename}' 
                    WITH (DATA_SOURCE = '{blob_source}',
                    FIRSTROW = 2,
                    FORMAT = 'CSV',
                    FIELDTERMINATOR = ',',
                    ROWTERMINATOR = '0x0a');'''.format(
                        table = table,
                        blob_source = self.BLOB_SOURCE,
                        filename = filename
                    )
        cursor = self.connect_to_db()
        cursor.execute(bulk_insert)
        cursor.commit()
        cursor.close()
        
    def upload_csv_to_database(self, filename, blob_filename, ignore_keywords=['dataset'], varchar_limit=2000):
        
        df = pd.read_csv(filename)
        for col in df.columns:
            df[col] = self.find_dtype(df, col)
        
        table_name = self.extract_table_name(filename, ignore_keywords)
        
        print ("table_name", table_name)
        
        self.create_table(table_name, df, varchar_limit)
        self.bulk_upload(table_name, blob_filename)

    def create_blob_source(self, storage_sas_token, blob_url):

        cursor = self.connect_to_db()
        cursor.execute('''select * from sys.external_data_sources 
                    where name='{0}';'''.format(self.BLOB_SOURCE))
        res = len(cursor.fetchall())
        if res > 0:
            cursor.close()
            return ('''The BLOB source is already created! In order to change it call <your_upload_sql_object>.BLOB_SOURCE = <new_name>''')

        sql1 = '''IF NOT EXISTS 
                        (SELECT COUNT(*) 
                        FROM sys.symmetric_keys 
                        WHERE name LIKE '%DatabaseMasterKey%')
                BEGIN
                    CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'applied$123';
                END;'''
        sql2 = '''IF NOT EXISTS 
                    (select * 
                    from sys.database_scoped_credentials 
                    where name like '%MyAzureBlobStorageCredential%')
                BEGIN
                    CREATE DATABASE SCOPED CREDENTIAL MyAzureBlobStorageCredential
                    WITH IDENTITY = 'SHARED ACCESS SIGNATURE',
                    SECRET = '{0}';
                END;'''.format(storage_sas_token)
        sql3 = '''CREATE EXTERNAL DATA SOURCE {0}
                WITH ( TYPE = BLOB_STORAGE, LOCATION = '{1}',
                CREDENTIAL= MyAzureBlobStorageCredential);'''.format(self.BLOB_SOURCE, blob_url)
        
        cursor.execute(sql1)
        cursor.execute(sql2)
        cursor.execute(sql3)
        cursor.commit()
        cursor.close()
    


class UploadDataToBlob:

    def __init__(self, container_connection_str, container_acc, container_key, container_name):
        self.container_acc = container_acc
        os.environ['AZURE_STORAGE_CONNECTION_STRING'] = container_connection_str
        self.container_key = container_key
        self.container_name = container_name
    
    def upload_blob(self, filename, filepath):
        blob_service_client = BlockBlobService(account_name=self.container_acc, account_key=self.container_key)
        blob_service_client.set_container_acl(self.container_name, public_access=PublicAccess.Container)
        blob_service_client.create_blob_from_path(self.container_name, filename, filepath)

