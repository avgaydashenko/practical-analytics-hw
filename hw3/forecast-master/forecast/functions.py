import warnings
import pandas as pd
import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri as pd2
from rpy2.robjects.packages import importr
pd2.activate()
__ts = robjects.r('ts')
__forecast = importr('forecast')


def get(obj, *names, **kwargs):
    def dic(robj):
        return dict(map(lambda t: (t[1], t[0]), enumerate(robj.names)))
    for name in names:
        obj = obj[dic(obj)[name]]
    if kwargs.pop('py', False):
        obj = pd2.ri2py(obj)
        if isinstance(obj, robjects.RObjectMixin):
            raise TypeError('Failed to convert %s' % '.'.join(names))
    if kwargs.pop('list', False):
        obj = list(obj)
    return obj


def stl(series, frequency, method=None, **kwargs):
    """Does STL decomposition of given time series using R `forecast.stlm`

    Returns
    -------
    dataframe with decomposed time series
    .. Note:
        if series.name is not None:
            names have prefix `series.name`

    :param series: pd.Series instance
    :param frequency: expected frequency of series
    :param method: model for nonseasonal part
    :param kwargs: kwargs for `forecast.stlm` in R
    :return: pd.DataFrame ['seasonal', 'trend', 'e']
    """
    if not isinstance(series, pd.Series):
        raise TypeError('Wrong type, expected Series, got %s' % type(series))
    if method:
        kwargs['method'] = method
    name = series.name
    stl_names = ('seasonal', 'trend', 'e')
    if name:
        stl_names = tuple(map(lambda s: '%s_%s' % (name, s), stl_names))
    r_ts = __ts(series, frequency=frequency)
    r_stl = __forecast.stlm(r_ts, **kwargs)
    return pd.DataFrame(get(r_stl, 'stl', 'time.series', py=True),
                        columns=stl_names, index=series.index)


def forecast(series, frequency, h=None, method=None,
             stlkwargs=None, trend=True, **kwargs):
    """Does forcasting for given time series using R `forecast.stlf`

    Returns
    -------
    dataframe with forecasting mean and confidence intervals
    .. Note:
        if series.name is not None:
            names have prefix `series.name`

    :param series: pd.Series instance
    :param frequency: expected frequency of series
    :param h: forecasting steps
    :param method: model for nonseasonal part
    :param trend: do forecast for trend too?
    :param kwargs: kwargs for `forecast.forecast` in R
    :param stlkwargs: kwargs for `forecast.stlm` in R
    :return: pd.DataFrame ['forecast', 'l80', 'l95, 'u80', 'u95']
    """
    if not isinstance(series, pd.Series):
        raise TypeError('Wrong type, expected Series, got %s' % type(series))
    stlkwargs = stlkwargs or dict()
    if method:
        kwargs['method'] = method
        if method not in stlkwargs:
            stlkwargs['method'] = method
    if h is None:
        h = max(frequency, 10)
    if series.name:
        name = series.name + '_'
    else:
        name = ''
    r_ts = __ts(series, frequency=frequency)
    r_stl = __forecast.stlm(r_ts, **stlkwargs)
    r_fc = __forecast.forecast(r_stl, h=h, **kwargs)
    mean = pd.Series(get(r_fc, 'mean', py=True), name=name + 'forecast')
    lower = pd.DataFrame(get(r_fc, 'lower', py=True),
                         columns=(name + 'l80', name + 'l95'))
    upper = pd.DataFrame(get(r_fc, 'upper', py=True),
                         columns=(name + 'u80', name + 'u95'))
    future = pd.concat([mean, lower, upper], 1)  # type: pd.DataFrame
    if trend:
        _seasonal = get(r_fc, 'seasonal', list=True)
        seasonal = pd.Series((_seasonal * (h // frequency) +
                              _seasonal[:h % frequency])
                             )
        trend = future.apply(lambda s: s - seasonal)
        trend.rename(columns=lambda n: n + '_trend', inplace=True)
        future = pd.concat([future, trend], 1)
    if isinstance(series.index, pd.DatetimeIndex):
        newindex = pd.DatetimeIndex(
            start=series.index[-1],
            periods=h,
            freq=series.index.inferred_freq)
        future.index = newindex.shift(1)
    else:
        warnings.warn('Index cannot be continued!')
    return future


def stldf(df, frequency, method=None, **kwargs):
    """Does STL decomposition for every column of
    given data frame using R `forecast.stlm`

    Returns
    -------
    dataframe with forecasting mean and confidence intervals
    .. Note:
        new columns have prefix `column.name`

    :param df: pd.DataFrame
    :param frequency: expected frequency of series(it is common
        for all of them)
    :param method: model for nonseasonal part
    :param kwargs: kwargs for `forecast.stlm` in R
    :return: pd.DataFrame [columns -> ['old', 'seasonal', 'trend', 'e']]
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError('Wrong type, expected DataFrame, got %s' % type(df))
    stls = [stl(series, frequency, method=method, **kwargs)
            for key, series in df.iteritems()]

    return pd.concat([df] + stls, 1)


def bind(cls, *exts):
    for ext in exts:
        setattr(cls, ext.__name__, ext)
