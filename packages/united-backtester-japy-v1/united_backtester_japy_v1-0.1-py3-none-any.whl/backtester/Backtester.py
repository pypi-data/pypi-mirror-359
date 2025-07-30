import backtester

from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Union
from typing import Protocol
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    TRAILING = "trailing"

class OrderPositionSide(Enum):
    LONG = "long"
    SHORT = "short"

class OrderStatus(Enum):
    PENDING = "pending"
    ACTIVATED = "activated"
    FILLED = "filled"
    CANCELED = "canceled"

class CloseType(Enum):
    TAKE_PROFIT = "profit"
    STOP_LOSS = "loss"
    
class DataRow(Protocol):
    Index: datetime
    high: float
    low: float
    close: float
    open: float
    

@dataclass
class Order:
    # 기본 주문 정보
    symbol: str
    position_side: OrderPositionSide
    order_type: OrderType
    position_size: float
    entry_price: float
    entry_time: datetime
    interval: str
    activated_time: Optional[datetime] = None
    margin: Optional[float] = None
    
    # 청산 관련 정보
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    close_type: Optional[CloseType] = None
    
    # 주문 상태
    status: OrderStatus = OrderStatus.PENDING
    
    # 리밋 주문 관련
    limit_price: Optional[float] = None
    
    # 손절 주문 관련
    stop_loss_price: Optional[float] = None
    
    # 트레일링 주문 관련
    activation_price: Optional[float] = None
    callback_rate: Optional[float] = None
    highest_price: Optional[float] = None  # LONG 포지션용
    lowest_price: Optional[float] = None   # SHORT 포지션용
    metadata: Optional[dict] = None
    
    def check_activation_price(self, row: DataRow) -> bool:
        """
        트레일링 스탑 주문 활성화 체크
        
        Returns: 주문 활성화 필요 여부 (True/False)
        """
        
        if self.position_side == OrderPositionSide.LONG:
            return row.high >= self.activation_price
        else:
            return row.low <= self.activation_price
        
    def check_activation_price_for_limit_order_open(self, row: DataRow) -> bool:
        """
        리밋오더 예약주문 활성화 체크
        리밋 open 체결 조건
        close조건은 stop_loss로 손절 가격 설정가능,
        limit price로 익절 가격 설정가능능
        """
        
        return row.low <= self.activation_price <= row.high
        
    def check_stop_loss_conditions(self, row):
        """손절 조건 체크 로직을 구현해야 합니다
        트레이딩뷰 close 개념"""
        if self.position_side == OrderPositionSide.LONG:
            return row.low <= self.stop_loss_price
        else:
            return row.high >= self.stop_loss_price
        
    def check_trailing_stop(self, row: DataRow, df_5m: pd.DataFrame) -> bool:
        """트레일링 스탑 체크
        Returns: 주문 청산 필요 여부 (True/False)
        """
        if self.order_type != OrderType.TRAILING:
            return False
        
        if self.status != OrderStatus.ACTIVATED:
            return False
        
        is_closed=False
        
        # 한캔들내에서 정리되는 경우
        if row.Index == self.activated_time:
            if self.position_side == OrderPositionSide.LONG:
                if row.high * (1 - self.callback_rate) < row.close:
                    self.limit_price = row.high * (1 - self.callback_rate)
                    self.highest_price = row.high
                    is_closed=False
                else:
                    self.limit_price = row.high * (1 - self.callback_rate)
                    self.highest_price = row.high
                    is_closed=True
            else:
                if row.low * (1 + self.callback_rate) > row.close:
                    self.limit_price = row.low * (1 + self.callback_rate)
                    self.lowest_price = row.low
                    is_closed=False
                else:
                    self.limit_price = row.low * (1 + self.callback_rate)
                    self.lowest_price = row.low
                    is_closed=True
            
        else:
            highest_or_lowest = self.highest_price if self.position_side == OrderPositionSide.LONG else self.lowest_price 
            _highest_or_lowest, is_closed, new_trailing_stop_price = backtester.check_trailing_stop_exit_cond(
                df = df_5m,
                _index = row.Index,
                _position_size = self.position_size,
                _highest_or_lowest = highest_or_lowest,
                _profit_price = self.limit_price,
                _callbackrate = self.callback_rate,
                interval = self.interval
            )
            
            if _highest_or_lowest != highest_or_lowest:
                if self.position_side == OrderPositionSide.LONG:
                    self.highest_price = _highest_or_lowest
                else:
                    self.lowest_price = _highest_or_lowest
            if new_trailing_stop_price != self.limit_price:
                self.limit_price = new_trailing_stop_price
        
        return is_closed
            
    def check_limit_order(self, row: DataRow) -> bool:
        """
        리밋 주문 체크
        Returns: 주문 실행 필요 여부 (True/False)
        """
            
        if self.order_type != OrderType.LIMIT:
            return False
        if self.position_side == OrderPositionSide.LONG:
            return row.high >= self.limit_price
        elif self.position_side == OrderPositionSide.SHORT:
            return row.low <= self.limit_price
        else:
            raise ValueError("Invalid position side")
        
    def check_stop_loss_order(self, row: DataRow) -> bool:
        """손절 주문 체크 가격 기반으로 봉마감시 정리하는 로직은 사용하지 말것
        봉마감시 손절은 전략에서 코드 작성"""
        if self.stop_loss_price is None:
            return False
        if self.position_side == OrderPositionSide.LONG:
            return row.low <= self.stop_loss_price
        else:
            return row.high >= self.stop_loss_price

    def close_order(self, row: DataRow, close_type: CloseType, close_price=None):
        """주문 청산 여기에서 손절 주문은 order에 해당하는 손절이고 
        전체적인 포지션을 정리하는 로직은 MAIN backtest class에 있음"""
        if close_price is None:
            if close_type == CloseType.TAKE_PROFIT:
                if self.order_type == OrderType.MARKET:
                    close_price = row.close
                elif self.order_type == OrderType.LIMIT:
                    close_price = self.limit_price
                elif self.order_type == OrderType.TRAILING:
                    close_price = self.limit_price
            elif close_type == CloseType.STOP_LOSS:
                close_price = self.stop_loss_price
        else:
            close_price = close_price
        
        self.exit_price = close_price
        self.exit_time = row.Index
        self.close_type = close_type
        self.status = OrderStatus.FILLED
        

    def to_trade_record(self) -> dict:
        """거래 기록용 딕셔너리 반환"""
        return {
            "symbol": self.symbol,
            "position": self.position_side.value,
            "position_size": self.position_size,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "close_type": self.close_type.value if self.close_type else None,
            'profit_pct': ((self.exit_price - self.entry_price) / (self.entry_price))* 100 if self.position_side == OrderPositionSide.LONG
                    else ((self.entry_price - self.exit_price) / (self.entry_price))* 100,
            "margin": self.margin if self.margin is not None else 0,
            "entry_time": self.entry_time,
            "exit_time": self.exit_time
        }
        
    def to_dict(self) -> dict:
        """Order 객체의 모든 속성을 딕셔너리로 반환"""
        return {
            "symbol": self.symbol,
            "position_side": self.position_side.value,
            "order_type": self.order_type.value,
            "position_size": self.position_size,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time,
            "interval": self.interval,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time,
            "close_type": self.close_type.value if self.close_type else None,
            "status": self.status.value,
            "margin": self.margin if self.margin is not None else 0,
            "limit_price": self.limit_price,
            "activation_price": self.activation_price,
            "callback_rate": self.callback_rate,
            "highest_price": self.highest_price,
            "lowest_price": self.lowest_price,
            "activated_time": self.activated_time
        }


