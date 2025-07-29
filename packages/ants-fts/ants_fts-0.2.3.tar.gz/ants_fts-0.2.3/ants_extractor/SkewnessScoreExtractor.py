import pandas
from .BaseExtractor import BaseExtractor


class SkewnessScoreExtractor(BaseExtractor):

    def __init__(self):
        pass

    def extract(df, grouped_columns, column):

        basic_agg_df = df.groupby(by=grouped_columns)\
                         .agg(\
                             mean_ = (column, 'mean'), \
                             std_  = (column, 'std'),\
                             cnt_ = (column, 'count'))\
                         .reset_index();

        merged_df = df[grouped_columns + [column]].merge(basic_agg_df, on=grouped_columns);
        merged_df = merged_df[merged_df.cnt_ > 2];

        _1st_part = merged_df.cnt_ / ((merged_df.cnt_-1)*(merged_df.cnt_-2));
        _2nd_part = ((merged_df[column] - merged_df.mean_)/merged_df.std_)**3;

        merged_df['_skewness_score'] = _1st_part * _2nd_part;
        scored_df = merged_df.groupby(by=grouped_columns).agg(_skewness_score = ("_skewness_score", "sum")).reset_index();

        return scored_df;
    pass




