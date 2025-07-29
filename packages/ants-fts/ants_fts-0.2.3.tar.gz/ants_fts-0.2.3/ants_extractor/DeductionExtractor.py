import pandas as pd
import numpy as np
from .BaseExtractor import BaseExtractor



class DeductionExtractor(BaseExtractor):
    
    def __init__(self):

        pass;


    @staticmethod
    def extract(df, grouped_columns, discount_amount_column, revenue_column):
        _df = df[grouped_columns + [discount_amount_column, revenue_column]];
        # Calculate and validate discount rate
        _df["discount_rate"] = np.minimum(
                _df[discount_amount_column] / _df[revenue_column].replace(0, 100).fillna(100),
                1
            )
        _df['is_discount'] = (_df['discount_rate']>0).astype(int);
        #print(_df)
        deduction_fts = _df.groupby(by=grouped_columns)\
                            .agg(\
                                _cnt = (discount_amount_column, "count"),\
                                _avg_discount = ('discount_rate', 'mean'),\
                                _var_discount = ('discount_rate', 'var'),\
                                _discount_cnt = ('is_discount', 'sum'),\
                                _sum_discount = ('discount_rate', 'sum'),\
                                _min_discount = ('discount_rate', 'min'),\
                                _max_discount = ('discount_rate', 'max')
                            )\
                            .reset_index();
        # Caculate and validate the value of deduction rate
        deduction_fts["_deduction_rate"] = np.where(
                deduction_fts["_discount_cnt"] == 0,
                0,
                deduction_fts["_sum_discount"] / deduction_fts["_discount_cnt"]
            )
        deduction_fts["_deduction_rate"] = np.minimum(deduction_fts["_deduction_rate"], 1)
        #Caculate and validate the value of deduction ratio
        deduction_fts["_deduction_ratio"] = np.where(
                deduction_fts["_cnt"] == 0,
                0,
                deduction_fts["_discount_cnt"]/deduction_fts["_cnt"]
            )
        deduction_fts["_deduction_ratio"] = np.minimum(deduction_fts["_deduction_ratio"], 1)
        #Return
        deduction_fts = deduction_fts[grouped_columns + ["_deduction_rate", "_deduction_ratio", "_avg_discount", "_var_discount", "_min_discount", "_max_discount", "_discount_cnt"]]
        return deduction_fts;

    pass