class BacktesterABS(ABC):
    def __init__(self, test_id, symbol, test_start_date='2023-01-01', test_end_date='2024-06-30', 
                 interval='60m', data_type='futures', params=None ,pyramiding=1):
        self.test_id = test_id
        self.symbol = symbol
        self.interval = interval
        self.test_start_date = test_start_date
        self.test_end_date = test_end_date
        self.trade_history = []
        self.active_orders = []
        self.data = None
        self.data_5m = None
        self.data_type = data_type
        self.result = None
        self.params = None
        self.pyramiding = pyramiding
        self.position_size = 0
        self.set_params(params)
        
    def set_test_id(self, test_id):
        """테스트 ID 설정"""
        self.test_id = test_id
        
    def fetch_test_data(self):
        """테스트 데이터 가져오기"""
        self.data = backtester.get_data(self.symbol, self.interval, data_type=self.data_type)
        self.data_5m = backtester.get_data(self.symbol, '5m', data_type=self.data_type)
        
    def check_take_profit_conditions(self, row, order: Order):
        """마켓주문시 익절 조건 체크 로직을 구현해야 합니다"""
        pass

    def check_loss_conditions(self, row, position_size):
        """손절 조건 체크 로직을 구현해야 합니다 인풋을 수정하려면 process_order도 함께 수정해야 함"""
        pass
    
    def add_trade_record(self, trade):
        """거래 기록 추가"""
        self.trade_history.append(trade)

    def save_results(self):
        """결과 저장"""
        results_df = pd.DataFrame(self.result)
        result_path = f'{self.test_id}_results.csv'
        results_df.to_csv(result_path,index=False)
        backtester.merge_csv_to_excel(self.test_id,result_path)
        
    def prepare_for_backtest(self):
        """백테스트 실행 전 준비"""
        self.trade_history = []
        self.fetch_test_data()
        self.set_indicators()
        self.set_entry_signal()
        if self.test_start_date:
            self.data = self.data.loc[self.test_start_date:]
        if self.test_end_date:
            self.data = self.data.loc[:self.test_end_date]
            
    def process_order(self, row: DataRow):
        """주문 처리 로직"""
        remove_orders = []
        position_size = 0
        avg_entry_price = 0
        close_position=False
        for order in self.active_orders:
            if row.Index != order.entry_time:
                
                # 리밋주문
                if order.order_type == OrderType.LIMIT:
                    if order.status == OrderStatus.PENDING:
                        if order.check_activation_price_for_limit_order_open(row):
                            order.status = OrderStatus.ACTIVATED
                            order.activated_time = row.Index
                            
                    if order.status == OrderStatus.ACTIVATED:
                        if order.check_limit_order(row):
                            order.close_order(row, CloseType.TAKE_PROFIT)
                            remove_orders.append(order)
                            self.add_trade_record(order)
                            continue
                    
                # 트레일링스탑
                elif order.order_type == OrderType.TRAILING:
                    if order.status == OrderStatus.PENDING:
                        if order.check_activation_price(row):
                            order.status = OrderStatus.ACTIVATED
                            order.activated_time = row.Index
                            
                    # elif 사용 금지
                    if order.status == OrderStatus.ACTIVATED:
                        if order.check_trailing_stop(row, self.data_5m):
                            order.close_order(row, CloseType.TAKE_PROFIT)
                            remove_orders.append(order)
                            self.add_trade_record(order)
                            continue

                # 마켓주문       
                elif order.order_type == OrderType.MARKET:
                    if self.check_take_profit_conditions(row, order):
                        order.close_order(row, CloseType.TAKE_PROFIT)
                        remove_orders.append(order)
                        self.add_trade_record(order)
                        continue
                
                # 주문에 대한 exit 개념
                if order.stop_loss_price is not None and order.status == OrderStatus.ACTIVATED:
                    if order.check_stop_loss_conditions(row):
                        order.close_order(row, CloseType.STOP_LOSS)
                        remove_orders.append(order)
                        self.add_trade_record(order)
                        continue
            
            # 포지션 사이즈 계산
            position_size += order.position_size
            # 포지션 평균 가격 계산
            avg_entry_price += order.entry_price * abs(order.position_size)
        
        # 전체 포지션에 대한 close 개념
        if position_size != 0 and len(self.active_orders) != len(remove_orders) and self.check_loss_conditions(row, position_size):
            close_position=True
                
        # 전체 포지션 정리
        if close_position:
            avg_entry_price=avg_entry_price/abs(position_size)
            close_order = Order(
                symbol=self.symbol,
                position_side=order.position_side,
                order_type=OrderType.MARKET,
                position_size=position_size,
                entry_price=avg_entry_price,
                entry_time=order.entry_time,
                interval=self.interval,
                status=OrderStatus.FILLED,
                exit_price=row.close,
                exit_time=row.Index,
                close_type=CloseType.STOP_LOSS
            )
            self.add_trade_record(close_order)
            self.active_orders=[]
        else:
            for order in remove_orders:
                self.active_orders.remove(order)
            
        # process_order 코드는 active_orders가 있을 때 실행되는데 익절 혹은 손절로 정리 된 경우 조건 확인후 만족시 재진입
        # 동시에 여러 포지션은 고려되지 않아서 이런 경우 메소드 수정 필요
        if len(self.active_orders) == 0 :
            long_signal, short_signal = self.check_entry_signals(row)
            if long_signal:
                self.open_position(row, OrderPositionSide.LONG)
            elif short_signal:
                self.open_position(row, OrderPositionSide.SHORT)
            return
        
    def run_backtest(self):
        """백테스트 실행 메인 로직"""
        self.prepare_for_backtest()
        # 백테스트 실행 로직 구현
        for row in self.data.itertuples():
            # 포지션 진입 로직
            if len(self.active_orders) == 0:
                long_signal, short_signal = self.check_entry_signals(row)
                if long_signal:
                    self.open_position(row, OrderPositionSide.LONG)
                elif short_signal:
                    self.open_position(row, OrderPositionSide.SHORT)
            else:
                self.process_order(row)
        self.analyze_trade_history()
    
    def set_params(self, params):
        """
        전략 파라미터 설정
        self.params = params
        if params:
            self.signal_type = params[0][0]
            self.signal_var = params[0]
            self.blackflag_atr_period, self.blackflag_atr_factor, self.blackflag_interval = params[1]
            self.supertrend_atr_period, self.supertrend_multiplier, self.supertrend_interval = params[2]
            self.time_loss_var = params[3]
        이런식으로 필요한 파라미터 설정
        """
        pass

    @abstractmethod
    def set_indicators(self, params):
        """
        지표 설정 로직을 구현해야 합니다.
        예: RSI, MACD, 볼린저밴드 등의 기술적 지표
        self.data['indicator'] 컬럼에 지표 값 저장 1 or 0 or -1
        """
        pass

    @abstractmethod
    def set_entry_signal(self, params):
        """
        진입 조건 설정 로직을 구현해야 합니다.
        예: 크로스오버, 돌파, 반전, UT시그널, SUPERTREND V 등
        self.data['signal'] 컬럼에 시그널 값 저장 1 or 0 or -1
        """
        pass

    @abstractmethod
    def check_entry_signals(self, row):
        """진입 시그널 체크 로직을 구현해야 합니다"""
        pass
    
    @abstractmethod
    def open_position(self, row, position_side: OrderPositionSide):
        """포지션 진입 로직을 구현해야 합니다"""
        pass

    @abstractmethod
    def analyze_trade_history(self):
        """거래 기록 분석 로직을 구현해야 합니다"""
        '''
        
    def analyze_trade_history(self):
        """거래 기록 분석"""
        trade_history = [i.to_trade_record() for i in self.trade_history]
        result = backtester.analyze_trade_history(
            trade_history, self.data, self.symbol, 
        )
        self.result=result
        '''
        pass
    
