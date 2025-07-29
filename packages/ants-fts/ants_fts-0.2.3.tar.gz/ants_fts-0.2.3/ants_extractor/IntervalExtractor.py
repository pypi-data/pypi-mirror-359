# ants_extractor/IntervalExtractor.py
import pandas as pd
from .BaseExtractor import BaseExtractor

class IntervalExtractor(BaseExtractor):
    

    def __init__(self):
        #self.feature_name = name;

        pass;
    @staticmethod
    def extract(df, grouped_columns, key_date_column):
        cols = grouped_columns + [key_date_column];
        interval_fts_df = df[cols];
        interval_fts_df[key_date_column] = pd.to_datetime(interval_fts_df[key_date_column], format = "%Y-%m-%d %H:%M:%S", errors='coerce');
        interval_fts_df = interval_fts_df.drop_duplicates().sort_values(by=cols, ascending=[True]*len(cols));
        interval_fts_df['interval'] = interval_fts_df.groupby(by=grouped_columns)[key_date_column].diff().dt.total_seconds()/(24*3600);
        
        itv_fts = interval_fts_df.groupby(by=grouped_columns)\
                                 .agg(\
                                       _cnt = (key_date_column,"count"),
                                       _avg_itv = ('interval', 'mean'),
                                       _var_itv = ('interval', 'var'),
                                       _min_itv = ('interval', 'min'),
                                       _max_itv = ('interval', 'max')
                                     )\
                                 .reset_index();
        #itv_fts = itv_fts[itv_fts._cnt>2];
        return itv_fts;





