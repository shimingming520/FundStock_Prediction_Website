import pandas as pd
import numpy as np
import torch
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 不限制显示宽度

class FundDataProcessor:
    def __init__(self,data_path_or_df,save_path):
        self.data_path_or_df = data_path_or_df
        self.save_path = save_path
        # self.scaler = StandardScaler()
        self.feature_columns = []

    def load_and_clean_data(self):
        """加载和清洗数据"""
        if isinstance(self.data_path_or_df, str):
            df = pd.read_csv(self.data_path_or_df)
        else:
            df = self.data_path_or_df.copy()

        # 确保日期格式
        df['净值日期'] = pd.to_datetime(df['净值日期'])
        df = df.sort_values('净值日期').reset_index(drop=True)

        # 处理数值字段
        df['单位净值'] = df['单位净值'].astype(float)
        df['累计净值'] = df['累计净值'].astype(float)
        df['日增长率'] = df['日增长率'].str.rstrip('%').astype(float)

        # 处理分类变量
        df['申购状态'] = df['申购状态'].map({'开放申购': 1, '暂停申购': 0}).fillna(0)
        df['赎回状态'] = df['赎回状态'].map({'开放赎回': 1, '暂停赎回': 0}).fillna(0)
        df['分红送配'] = df['分红送配'].notna().astype(int)  # 是否有分红

        # 检查缺失值
        print(f"数据总行数: {len(df)}")
        print(f"缺失值统计:\n{df.isnull().sum()}")

        # 填充可能的缺失值（使用前向填充）
        df = df.ffill()

        return df

    def create_fund_features(self,df_data):
        """创建基金特有的特征 - 修复版本"""
        df = df_data.copy()

        # 1. 技术指标 - 使用向量化操作避免索引问题
        df['MA_5'] = df['单位净值'].rolling(window=5).mean()
        df['MA_20'] = df['单位净值'].rolling(window=20).mean()
        df['Volatility_5'] = df['日增长率'].rolling(window=5).std()
        df['Volatility_20'] = df['日增长率'].rolling(window=20).std()

        # 2. 动量指标 - 使用shift避免apply
        df['Momentum_5'] = (df['单位净值'] / df['单位净值'].shift(5) - 1).fillna(0)
        df['Momentum_10'] = (df['单位净值'] / df['单位净值'].shift(10) - 1).fillna(0)

        # 3. 相对强弱指标 (RSI) - 修复版本
        def calculate_rsi(prices, window=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.fillna(50)  # 填充NaN为中性值50

        df['RSI_14'] = calculate_rsi(df['单位净值'])

        # 4. 布林带
        df['BB_Middle'] = df['单位净值'].rolling(window=20).mean()
        bb_std = df['单位净值'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + 2 * bb_std
        df['BB_Lower'] = df['BB_Middle'] - 2 * bb_std
        # 避免除零错误
        bb_range = df['BB_Upper'] - df['BB_Lower']
        df['BB_Position'] = (df['单位净值'] - df['BB_Lower']) / bb_range.where(bb_range != 0, 1)

        # 5. 价格排名特征 - 修复版本（避免使用apply和负索引）
        def calculate_price_rank(series, window=20):
            """计算价格在滚动窗口中的相对位置"""
            ranks = []
            for i in range(len(series)):
                if i < window - 1:
                    ranks.append(0.5)  # 窗口不足时使用中性值
                else:
                    window_data = series.iloc[i - window + 1:i + 1]
                    min_val = window_data.min()
                    max_val = window_data.max()
                    current_val = series.iloc[i]

                    if max_val != min_val:
                        rank = (current_val - min_val) / (max_val - min_val)
                    else:
                        rank = 0.5
                    ranks.append(rank)
            return pd.Series(ranks, index=series.index)

        df['Price_Rank_20'] = calculate_price_rank(df['单位净值'], window=20)

        # 6. 时间特征
        df['day_of_week'] = df['净值日期'].dt.dayofweek
        df['month'] = df['净值日期'].dt.month
        df['quarter'] = df['净值日期'].dt.quarter
        df['is_month_end'] = df['净值日期'].dt.is_month_end.astype(int)
        df['is_quarter_end'] = df['净值日期'].dt.is_quarter_end.astype(int)

        # 7. 交易状态组合特征
        df['trading_status'] = df['申购状态'] + df['赎回状态']

        # 8. 异常波动检测 - 修复版本
        rolling_mean = df['日增长率'].abs().rolling(20).mean()
        rolling_std = df['日增长率'].abs().rolling(20).std()
        df['abnormal_move'] = ((df['日增长率'].abs() > rolling_mean + 2 * rolling_std) |
                               (df['日增长率'].abs() > 5)).astype(int)  # 或者绝对值大于5%

        # 9. 收益率特征
        df['return_1d'] = df['日增长率'] / 100  # 转换为小数
        df['return_5d'] = df['return_1d'].rolling(5).sum()
        df['return_20d'] = df['return_1d'].rolling(20).sum()

        # 10. 波动率特征
        df['volatility_5d'] = df['return_1d'].rolling(5).std()
        df['volatility_20d'] = df['return_1d'].rolling(20).std()

        # 11. 最大回撤
        def calculate_max_drawdown(series, window=20):
            """计算滚动最大回撤"""
            drawdowns = []
            for i in range(len(series)):
                if i < window - 1:
                    drawdowns.append(0)
                else:
                    window_data = series.iloc[i - window + 1:i + 1]
                    peak = window_data.expanding().max()
                    drawdown = (window_data - peak) / peak
                    max_drawdown = drawdown.min()
                    drawdowns.append(max_drawdown)
            return pd.Series(drawdowns, index=series.index)

        df['max_drawdown_20'] = calculate_max_drawdown(df['单位净值'], window=20)

        # 填充NaN值
        df = df.ffill().bfill()
        # 选择最终特征列
        feature_columns = [
            '单位净值', '累计净值', '日增长率', '申购状态', '赎回状态', '分红送配',
            'MA_5', 'MA_20', 'Volatility_5', 'Volatility_20', 'Momentum_5', 'Momentum_10',
            'RSI_14', 'BB_Middle', 'BB_Upper', 'BB_Lower', 'BB_Position',
            'Price_Rank_20', 'trading_status', 'abnormal_move',
            'return_1d', 'return_5d', 'return_20d', 'volatility_5d', 'volatility_20d',
            'max_drawdown_20'
        ]

        # 添加周期性编码的时间特征
        time_features = self.create_cyclic_time_features(df['净值日期'])
        df = pd.concat([df, time_features], axis=1)
        feature_columns.extend(time_features.columns.tolist())

        self.feature_columns = feature_columns

        print(f"特征创建完成，共 {len(feature_columns)} 个特征")
        print(f"数据形状: {df.shape}")

        # return df
        return df, feature_columns

    def create_cyclic_time_features(self, dates):
        """创建周期性的时间特征"""
        features = pd.DataFrame(index=dates.index)

        # 周期性编码
        features['day_sin'] = np.sin(2 * np.pi * dates.dt.dayofweek / 6)
        features['day_cos'] = np.cos(2 * np.pi * dates.dt.dayofweek / 6)
        features['month_sin'] = np.sin(2 * np.pi * dates.dt.month / 12)
        features['month_cos'] = np.cos(2 * np.pi * dates.dt.month / 12)

        return features

    def all_process(self):
        df = self.load_and_clean_data()
        df, feature_columns = self.create_fund_features(df)
        df.to_csv(self.save_path)
        return df, feature_columns