class FilteredBacktester(BacktesterABS):
    def __init__(self, test_id, symbol, test_start_date='2023-01-01', test_end_date='2024-12-15', 
                interval='60m', data_type='futures', profit_ratio=0.01, params=None, pyramiding=1):
        """
        백테스팅 프레임워크의 기본 클래스
        사용자는 이 클래스를 상속하여 자신만의 전략을 구현할 수 있습니다.
        
        주요 오버라이딩 포인트:
        - calculate_signals: 진입 시그널 계산
        - apply_filters: 필터 로직 구현
        - check_open_conditions: 진입 조건 확인
            - handle_loss: 손절 조건 구현
        """
        super().__init__(test_id, symbol, test_start_date, test_end_date, 
                        interval, data_type, params, pyramiding)
        self.profit_ratio = profit_ratio
        
    def set_params(self, params):
        """
        전략 파라미터 설정
        """
        self.params = params
        if params:
            self.signal_type = params[0][0]
            self.signal_var = params[0]
            self.blackflag_atr_period, self.blackflag_atr_factor, self.blackflag_interval = params[1]
            self.supertrend_atr_period, self.supertrend_multiplier, self.supertrend_interval = params[2]
    
    def set_entry_signal(self):
        """시그널 계산"""
        if self.signal_type == 'v':
            self.data['signal'] = backtester.calculate_supertrend_v(self.data)
        elif self.signal_type == 'ut':
            self.data['signal'] = backtester.calculate_ut_signal(self.data, self.signal_var[2], self.signal_var[3])
        else:
            raise ValueError(f"Invalid signal type: {self.signal_type}")
        
    def set_indicators(self):
        """필터 계산"""
        # 기본 데이터프레임 준비
        base_data = self.data.copy()
        interval_int = int(self.interval.replace('m', ''))
        super_trend_interval_int = int(self.supertrend_interval.replace('m', ''))
        black_flag_interval_int = int(self.blackflag_interval.replace('m', ''))
        
        # 수퍼트렌드 계산 및 병합
        df_super = backtester.get_supertrend(
            self.symbol, 
            multiplier=self.supertrend_multiplier, 
            atr_period=self.supertrend_atr_period, 
            interval=self.supertrend_interval
        )
        
        # 블랙플래그 계산 및 병합
        df_black = backtester.get_blackflag(
            self.symbol, 
            ATRPeriod=self.blackflag_atr_period, 
            ATRFactor=self.blackflag_atr_factor, 
            interval=self.blackflag_interval
        )
        
        # 데이터 병합
        final_df = base_data.copy()
        final_df = final_df.join(df_super.rename('supertrend_direction'), how='left')
        final_df = final_df.join(df_black.rename('blackflag_direction'), how='left')
        
        # 결측값 처리
        final_df['supertrend_direction'] = final_df['supertrend_direction'].ffill()
        final_df['blackflag_direction'] = final_df['blackflag_direction'].ffill()
        
        # 시간간격 조정
        if super_trend_interval_int != interval_int:
            final_df['supertrend_direction'] = final_df['supertrend_direction'].shift(
                super_trend_interval_int // interval_int
            ).fillna(0)
            
        if black_flag_interval_int != interval_int:
            final_df['blackflag_direction'] = final_df['blackflag_direction'].shift(
                black_flag_interval_int // interval_int
            ).fillna(0)
        
        # 필터 적용
        final_df['filter'] = np.where(
            final_df['supertrend_direction'] == final_df['blackflag_direction'],
            final_df['supertrend_direction'],
            0
        )
        # 최종 지표 설정
        self.data['indicator'] = final_df['filter']

    def check_entry_signals(self, row):
        """진입 시그널 체크 로직을 구현해야 합니다"""
        long_signal = row.signal == 1 and row.indicator == 1
        short_signal = row.signal == -1 and row.indicator == -1
        return long_signal, short_signal
        
    def check_loss_conditions(self, row, position_size):
        """손절 조건 체크 로직을 구현해야 합니다"""
        order_position = 1 if position_size > 0 else -1
        trend_reverse_cond = row.indicator != order_position
        return trend_reverse_cond
    
    def open_position(self, row, position_side: OrderPositionSide):
        """포지션 진입 로직을 구현해야 합니다"""
        limit_price = row.close * (1 + self.profit_ratio) if position_side == OrderPositionSide.LONG else row.close * (1 - self.profit_ratio)
        order_limit = Order(
            symbol=self.symbol,
            position_side=position_side,
            order_type=OrderType.LIMIT,
            position_size=1 if position_side == OrderPositionSide.LONG else -1,
            entry_price=row.close,
            entry_time=row.Index,
            interval=self.interval,
            limit_price=limit_price,
            status=OrderStatus.ACTIVATED
        )
        self.active_orders.append(order_limit)

    def analyze_trade_history(self):
        """거래 기록 분석"""
        trade_history = [i.to_trade_record() for i in self.trade_history]
        result = backtester.analyze_trade_history(
            trade_history, self.data, self.symbol, 
            signal_var=self.params[0], 
            blackflag_var=self.params[1], 
            supertrend_var=self.params[2], 
        )
        self.result=result

        
