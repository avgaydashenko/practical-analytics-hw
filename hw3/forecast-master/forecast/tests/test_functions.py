from __future__ import absolute_import
import unittest
import pandas as pd
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri as pd2
from rpy2.robjects.packages import importr
from forecast.functions import stl, stldf, forecast
pd2.activate()
_ts = robjects.r('ts')
_forecast = importr('forecast')


class TestFunctions(unittest.TestCase):
    def setUp(self):
        robjects.r.data('UKgas')
        self.data = pd.Series(
                robjects.r['UKgas'],
                index=pd.date_range(pd.datetime.now(),
                                    periods=len(robjects.r['UKgas'])))
        self.data.index = pd.to_datetime(self.data.index)

    def test_stl(self):
        stl(self.data, frequency=4)
        stl(self.data, frequency=4, method='arima')

    def test_stldf(self):
        df = pd.DataFrame()
        df['one'] = self.data
        df['two'] = self.data
        stldf(df, frequency=4)
        stldf(df, frequency=4, method='arima')

    def test_forecast(self):
        forecast(self.data, frequency=4, method='arima')
        forecast(self.data, frequency=4)
