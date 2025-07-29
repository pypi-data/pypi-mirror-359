import pandas as pd
from .BaseExtractor import BaseExtractor


class PurchasingPowerExtractor(BaseExtractor):
    def __init__(self):
        pass;


    @staticmethod 
    def extract(df, grouped_columns, revenue_column):
        _df = df[grouped_columns + [revenue_column]];
        purchasing_power_fts = _df.groupby(by=grouped_columns)\
                                    .agg(\
                                        _total_revenue = (revenue_column, "sum"), \
                                        _aov = (revenue_column, "mean"),\
                                        _median_ov = (revenue_column, "median")
                                    )\
                                    .reset_index();
        purchasing_power_fts['_percentage_rank'] = purchasing_power_fts._total_revenue.rank(pct=True)

        return purchasing_power_fts;
        









    pass