class FilteredTrailingStopBacktester(BacktesterABS):
    def __init__(self, test_id, symbol, test_start_date='2023-01-01', test_end_date='2024-06-30', 
                interval='60m', data_type='futures', profit_ratio=0.01, 
                first_close_position_ratio=0.5, callback_rate=0.005, params=None, pyramiding=1):
        """
        백테스팅 프레임워크의 기본 클래스
        사용자는 이 클래스를 상속하여 자신만의 전략을 구현할 수 있습니다.
        
        주요 오버라이딩 포인트:
        - calculate_signals: 진입 시그널 계산
        - apply_filters: 필터 로직 구현
        - check_open_conditions: 진입 조건 확인
            - handle_loss: 손절 조건 구현
        """
        super().__init__(test_id, symbol, test_start_date, test_end_date, 
                        interval, data_type, params, pyramiding)
        self.first_close_position_ratio = first_close_position_ratio
        self.profit_ratio = profit_ratio
        self.callback_rate = callback_rate
        
    def set_params(self, params):
        """
        전략 파라미터 설정
        """
        self.params = params
        if params:
            self.signal_type = params[0][0]
            self.signal_var = params[0]
            self.blackflag_atr_period, self.blackflag_atr_factor, self.blackflag_interval = params[1]
            self.supertrend_atr_period, self.supertrend_multiplier, self.supertrend_interval = params[2]
    
    def set_entry_signal(self):
        """시그널 계산"""
        if self.signal_type == 'v':
            self.data['signal'] = backtester.calculate_supertrend_v(self.data)
        elif self.signal_type == 'ut':
            self.data['signal'] = backtester.calculate_ut_signal(self.data, self.signal_var[2], self.signal_var[3])
        else:
            raise ValueError(f"Invalid signal type: {self.signal_type}")
        
    def set_indicators(self):
        """필터 계산"""
        # 기본 데이터프레임 준비
        base_data = self.data.copy()
        interval_int = int(self.interval.replace('m', ''))
        super_trend_interval_int = int(self.supertrend_interval.replace('m', ''))
        black_flag_interval_int = int(self.blackflag_interval.replace('m', ''))
        
        # 수퍼트렌드 계산 및 병합
        df_super = backtester.get_supertrend(
            self.symbol, 
            multiplier=self.supertrend_multiplier, 
            atr_period=self.supertrend_atr_period, 
            interval=self.supertrend_interval
        )
        
        # 블랙플래그 계산 및 병합
        df_black = backtester.get_blackflag(
            self.symbol, 
            ATRPeriod=self.blackflag_atr_period, 
            ATRFactor=self.blackflag_atr_factor, 
            interval=self.blackflag_interval
        )
        
        # 데이터 병합
        final_df = base_data.copy()
        final_df = final_df.join(df_super.rename('supertrend_direction'), how='left')
        final_df = final_df.join(df_black.rename('blackflag_direction'), how='left')
        
        # 결측값 처리
        final_df['supertrend_direction'] = final_df['supertrend_direction'].ffill()
        final_df['blackflag_direction'] = final_df['blackflag_direction'].ffill()
        
        # 시간간격 조정
        if super_trend_interval_int != interval_int:
            final_df['supertrend_direction'] = final_df['supertrend_direction'].shift(
                super_trend_interval_int // interval_int
            ).fillna(0)
            
        if black_flag_interval_int != interval_int:
            final_df['blackflag_direction'] = final_df['blackflag_direction'].shift(
                black_flag_interval_int // interval_int
            ).fillna(0)
        
        # 필터 적용
        final_df['filter'] = np.where(
            final_df['supertrend_direction'] == final_df['blackflag_direction'],
            final_df['supertrend_direction'],
            0
        )

        # 최종 지표 설정
        self.data['indicator'] = final_df['filter']

    def check_entry_signals(self, row):
        """진입 시그널 체크 로직을 구현해야 합니다"""
        long_signal = row.signal == 1 and row.indicator == 1
        short_signal = row.signal == -1 and row.indicator == -1
        return long_signal, short_signal
        
    def check_loss_conditions(self, row, position_size):
        """손절 조건 체크 로직을 구현해야 합니다"""
        order_position = 1 if position_size > 0 else -1
        trend_reverse_cond = row.indicator != order_position
        return trend_reverse_cond
    
    def open_position(self, row, position_side: OrderPositionSide):
        """포지션 진입 로직을 구현해야 합니다"""
        limit_price = row.close * (1 + self.profit_ratio) if position_side == OrderPositionSide.LONG else row.close * (1 - self.profit_ratio)
        order_limit = Order(
            symbol=self.symbol,
            position_side=position_side,
            order_type=OrderType.LIMIT,
            position_size=self.first_close_position_ratio if position_side == OrderPositionSide.LONG else self.first_close_position_ratio * -1,
            entry_price=row.close,
            entry_time=row.Index,
            interval=self.interval,
            limit_price=limit_price,
            status=OrderStatus.ACTIVATED
        )
        self.active_orders.append(order_limit)
        order_trailing = Order(
            symbol=self.symbol,
            position_side=position_side,
            order_type=OrderType.TRAILING,
            position_size=1 - self.first_close_position_ratio if position_side == OrderPositionSide.LONG else (1 - self.first_close_position_ratio) * -1,
            entry_price=row.close,
            entry_time=row.Index,
            interval=self.interval,
            activation_price=limit_price,
            limit_price=row.high * (1 + self.callback_rate) if position_side == OrderPositionSide.LONG else row.low * (1 - self.callback_rate),
            highest_price=row.high,
            lowest_price=row.low,
            callback_rate=self.callback_rate,
            status=OrderStatus.PENDING
        )
        self.active_orders.append(order_trailing)

    def analyze_trade_history(self):
        """거래 기록 분석"""
        trade_history = [i.to_trade_record() for i in self.trade_history]
        result = backtester.analyze_trade_history(
            trade_history, self.data, self.symbol, 
            signal_var=self.params[0], 
            blackflag_var=self.params[1], 
            supertrend_var=self.params[2], 
        )
        self.result=result


