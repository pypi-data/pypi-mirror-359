# utils/indicators.py
import pandas as pd
import numpy as np
import pandas_ta as ta
from .data_utils import get_data

# inner function
def standardize_column_names(df):
    """
    데이터프레임의 컬럼명을 소문자로 표준화하는 함수입니다.
    
    Parameters
    ----------
    df : pandas.DataFrame
        표준화할 데이터프레임
        
    Returns
    -------
    pandas.DataFrame
        컬럼명이 표준화된 데이터프레임
    """
    column_mapping = {
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Open': 'open',
        'Volume': 'volume',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'open': 'open',
        'volume': 'volume'
    }
    
    df = df.copy()
    df.columns = [column_mapping.get(col, col.lower()) for col in df.columns]
    return df

def calculate_wilders_ma(series, length):
    """Calculate Wilders Moving Average."""
    wilders = pd.Series(0.0, index=series.index)
    wilders.iloc[length - 1] = series.iloc[:length].mean()
    for i in range(length, len(series)):
        wilders.iloc[i] = (wilders.iloc[i - 1] * (length - 1) + series.iloc[i]) / length
    return wilders

# outer function
def get_candle_signal(symbol, interval, increse_rate=5, start=None, end=None, get_data_type='futures'):
    df = get_data(symbol, interval, start=start, end=end, data_type=get_data_type)
    df['pct_change'] = df['close'].pct_change().mul(100)
    df['ema5']=ta.ema(df['close'],length=5)
    df['ema10']=ta.ema(df['close'],length=10)
    df['ema20']=ta.ema(df['close'],length=20)
    df['ema60']=ta.ema(df['close'],length=60)
    df['ema120']=ta.ema(df['close'],length=120)
    if increse_rate >=10:
        signal_condition = (df['ema5'] > df['ema10']) & (df['ema10'] > df['ema20']) & (df['ema20'] > df['ema60']) & (df['ema60'] > df['ema120'])
    else:
        signal_condition = (df['ema5'] > df['ema10']) & (df['ema10'] > df['ema20']) & (df['ema20'] > df['ema60'])
    df['candle_signal'] = np.where(signal_condition & (df['pct_change'] >=increse_rate) , 1, 0)
    
    return df['candle_signal']

def calculate_goya_line(series, period=24):
    """Calculate Goya Line."""
    return ta.ema(series, length=period)

def calculate_supertrend(df, multiplier, atr_period=10,return_df=False):
    """
    슈퍼트렌드 지표를 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    multiplier : float
        ATR 승수
    atr_period : int, optional
        ATR 계산 기간, by default 10

    Returns
    -------
    pandas.Series
        슈퍼트렌드 방향을 나타내는 시리즈 (1: 상승추세, -1: 하락추세)
    """
    df = standardize_column_names(df)
    df['atr'] = ta.atr(high=df['high'], low=df['low'], close=df['close'], length=atr_period)
    df['hl2'] = (df['high'] + df['low']) / 2
    df['up'] = df['hl2'] - (multiplier * df['atr'])
    df['dn'] = df['hl2'] + (multiplier * df['atr'])
    df['supertrend_direction'] = 1  # Initialize trend to 1

    df['up1'] = df['up'].shift(1)
    df['dn1'] = df['dn'].shift(1)
    df['close1'] = df['close'].shift(1)

    for i in range(len(df)):
        if i == 0:
            df.loc[df.index[i], 'up'] = df.loc[df.index[i], 'up']
            df.loc[df.index[i], 'dn'] = df.loc[df.index[i], 'dn']
            df.loc[df.index[i], 'supertrend_direction'] = 1
        else:
            up = df.loc[df.index[i], 'up']
            up1 = df.loc[df.index[i - 1], 'up']
            dn = df.loc[df.index[i], 'dn']
            dn1 = df.loc[df.index[i - 1], 'dn']
            close1 = df.loc[df.index[i - 1], 'close']
            trend_prev = df.loc[df.index[i - 1], 'supertrend_direction']
            
            if close1 > up1:
                df.loc[df.index[i], 'up'] = max(up, up1)
            else:
                df.loc[df.index[i], 'up'] = up

            if close1 < dn1:
                df.loc[df.index[i], 'dn'] = min(dn, dn1)
            else:
                df.loc[df.index[i], 'dn'] = dn

            if trend_prev == -1 and df.loc[df.index[i], 'close'] > dn1:
                df.loc[df.index[i], 'supertrend_direction'] = 1
            elif trend_prev == 1 and df.loc[df.index[i], 'close'] < up1:
                df.loc[df.index[i], 'supertrend_direction'] = -1
            else:
                df.loc[df.index[i], 'supertrend_direction'] = trend_prev
    
    if return_df:
        return df
    else:
        return df['supertrend_direction']

