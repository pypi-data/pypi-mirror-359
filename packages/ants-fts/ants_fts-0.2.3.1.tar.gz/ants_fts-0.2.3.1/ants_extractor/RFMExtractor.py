import pandas as pd
from .BaseExtractor import BaseExtractor

class RFMExtractor(BaseExtractor):

    def __init__(self):
        pass

    @staticmethod
    def extract(df, grouped_columns, key_date_column, revenue_column, reference_date):
        _df = df[grouped_columns + [key_date_column, revenue_column]];
        _df[key_date_column] = pd.to_datetime(_df[key_date_column], format="%Y-%m-%d %H:%M:%S", errors = "coerce");
        reference_date = pd.to_datetime(reference_date, format="%Y-%m-%d %H:%M:%S", errors = "coerce");
        recency_fts = _df.groupby(by=grouped_columns)\
                        .agg(\
                                _max_dt = (key_date_column, "max"),\
                                _frequency = (key_date_column, "count"),\
                                _monetary = (revenue_column, "sum")
                            )\
                        .reset_index();
        recency_fts['_recency'] = (reference_date - recency_fts._max_dt).dt.total_seconds()/86400;
        recency_fts = recency_fts[grouped_columns + ['_recency', '_frequency', '_monetary']];
        return recency_fts;
    pass