class FilteredTrailingStopBacktesterWithTimeLoss(FilteredTrailingStopBacktester):
        
    def set_params(self, params):
        """전략 파라미터 설정"""
        super().set_params(params)
        if params:
            self.time_loss_var = params[3]
        
    def check_loss_conditions(self, row, position_size, entry_time):
        """손절 조건 체크"""
        time_loss_cond = row.Index - entry_time >= timedelta(hours=self.time_loss_var)    
        trend_reverse_cond = super().check_loss_conditions(row, position_size)
        return time_loss_cond or trend_reverse_cond
    
    def analyze_trade_history(self):
        """거래 기록 분석"""
        trade_history = [i.to_trade_record() for i in self.trade_history]
        result = backtester.analyze_trade_history(
            trade_history, self.data, self.symbol, 
            signal_var=self.params[0], 
            blackflag_var=self.params[1], 
            supertrend_var=self.params[2], 
            time_loss_var=self.params[3]
        )
        self.result=result
        
    def process_order(self, row: DataRow):
        """주문 처리 로직"""
        remove_orders = []
        position_size = 0
        avg_entry_price = 0
        close_position=False
        for order in self.active_orders:
            position_size += order.position_size
            avg_entry_price += order.entry_price * abs(order.position_size)
            if row.Index != order.entry_time:
                if order.order_type == OrderType.LIMIT:
                    if order.check_limit_order(row):
                        order.close_order(row, CloseType.TAKE_PROFIT)
                        remove_orders.append(order)
                        self.add_trade_record(order)
                        continue
                    
                elif order.order_type == OrderType.TRAILING:
                    if order.status == OrderStatus.PENDING:
                        if order.check_activation_price(row):
                            order.status = OrderStatus.ACTIVATED
                            order.activated_time = row.Index
                            
                    # elif 사용 금지
                    if order.status == OrderStatus.ACTIVATED:
                        if order.check_trailing_stop(row, self.data_5m):
                            order.close_order(row, CloseType.TAKE_PROFIT)
                            remove_orders.append(order)
                            self.add_trade_record(order)
                            continue
                        
                elif order.order_type == OrderType.MARKET:
                    if self.check_take_profit_conditions(row, order):
                        order.close_order(row, CloseType.TAKE_PROFIT)
                        remove_orders.append(order)
                        self.add_trade_record(order)
                        continue
                
                # 주문에 대한 exit 개념
                if order.stop_loss_price is not None:
                    if order.check_stop_loss_conditions(row):
                        order.close_order(row, CloseType.STOP_LOSS)
                        remove_orders.append(order)
                        self.add_trade_record(order)
                        continue
        
        # 전체 포지션에 대한 close 개념
        if position_size != 0 and len(self.active_orders) != len(remove_orders) and self.check_loss_conditions(row, position_size, order.entry_time):
            close_position=True
                
        # 전체 포지션 정리
        if close_position:
            avg_entry_price=avg_entry_price/abs(position_size)
            close_order = Order(
                symbol=self.symbol,
                position_side=order.position_side,
                order_type=OrderType.MARKET,
                position_size=position_size,
                entry_price=avg_entry_price,
                entry_time=order.entry_time,
                interval=self.interval,
                status=OrderStatus.FILLED,
                exit_price=row.close,
                exit_time=row.Index,
                close_type=CloseType.STOP_LOSS
            )
            self.add_trade_record(close_order)
            self.active_orders=[]
        else:
            for order in remove_orders:
                self.active_orders.remove(order)
            
            # close position이 아니고 기존 주문이 없으면 시그널 발생시 포지션 진입
            if len(self.active_orders) == 0 :
                long_signal, short_signal = self.check_entry_signals(row)
                if long_signal:
                    self.open_position(row, OrderPositionSide.LONG)
                elif short_signal:
                    self.open_position(row, OrderPositionSide.SHORT)
                return