def get_supertrend(symbol, multiplier=4, atr_period=100, interval='60m',start=None, end=None, get_data_type='futures', return_df=False):
    """
    슈퍼트렌드 지표를 계산하여 반환합니다.

    Parameters
    ----------
    symbol : str
        코인 심볼
    multiplier : float
        슈퍼트렌드 계산에 사용되는 ATR 승수
    atr_period : int, optional
        ATR 계산 기간, by default 10
    interval : str, optional
        캔들 간격, by default '60m'
    start : str, optional
        시작 날짜, by default None, format='YYYY-MM-DD'
    end : str, optional
        종료 날짜, by default None, format='YYYY-MM-DD'
    get_data_type : str, optional
        데이터 타입, by default 'futures'
        'futures': 선물 데이터
        'spot': 현물 데이터

    Returns
    -------
    pd.Series
        슈퍼트렌드 방향 시리즈 (1: 상승추세, -1: 하락추세)
    """
    df = get_data(symbol, interval,start=start,end=end,data_type=get_data_type)
    super_trend = calculate_supertrend(df, multiplier, atr_period,return_df=return_df)
    return super_trend

def calculate_ut_signal(df, atr_period_ut=100, key_Val=2,return_df=False):
    """
    UT 시그널을 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    atr_period_ut : int
        ATR 계산 기간
    key_Val : float
        ATR 승수

    Returns
    -------
    pandas.Series
        UT 시그널 시리즈 (1: 매수 신호, -1: 매도 신호, 0: 중립)

    Notes
    -----
    - ATR을 이용한 트레일링 스탑을 계산하여 매수/매도 시그널을 생성합니다
    - 가격이 트레일링 스탑을 상향 돌파하면 매수(1), 하향 돌파하면 매도(-1) 시그널이 발생합니다
    - atr_period_ut 기간만큼의 초기 데이터는 NaN 값이 발생합니다
    """
    data = standardize_column_names(df)
    # Calculate ATR
    data['ATR'] = ta.atr(data['high'],data['low'],data['close'],length=atr_period_ut)
    data['nLoss'] = key_Val * data['ATR']

    data['src'] = data['close']

    # Initialize variables
    data['xATRTrailingStop'] = 0.0
    data['pos'] = 0

    # Calculate ATR Trailing Stop
    for i in range(1, len(data)):
        prev_trailing_stop = data['xATRTrailingStop'].iat[i-1]
        prev_src = data['src'].iat[i-1]
        curr_src = data['src'].iat[i]
        nLoss = data['nLoss'].iat[i]

        iff_1 = curr_src - nLoss if curr_src > prev_trailing_stop else curr_src + nLoss
        iff_2 = min(prev_trailing_stop, curr_src + nLoss) if (curr_src < prev_trailing_stop and prev_src < prev_trailing_stop) else iff_1
        data['xATRTrailingStop'].iat[i] = max(prev_trailing_stop, curr_src - nLoss) if (curr_src > prev_trailing_stop and prev_src > prev_trailing_stop) else iff_2
        
        iff_3 = -1 if (prev_src > prev_trailing_stop and curr_src < prev_trailing_stop) else data['pos'].iat[i-1]
        data['pos'].iat[i] = 1 if (prev_src < prev_trailing_stop and curr_src > prev_trailing_stop) else iff_3
        
    # for buy (src > xATRTrailingStop) & (beforde_src < before_xATRTrailingStop)
    data['buy'] = (data['src'] > data['xATRTrailingStop']) & (data['src'].shift(1) < data['xATRTrailingStop'].shift(1))
    # for sell (src < xATRTrailingStop) & (beforde_src > before_xATRTrailingStop)
    data['sell'] = (data['src'] < data['xATRTrailingStop']) & (data['src'].shift(1) > data['xATRTrailingStop'].shift(1))
    data['ut_signal'] = np.where(data['buy'], 1, np.where(data['sell'], -1, 0))
    if return_df:
        return data
    else:
        return data['ut_signal']

def get_ut_signal(symbol, atr_period_ut=100, key_Val=2, interval='60m', start=None, end=None, get_data_type='futures', return_df=False):
    """
    UT 시그널을 계산하는 함수입니다.

    Parameters
    ----------
    symbol : str
        거래 심볼 (예: 'BTCUSDT')
    atr_period_ut : int 
        ATR 계산 기간
    key_Val : float
        ATR 승수
    interval : str, optional
        캔들 간격, by default '60m'
    start : str, optional
        시작 날짜, by default None, format='YYYY-MM-DD'
    end : str, optional
        종료 날짜, by default None, format='YYYY-MM-DD'
    get_data_type : str, optional
        데이터 타입 ('futures' 또는 'spot'), by default 'futures'

    Returns
    -------
    pandas.Series
        UT 시그널 시리즈 (1: 매수 신호, -1: 매도 신호, 0: 중립)

    Notes
    -----
    - 주어진 심볼에 대한 OHLCV 데이터를 가져와서 UT 시그널을 계산합니다
    - calculate_ut_signal() 함수를 내부적으로 호출하여 시그널을 생성합니다
    """
    data = get_data(symbol, interval,start=start,end=end,data_type=get_data_type)
    data = calculate_ut_signal(data, atr_period_ut, key_Val,return_df=return_df)
    return data

