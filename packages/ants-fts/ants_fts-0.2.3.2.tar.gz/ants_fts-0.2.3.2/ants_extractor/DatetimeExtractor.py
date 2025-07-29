import pandas as pd
from datetime import datetime, timedelta
from .BaseExtractor import BaseExtractor

"""
LIST OF FEATURES
_weekend_rate
_weekday_rate
_monday_rate
_tuesday_rate
_wednesday_rate
_thurday_rate
_friday_rate
_saturday_rate
_sunday_rate
_am_rate
_pm_rate
_dawn_rate
_morning_rate
_afternoon_rate
_evening_rate
_midnight_rate
"""
def get_weekend_rate(group):
    x = (group >= 5).sum();
    return x/group.shape[0];

def get_weekday_rate(group):
    x = (group < 5).sum();
    return x/group.shape[0];

class DatetimeExtractor(BaseExtractor):

    def __init__(self):
        pass;

    @staticmethod
    def extract(df, grouped_columns, key_date_column):
        df[key_date_column] = pd.to_datetime(df[key_date_column], errors='coerce');
        _df = df[grouped_columns + [key_date_column]];
        _df['day_of_week'] = _df[key_date_column].dt.dayofweek;
        _df['weekend'] = (_df.day_of_week>4).astype(int);
        _df['weekday'] = (_df.day_of_week<5).astype(int);
        _df['monday' ] = (_df.day_of_week==0).astype(int);
        _df['tuesday'] = (_df.day_of_week==1).astype(int);
        _df['wednesday'] = (_df.day_of_week==2).astype(int);
        _df['thurday'] = (_df.day_of_week==3).astype(int);
        _df['friday'] = (_df.day_of_week==4).astype(int);
        _df['saturday'] = (_df.day_of_week==5).astype(int);
        _df['sunday'] = (_df.day_of_week==6).astype(int);
        _df['hour'] = _df[key_date_column].dt.hour;
        _df['am'] = (_df.hour <  12).astype(int);
        _df['pm'] = (_df.hour >= 12).astype(int);
        _df['dawn'] = ((_df.hour >= 1)&(_df.hour < 6)).astype(int);
        _df['morning'] = ((_df.hour >= 6)&(_df.hour < 12)).astype(int);
        _df['afternoon'] = ((_df.hour >= 12)&(_df.hour < 18)).astype(int);
        _df['evening'] = ((_df.hour >= 18)&(_df.hour < 22)).astype(int);
        _df['midnight'] = ((_df.hour >= 22)|(_df.hour < 1)).astype(int);
        _grouped_df = _df.groupby(by=grouped_columns)\
                            .agg(\
                                    cnt = (key_date_column, "count"),\
                                    weekend = ("weekend", "sum"),\
                                    weekday = ("weekday", "sum"),\
                                    monday = ("monday", "sum"),\
                                    tuesday = ("tuesday", "sum"),\
                                    wednesday = ("wednesday", "sum"),\
                                    thurday = ("thurday", "sum"),\
                                    friday = ("friday", "sum"),\
                                    saturday = ("saturday", "sum"),\
                                    sunday = ("sunday", "sum"),\
                                    am = ("am", "sum"),\
                                    pm = ("pm", "sum"),\
                                    dawn = ("dawn", "sum"),\
                                    morning = ("morning", "sum"),\
                                    afternoon = ("afternoon", "sum"),\
                                    evening = ("evening", "sum"),\
                                    midnight = ("midnight", "sum")\
                                    )\
                            .reset_index();
        _grouped_df['_weekend_rate'] = _grouped_df.weekend/_grouped_df.cnt
        _grouped_df['_weekday_rate'] = _grouped_df.weekday/_grouped_df.cnt
        _grouped_df['_monday_rate'] = _grouped_df.monday/_grouped_df.cnt
        _grouped_df['_tuesday_rate'] = _grouped_df.tuesday/_grouped_df.cnt
        _grouped_df['_wednesday_rate'] = _grouped_df.wednesday/_grouped_df.cnt
        _grouped_df['_thurday_rate'] = _grouped_df.thurday/_grouped_df.cnt
        _grouped_df['_friday_rate'] = _grouped_df.friday/_grouped_df.cnt
        _grouped_df['_saturday_rate'] = _grouped_df.saturday/_grouped_df.cnt
        _grouped_df['_sunday_rate'] = _grouped_df.sunday/_grouped_df.cnt
        _grouped_df['_am_rate'] = _grouped_df.am/_grouped_df.cnt
        _grouped_df['_pm_rate'] = _grouped_df.pm/_grouped_df.cnt
        _grouped_df['_dawn_rate'] = _grouped_df.dawn/_grouped_df.cnt
        _grouped_df['_morning_rate'] = _grouped_df.morning/_grouped_df.cnt
        _grouped_df['_afternoon_rate'] = _grouped_df.afternoon/_grouped_df.cnt
        _grouped_df['_evening_rate'] = _grouped_df.evening/_grouped_df.cnt
        _grouped_df['_midnight_rate'] = _grouped_df.midnight/_grouped_df.cnt
        fts_names = ['_weekend_rate', '_weekday_rate', \
            '_monday_rate', '_tuesday_rate', \
            '_wednesday_rate', '_thurday_rate', \
            '_friday_rate', '_saturday_rate', '_sunday_rate', \
            '_am_rate', '_pm_rate', \
            '_dawn_rate', '_morning_rate', '_afternoon_rate', '_evening_rate', '_midnight_rate'];
        dt_fts = _grouped_df[grouped_columns + fts_names];
        return dt_fts;









    pass




