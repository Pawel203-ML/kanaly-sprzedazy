import pandas as pd
import datetime as dt
import os
import numpy as np

class db:
    def __init__(self):
        self.transactions = db.transation_init()
        self.cc = pd.read_csv(r'db\country_codes.csv',index_col=0)
        self.customers = pd.read_csv(r'db\customers.csv',index_col=0)
        self.prod_info = pd.read_csv(r'db\prod_cat_info.csv')

    @staticmethod
    def transation_init():
        transactions = pd.DataFrame()
        transactions_list = [] 
        src = r'db\transactions'
        
        for filename in os.listdir(src):
            filepath = os.path.join(src, filename)
            transactions_list.append(pd.read_csv(filepath, index_col=0))
        
        transactions = pd.concat(transactions_list, ignore_index=True)

        return transactions
    
    #tworzy nam cala tabele danych wyciagnietych z plikow
    def merge(self):
        df = self.transactions.join(self.prod_info.drop_duplicates(subset=['prod_cat_code'])
        .set_index('prod_cat_code')['prod_cat'],on='prod_cat_code',how='left')

        df = df.join(self.prod_info.drop_duplicates(subset=['prod_sub_cat_code'])
        .set_index('prod_sub_cat_code')['prod_subcat'],on='prod_subcat_code',how='left')

        df = df.join(self.customers.join(self.cc,on='country_code')
        .set_index('customer_Id'),on='cust_id')

        self.merged = df

def init():
    df = db()
    df.merge()

    return df.merged


if __name__ == '__main__':
    print(init())
    