def calculate_supertrend_v(df, window_len=28, v_len=14, tf=100, st_mult=1, st_period=100):
    """
    슈퍼트렌드 V 지표를 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    window_len : int, optional
        가격 스프레드 계산을 위한 윈도우 길이, by default 28
    v_len : int, optional
        볼륨 스무딩을 위한 이동평균 기간, by default 14  
    tf : int, optional
        시간 프레임 조정 계수, by default 100
    st_mult : int, optional
        슈퍼트렌드 밴드 승수, by default 1
    st_period : int, optional
        ATR 계산 기간, by default 100

    Returns
    -------
    pandas.series
        슈퍼트렌드 V 지표가 계산된 시리즈

    Notes
    -----
    - 가격과 거래량을 결합한 슈퍼트렌드 변형 지표를 계산합니다
    - 상단/하단 밴드와 추세 방향을 포함한 결과를 반환합니다
    """
    df = standardize_column_names(df)
    df['hilow'] = (df['high'] - df['low']) * 100
    df['openclose'] = (df['close'] - df['open']) * 100
    df['vol'] = df['volume'] / df['hilow']
    df['spreadvol'] = df['openclose'] * df['vol']
    df['spreadvol_cum'] = df['spreadvol'].cumsum()
    df['VPT'] = df['spreadvol'] + df['spreadvol_cum']
    
    df['price_spread'] = df['high'].subtract(df['low']).rolling(window=window_len).std()
    df['v'] = df['spreadvol'] + df['spreadvol_cum']
    df['smooth'] = df['v'].rolling(window=v_len).mean()
    df['v_spread'] = (df['v'] - df['smooth']).rolling(window=window_len).std()
    df['shadow'] = (df['v'] - df['smooth']) / df['v_spread'] * df['price_spread']
    
    df['out'] = np.where(df['shadow'] > 0, df['high'] + df['shadow'], df['low'] + df['shadow'])
    len_factor = tf / 60 * 7
    df['c'] = ta.ema(df['out'], length=len_factor)
    df['o'] = ta.ema(df['open'], length=len_factor)
    df['vpt'] = ta.ema(df['out'], length=len_factor)
    df['atr'] = df.ta.atr(length=st_period)
    
    # Calculate upper and lower levels
    df['up_lev'] = df['vpt'] - st_mult * df['atr']
    df['dn_lev'] = df['vpt'] + st_mult * df['atr']

    # Initialize up_trend and down_trend columns
    df['up_trend'] = df['up_lev'].copy()
    df['down_trend'] = df['dn_lev'].copy()

    # Calculate final up and down trends
    for i in range(1, len(df)):
        df.loc[df.index[i], 'up_trend'] = max(
            df.loc[df.index[i], 'up_lev'],
            df.loc[df.index[i-1], 'up_trend']
        ) if df.loc[df.index[i-1], 'close'] > df.loc[df.index[i-1], 'up_trend'] else df.loc[df.index[i], 'up_lev']
        
        df.loc[df.index[i], 'down_trend'] = min(
            df.loc[df.index[i], 'dn_lev'],
            df.loc[df.index[i-1], 'down_trend']
        ) if df.loc[df.index[i-1], 'close'] < df.loc[df.index[i-1], 'down_trend'] else df.loc[df.index[i], 'dn_lev']

    # Calculate trend
    df['trend'] = 0
    for i in range(1, len(df)):
        if df.loc[df.index[i], 'close'] > df.loc[df.index[i-1], 'down_trend']:
            df.loc[df.index[i], 'trend'] = 1
        elif df.loc[df.index[i], 'close'] < df.loc[df.index[i-1], 'up_trend']:
            df.loc[df.index[i], 'trend'] = -1
        else:
            df.loc[df.index[i], 'trend'] = df.loc[df.index[i-1], 'trend']

    # Calculate SuperTrend line
    df['st_line'] = np.where(df['trend'] == 1, df['up_trend'], df['down_trend'])

    # Calculate buy/sell signals
    df['buy'] = (
        (df['close'] > df['st_line'].shift(1)) & 
        (df['close'].shift(1) <= df['st_line'].shift(1)) &
        (df['close'] > df['o'])
    )

    df['sell'] = (
        (df['close'] < df['st_line'].shift(1)) & 
        (df['close'].shift(1) >= df['st_line'].shift(1)) &
        (df['close'] < df['o'])
    )
    df['super_trend_v_signal'] = np.where(df['buy'], 1, np.where(df['sell'], -1, 0))
    return df['super_trend_v_signal']

def get_supertrend_v(symbol, interval='60m', window_len=28, v_len=14, tf=100, st_mult=1, st_period=100,start=None,end=None,get_data_type='futures'):
    """
    슈퍼트렌드 V 지표를 계산하는 함수입니다.

    Args:
        symbol (str): 거래 심볼 (예: 'BTCUSDT')
        interval (str): 캔들 간격 (예: '1h', '4h', '1d')
        window_len (int): VPT 계산을 위한 윈도우 길이 (기본값: 28)
        v_len (int): VPT 이동평균 계산을 위한 기간 (기본값: 14)
        tf (int): 추세 필터 기간 (기본값: 100)
        st_mult (float): 슈퍼트렌드 승수 (기본값: 1)
        st_period (int): 슈퍼트렌드 계산 기간 (기본값: 100)
        start (str, optional): 데이터 시작 시간 (예: '2023-01-01')
        end (str, optional): 데이터 종료 시간 (예: '2023-12-31')
        get_data_type (str): 데이터 타입 ('futures' 또는 'spot', 기본값: 'futures')

    Returns:
        pandas.Series: 슈퍼트렌드 V 신호값 (-1: 매도, 0: 중립, 1: 매수)
    """
    df = get_data(symbol, interval,start=start,end=end,data_type=get_data_type)
    df['super_trend_v_signal'] = calculate_supertrend_v(df, window_len, v_len, tf, st_mult, st_period)
    return df['super_trend_v_signal']

def calculate_blackflag(df, ATRPeriod, ATRFactor=6):
    """
    블랙플래그 지표를 계산하는 함수입니다.
    
    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    ATRPeriod : int
        ATR 계산에 사용할 기간
    ATRFactor : int, optional
        ATR 승수 (기본값: 6)
        
    Returns
    -------
    pandas.Series
        블랙플래그 트렌드 시그널 (-1: 하락, 1: 상승)
    """
    df = standardize_column_names(df)
    df['HiLo'] = np.minimum(df['high'] - df['low'], 
                           1.5 * (df['high'].rolling(window=ATRPeriod).mean() - 
                                 df['low'].rolling(window=ATRPeriod).mean()))
    
    df['HRef'] = np.where(df['low'] <= df['high'].shift(1),
                         df['high'] - df['close'].shift(1),
                         (df['high'] - df['close'].shift(1)) - 
                         0.5 * (df['low'] - df['high'].shift(1)))
    
    df['LRef'] = np.where(df['high'] >= df['low'].shift(1),
                         df['close'].shift(1) - df['low'],
                         (df['close'].shift(1) - df['low']) - 
                         0.5 * (df['low'].shift(1) - df['high']))
    
    df['TrueRange'] = df[['HiLo', 'HRef', 'LRef']].max(axis=1)
    df = df.iloc[ATRPeriod+1:].copy()
    df['Loss'] = ATRFactor * calculate_wilders_ma(df['TrueRange'], ATRPeriod)
    df['Up'] = df['close'] - df['Loss']
    df['Dn'] = df['close'] + df['Loss']
    
    df['TrendUp'] = df['Up']
    df['TrendDown'] = df['Dn']
    df['Trend'] = 1
    before_index=None
    for i, row in df.iterrows():
        if i == df.index[0]:
            before_index=i
            continue  # 첫 번째 행은 건너뜁니다.
        df.loc[i, 'TrendUp'] = max(row['Up'], df.loc[before_index, 'TrendUp']) if df.loc[before_index, 'close'] > df.loc[before_index, 'TrendUp'] else row['Up']
        df.loc[i, 'TrendDown'] = min(row['Dn'], df.loc[before_index, 'TrendDown']) if df.loc[before_index, 'close'] < df.loc[before_index, 'TrendDown'] else row['Dn']
        df.loc[i, 'Trend'] = 1 if row['close'] > df.loc[before_index, 'TrendDown'] else (-1 if row['close'] < df.loc[before_index, 'TrendUp'] else df.loc[before_index, 'Trend'])
        before_index=i
        
    df['Trail'] = np.where(df['Trend'] == 1, df['TrendUp'], df['TrendDown'])

    df['ex'] = df['high']
    for i, row in df.iterrows():
        if i == df.index[0]:
            continue  # 첫 번째 행은 건너뜁니다.
        prev_index = df.index.get_loc(i) - 1
        if df.loc[i, 'Trend'] == 1:
            df.loc[i, 'ex'] = max(df.iloc[prev_index]['ex'], row['high'])
        elif df.loc[i, 'Trend'] == -1:
            df.loc[i, 'ex'] = min(df.iloc[prev_index]['ex'], row['low'])
    return df['Trend']

def get_blackflag(symbol, ATRPeriod, interval='240m', ATRFactor=6, start=None, end=None, get_data_type='futures'):
    """
    블랙플래그 지표를 계산하는 함수입니다.

    Args:
        symbol (str): 거래 심볼 (예: 'BTCUSDT')
        ATRPeriod (int): ATR 계산 기간
        interval (str): 캔들 간격 (예: '240m', '1h', '4h', '1d')
        ATRFactor (float): ATR 승수 (기본값: 6)
        start (str, optional): 데이터 시작 시간 (예: '2023-01-01')
        end (str, optional): 데이터 종료 시간 (예: '2023-12-31')
        get_data_type (str): 데이터 타입 ('futures' 또는 'spot', 기본값: 'futures')

    Returns:
        pandas.Series: 블랙플래그 신호값 (-1: 매도, 1: 매수)
    """
    df = get_data(symbol, interval,start=start,end=end,data_type=get_data_type)
    df['Trend'] = calculate_blackflag(df, ATRPeriod, ATRFactor)
    return df['Trend']


def calculate_divergence_signal(df, 
                    rsi_period: int = 14,
                    volatility_threshold: float = 1.0,
                    repainting_baseline_period: int = 4,
                    repainting_divergence_period: int = 4,
                    result_type='repainted'):
    """
    다이버전스 신호를 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    rsi_period : int, optional
        RSI 계산 기간, by default 14
    volatility_threshold : float, optional
        다이버전스 조건으로 사용할 하락률, by default 1.0
    repainting_baseline_period : int, optional
        리페인팅 기간, by default 4
    repainting_divergence_period : int, optional
        리페인팅 기간, by default 4
    result_type : str, optional
        결과 타입, by default 'repainted',
        'repainted' : 리페인팅된 결과
        'original' : 리페인팅되지 않은 시그널 확정된 시점

    Returns
    -------
    pandas.Series
        다이버전스 신호값 (1: 매수 신호, -1: 매도 신호, 0: 중립)
    """
    # rsi 계산
    df['rsi'] = ta.rsi(df["close"], length=rsi_period).fillna(0)
    df['highest_rsi'] = df['rsi'].rolling(window=repainting_baseline_period +1).max()
    df['highest_price'] = df['high'].rolling(window=repainting_baseline_period +1).max()
    df['lowest_rsi'] = df['rsi'].rolling(window=repainting_baseline_period +1).min()
    df['lowest_price'] = df['low'].rolling(window=repainting_baseline_period +1).min()

    # 다이버전스 저장용 컬럼
    df['signal'] = 0
    df['signal_repainted'] = 0  
    df['down_diver_cond'] = False
    df['up_diver_cond'] = False

    up_mark_bar_index = None
    up_diver_start_index = None
    up_diver_bar_index = None

    down_mark_bar_index = None
    down_diver_start_index = None
    down_diver_bar_index = None

    # 기준점 초기화 조건 변수
    down_mark_bar_index_init_cond = False
    up_mark_bar_index_init_cond = False

    column_index_down_diver_cond = df.columns.get_loc('down_diver_cond')
    column_index_up_diver_cond = df.columns.get_loc('up_diver_cond')
    column_index_signal= df.columns.get_loc('signal')
    column_index_signal_repainted = df.columns.get_loc('signal_repainted')

    for i in range(len(df)):
        #print(f'{i} / {len(df)}', end='\r')
        def cal_diver_cond(_bar_index, _mark_bar_index,type='up'):
            
            if _mark_bar_index is None:
                _mark_bar_index = _bar_index
            # 기준점 high
            _mark_price = df['high'].iloc[_mark_bar_index] if type == 'down' else df['low'].iloc[_mark_bar_index]
            
            # 기준점부터 현재봉까지 저점
            mark_line_price = df['low'].iloc[_mark_bar_index+1:_bar_index + 1].min() if type == 'down' else df['high'].iloc[_mark_bar_index+1:_bar_index + 1].max()
            
            # 기간중 최대 하락률
            _price_change = abs((mark_line_price - _mark_price) / _mark_price * 100)
            
            diver_cond = _price_change >= volatility_threshold
            
            return diver_cond
        
        # 다이버가 시작됐을 때
        if down_diver_start_index is not None and i - down_diver_start_index <= repainting_divergence_period:


            # 다이버 인덱스 갱신 조건
            if df['high'].iloc[down_diver_start_index] != df['highest_price'].iloc[i]:
                down_diver_start_index = i
                

            elif df['high'].iloc[down_diver_start_index] == df['highest_price'].iloc[i] and i - down_diver_start_index == repainting_divergence_period:

                df.iloc[down_diver_start_index, column_index_signal_repainted] = -1
                df.iloc[down_diver_start_index + repainting_divergence_period, column_index_signal ] = -1
                # 리페인팅된 다이버 위치가 기준점 조건에 부합하면 새로운 기준점으로 설정
                if (df['rsi'].iloc[down_diver_start_index] > 70 and 
                    df['high'].iloc[down_diver_start_index] >= df['highest_price'].iloc[down_diver_start_index]):
                    down_mark_bar_index = down_diver_start_index
                    down_mark_bar_index_init_cond = False
                else:
                    down_mark_bar_index = None
                down_diver_start_index = None
            
            
        # 하락 다이버전스
        # 기준점
        # 기준점이 없는 경우 기준점 조건: RSI > 70이고 RSI와 가격이 최고점
        if (down_mark_bar_index is None and df['rsi'].iloc[i] > 70 and 
            df['high'].iloc[i] >= df['highest_price'].iloc[i]):
            down_mark_bar_index = i
            down_mark_bar_index_init_cond = False
            down_diver_start_index=None
            down_diver_bar_index = None
            
        # down_mark_bar_index_init_cond 가 True인 경우 기존 기존점 보다 고점이 작고 rsi가 70 이상이고 최근 고점인 경우 
        if down_mark_bar_index_init_cond and down_mark_bar_index is not None and df['rsi'].iloc[i] > 70 and df['high'].iloc[i] >= df['highest_price'].iloc[i] and df['high'].iloc[i] < df['high'].iloc[down_mark_bar_index]:
            down_mark_bar_index = i
            down_mark_bar_index_init_cond = False
            down_diver_start_index=None
            down_diver_bar_index = None

        # 기준점이 존재하고 고점이 갱신된 경우 
        if (
            down_mark_bar_index is not None and down_mark_bar_index != i and 
            df['high'].iloc[down_mark_bar_index] < df['high'].iloc[i]
            ):
            

            # 고점 갱신 및 rsi가 기준점 보다 작으면서 하락 다이버가 시작이 안된 경우
            if df['rsi'].iloc[i] < df['rsi'].iloc[down_mark_bar_index] and down_diver_start_index is None:
                # 기준점에서 1캔들 이내에서 고점 갱신 및 rsi가 70이상인 경우 기준점 재설정
                if i - down_mark_bar_index == 1 :
                    if df['rsi'].iloc[i] > 70:
                        down_mark_bar_index = i
                        down_mark_bar_index_init_cond = False
                        down_diver_start_index=None
                        down_diver_bar_index = None
                    else:
                        # rsi가 70 미만인 경우에는 기준점 취소
                        down_mark_bar_index = None
                else:
                    down_diver_bar_index = i
                    
            # 고점 갱신, rsi 고점 갱신된 경우 새로운 기준점으로 설정
            elif df['rsi'].iloc[i] > df['rsi'].iloc[down_mark_bar_index]:
                down_mark_bar_index = i
                down_mark_bar_index_init_cond = False
                down_diver_start_index=None
                down_diver_bar_index = None
            
            # 다이버 조건이 만족했을때 다이버 시작
            if down_diver_bar_index is not None:

                down_diver = cal_diver_cond(i, down_mark_bar_index,'down')
                df.iloc[i, column_index_down_diver_cond] = down_diver
                if down_diver:
                    # 변동성 만족시 다이버 스타트
                    down_diver_start_index = i
                    down_diver_bar_index = None
                    
                elif df['rsi'].iloc[i] > 70:
                    # 변동성 만족도 못하고 rsi가 70이상인 경우 기준점 재설정
                    down_mark_bar_index = i
                    down_mark_bar_index_init_cond = False
                    down_diver_start_index=None
                    down_diver_bar_index = None
                else:
                    # 변동성 만족도 못하고 rsi가 70미만인 경우
                    down_diver_start_index=None
                    down_diver_bar_index = None
                    down_mark_bar_index = None
        
        # 기준점이 있는데 rsi가 30이하로 떨어진 경우 기준점 초기화            
        if down_mark_bar_index is not None and df['rsi'].iloc[i] < 30:
            down_mark_bar_index_init_cond = True
            
            
        # 상승다이버
        # 상승 다이버가 시작됐을 때
        if up_diver_start_index is not None and i - up_diver_start_index <= repainting_divergence_period:
            # 다이버 인덱스 갱신 조건
            if df['low'].iloc[up_diver_start_index] != df['lowest_price'].iloc[i]:
                up_diver_start_index = i
                
            elif df['low'].iloc[up_diver_start_index] == df['lowest_price'].iloc[i] and i - up_diver_start_index == repainting_divergence_period:
                df.iloc[up_diver_start_index, column_index_signal_repainted] = 1
                df.iloc[up_diver_start_index + repainting_divergence_period, column_index_signal] = 1
                
                # 리페인팅된 다이버 위치가 기준점 조건에 부합하면 새로운 기준점으로 설정
                if (df['rsi'].iloc[up_diver_start_index] < 30 and 
                    df['low'].iloc[up_diver_start_index] <= df['lowest_price'].iloc[up_diver_start_index]):
                    up_mark_bar_index = up_diver_start_index
                    up_mark_bar_index_init_cond = False
                else:
                    up_mark_bar_index = None
                up_diver_start_index = None

        # 상승 다이버전스
        # 기준점이 없는 경우 기준점 조건: RSI < 30이고 RSI와 가격이 최저점
        if (up_mark_bar_index is None and df['rsi'].iloc[i] < 30 and 
            df['low'].iloc[i] <= df['lowest_price'].iloc[i]):
            up_mark_bar_index = i
            up_mark_bar_index_init_cond = False
            up_diver_start_index = None
            up_diver_bar_index = None

        # up_mark_bar_index_init_cond가 True인 경우 기존 기준점보다 저점이 높고 RSI가 30 이하이고 최근 저점인 경우
        if up_mark_bar_index_init_cond and up_mark_bar_index is not None and df['rsi'].iloc[i] < 30 and df['low'].iloc[i] <= df['lowest_price'].iloc[i] and df['low'].iloc[i] > df['low'].iloc[up_mark_bar_index]:
            up_mark_bar_index = i
            up_mark_bar_index_init_cond = False
            up_diver_start_index = None
            up_diver_bar_index = None

        # 기준점이 존재하고 저점이 갱신된 경우
        if (up_mark_bar_index is not None and up_mark_bar_index != i and 
            df['low'].iloc[up_mark_bar_index] > df['low'].iloc[i]):
            
            # 저점 갱신 및 RSI가 기준점보다 크면서 상승 다이버가 시작이 안된 경우
            if df['rsi'].iloc[i] > df['rsi'].iloc[up_mark_bar_index] and up_diver_start_index is None:
                # 기준점에서 1캔들 이내에서 저점 갱신 및 RSI가 30 이하인 경우 기준점 재설정
                if i - up_mark_bar_index == 1:
                    if df['rsi'].iloc[i] < 30:
                        up_mark_bar_index = i
                        up_mark_bar_index_init_cond = False
                        up_diver_start_index = None
                        up_diver_bar_index = None
                    else:
                        # RSI가 30 초과인 경우에는 기준점 취소
                        up_mark_bar_index = None
                else:
                    up_diver_bar_index = i
                    
            # 저점 갱신, RSI 저점 갱신된 경우 새로운 기준점으로 설정
            elif df['rsi'].iloc[i] < df['rsi'].iloc[up_mark_bar_index]:
                up_mark_bar_index = i
                up_mark_bar_index_init_cond = False
                up_diver_start_index = None
                up_diver_bar_index = None
            
            # 다이버 조건이 만족했을 때 다이버 시작
            if up_diver_bar_index is not None:
                up_diver = cal_diver_cond(i, up_mark_bar_index, 'up')
                df.iloc[i, column_index_up_diver_cond] = up_diver
                if up_diver:
                    # 변동성 만족시 다이버 스타트
                    up_diver_start_index = i
                    up_diver_bar_index = None
                    
                elif df['rsi'].iloc[i] < 30:
                    # 변동성 만족도 못하고 RSI가 30 이하인 경우 기준점 재설정
                    up_mark_bar_index = i
                    up_mark_bar_index_init_cond = False
                    up_diver_start_index = None
                    up_diver_bar_index = None
                else:
                    # 변동성 만족도 못하고 RSI가 30 초과인 경우
                    up_diver_start_index = None
                    up_diver_bar_index = None
                    up_mark_bar_index = None

        # 기준점이 있는데 RSI가 70 이상으로 올라간 경우 기준점 초기화
        if up_mark_bar_index is not None and df['rsi'].iloc[i] > 70:
            up_mark_bar_index_init_cond = True
            
                
    
    if result_type == 'repainted':
        return df['signal_repainted']
    else:
        return df['signal']

def get_divergence_signal(symbol,interval='60m', 
                    rsi_period: int = 14,
                    volatility_threshold: float = 2.2,
                    repainting_baseline_period: int = 4,
                    repainting_divergence_period: int = 4,
                    start=None,
                    end=None ,
                    result_type='repainted',
                    get_data_type='spot'):
    """
    다이버전스 신호를 계산하는 함수입니다.

    Args:
        symbol (str): 거래 심볼 (예: 'BTCUSDT')
        interval (str): 캔들 간격 (예: '60m', '1h', '4h', '1d')
        rsi_period (int): RSI 계산 기간 (기본값: 14)
        volatility_threshold (float): 다이버전스 조건으로 사용할 하락률 (기본값: 1.0)
        repainting_baseline_period (int): 리페인팅 기간 (기본값: 4)
        repainting_divergence_period (int): 리페인팅 기간 (기본값: 4)
        start (str, optional): 데이터 시작 시간 (예: '2023-01-01')
        end (str, optional): 데이터 종료 시간 (예: '2023-12-31')
        result_type (str): 결과 타입 ('repainted' 또는 'original', 기본값: 'repainted')
        get_data_type (str): 데이터 타입 ('futures' 또는 'spot', 기본값: 'spot')

    Returns:
        pandas.Series: 다이버전스 신호값 (1: 매수 신호, -1: 매도 신호, 0: 중립)
    """
    df = get_data(symbol, interval,start=start,end=end, data_type=get_data_type)
    df['divergence_signal'] = calculate_divergence_signal(df, rsi_period, volatility_threshold, repainting_baseline_period, repainting_divergence_period, result_type)
    return df['divergence_signal']
    
def calculate_ichimoku_senkou_a(df, conversion_periods=9, base_periods=26, displacement=26):
    """
    이치모쿠 선행스펜 A를 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    conversion_periods : int, optional
        전환선(Tenkan-sen) 계산 기간, by default 9
    base_periods : int, optional
        기준선(Kijun-sen) 계산 기간, by default 26  
    displacement : int, optional
        선행스팬 이동 기간, by default 26

    Returns
    -------
    pandas.Series
        선행스펜 A 값
    """
    def middle_donchian(high_series, low_series, length):
        """
        중간 동치안 채널 값을 계산
        """
        upper = high_series.rolling(window=length).max()
        lower = low_series.rolling(window=length).min()
        return (upper + lower) / 2
    
    df = standardize_column_names(df)  
    # Tenkan-sen (전환선) 계산
    tenkan = middle_donchian(df['high'], df['low'], conversion_periods)
    
    # Kijun-sen (기준선) 계산
    kijun = middle_donchian(df['high'], df['low'], base_periods)
    
    # Senkou Span A (선행스펜 A) 계산
    senkou_span_a = (tenkan + kijun) / 2
    
    # displacement 적용
    senkou_span_a = senkou_span_a.shift(displacement)
    return senkou_span_a

def get_ichimoku_senkou_a(symbol,interval='60m', conversion_periods=9, base_periods=26, displacement=26, start=None, end=None, get_data_type='futures'):
    """
    이치모쿠 선행스펜 A를 계산하는 함수입니다.

    Args:
        symbol (str): 거래 심볼 (예: 'BTCUSDT')
        interval (str): 캔들 간격 (예: '60m', '1h', '4h', '1d')
        conversion_periods (int): 전환선(Tenkan-sen) 계산 기간 (기본값: 9)
        base_periods (int): 기준선(Kijun-sen) 계산 기간 (기본값: 26)
        displacement (int): 선행스팬 이동 기간 (기본값: 26)
        start (str, optional): 데이터 시작 시간 (예: '2023-01-01')
        end (str, optional): 데이터 종료 시간 (예: '2023-12-31')
        get_data_type (str): 데이터 타입 ('futures' 또는 'spot', 기본값: 'futures')

    Returns:
        pandas.Series: 선행스펜 A 값
    """
    df = get_data(symbol, interval,start=start,end=end, data_type=get_data_type)
    df['ichimoku_senkou_a'] = calculate_ichimoku_senkou_a(df, conversion_periods, base_periods, displacement)
    return df['ichimoku_senkou_a']

def calculate_support_resistance_line(df, interval='60m'):
    """
    지지선과 저항선을 계산하는 함수입니다.

    Parameters
    ----------
    df : pandas.DataFrame
        OHLCV 데이터가 포함된 데이터프레임
    interval : str, optional
        캔들 간격 (예: '60m', '1h', '4h', '1d'), by default '60m'

    Returns
    -------
    pandas.DataFrame
        각 기간별 지지선과 저항선이 포함된 데이터프레임
        - buy1~6: 1일~6일 기준 지지선
        - sell1~6: 1일~6일 기준 저항선
    """
    df = standardize_column_names(df)
        
    interval_int = int(interval.replace('m', ''))
    
    period_step ={
        # 분 기준
        '1':1440 // interval_int,
        '2':2880 // interval_int,
        '3':10080 // interval_int,
        '4':20160 // interval_int,
        '5':30240 // interval_int,
        '6':40320 // interval_int,
    }
    
    for key in period_step:
        df[f'buy{key}'] = df['low'].rolling(window=period_step[key]).min()
        df[f'sell{key}'] = df['high'].rolling(window=period_step[key]).max()
    
    return df[[f'buy{key}' for key in period_step] + [f'sell{key}' for key in period_step]]                

def get_support_resistance_line(symbol, interval='60m',start=None, end= None, get_data_type='futures'):
    """
    지지선과 저항선을 계산하는 함수
    """
    df = get_data(symbol, interval, data_type=get_data_type)
    df_support_resistance = calculate_support_resistance_line(df, interval)
    return df_support_resistance
