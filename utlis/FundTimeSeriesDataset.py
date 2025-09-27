from utlis.FundDataProcessor import FundDataProcessor
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.preprocessing import StandardScaler
class FundTimeSeriesDataset(Dataset):
    def __init__(self, features, targets, scale_factors=None):
        self.features = features  # [num_samples, context_length, num_features]
        self.targets = targets  # [num_samples, prediction_length]
        self.scale_factors = scale_factors

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        sample = {
            'past_values': self.features[idx],
            'future_values': self.targets[idx],
        }

        if self.scale_factors is not None:
            sample['scale_factor'] = torch.FloatTensor([self.scale_factors[idx]])

        return sample


def create_fund_dataloaders(training_data, batch_size=32):
    """创建基金数据加载器"""
    train_dataset = FundTimeSeriesDataset(
        training_data['X_train'],
        training_data['y_train']
    )

    test_dataset = FundTimeSeriesDataset(
        training_data['X_test'],
        training_data['y_test']
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader

def prepare_training_data(df, feature_columns, target_column='单位净值',
                          context_length=60, prediction_length=10, test_size=0.2):
    """准备训练数据 - 修复版本"""

    # 确保有足够的数据
    if len(df) < context_length + prediction_length + 10:
        raise ValueError(
            f"数据量不足。需要至少 {context_length + prediction_length + 10} 行数据，当前只有 {len(df)} 行")
    scaler = StandardScaler()
    # 选择特征和目标
    features = df[feature_columns].values
    targets = df[target_column].values

    # 标准化特征（除了分类变量）
    numeric_columns = [col for col in feature_columns if col not in
                       ['申购状态', '赎回状态', '分红送配', 'trading_status', 'abnormal_move']]
    numeric_indices = [feature_columns.index(col) for col in numeric_columns if col in feature_columns]

    if numeric_indices:
        features_scaled = features.copy()
        features_scaled[:, numeric_indices] = scaler.fit_transform(features[:, numeric_indices])
    else:
        features_scaled = features

    # 创建序列数据 - 更安全的索引方式
    sequences, sequence_targets = [], []
    valid_dates = []

    total_length = len(features_scaled)

    for i in range(context_length, total_length - prediction_length):
        # 检查索引有效性
        if i - context_length < 0 or i + prediction_length > total_length:
            continue

        seq_features = features_scaled[i - context_length:i]
        seq_target = targets[i:i + prediction_length]

        # 检查是否有NaN值
        if np.any(np.isnan(seq_features)) or np.any(np.isnan(seq_target)):
            continue

        sequences.append(seq_features)
        sequence_targets.append(seq_target)
        valid_dates.append(df['净值日期'].iloc[i])

    if not sequences:
        raise ValueError("无法创建有效的训练序列，请检查数据质量或调整参数")

    sequences = np.array(sequences)
    sequence_targets = np.array(sequence_targets)

    print(f"成功创建 {len(sequences)} 个序列")
    print(f"每个序列特征形状: {sequences[0].shape}")
    print(f"目标形状: {sequence_targets[0].shape}")

    # 划分训练测试集（按时间顺序）
    split_idx = int(len(sequences) * (1 - test_size))

    if split_idx == 0 or split_idx == len(sequences):
        # raise ValueError("训练/测试划分无效，请调整test_size参数")
        X_train, X_test = sequences,[]
        y_train, y_test = sequence_targets,[]
        dates_train, dates_test = valid_dates, []
    else:
        X_train, X_test = sequences[:split_idx], sequences[split_idx:]
        y_train, y_test = sequence_targets[:split_idx], sequence_targets[split_idx:]
        dates_train, dates_test = valid_dates[:split_idx], valid_dates[split_idx:]

    # print(f"训练集大小: {X_train.shape}")
    # print(f"测试集大小: {X_test.shape}")
    # print(f"预测长度: {prediction_length}")

    return {
        'X_train': torch.FloatTensor(X_train),
        'X_test': torch.FloatTensor(X_test),
        'y_train': torch.FloatTensor(y_train),
        'y_test': torch.FloatTensor(y_test),
        'dates_train': dates_train,
        'dates_test': dates_test,
        'feature_names': feature_columns,
        "scaler":scaler
    }
def process_fund_data_for_training(data_path, context_length=60, prediction_length=10):
    """完整的基金数据处理流程"""

    # # 1. 初始化处理器
    # processor = FundDataProcessor(data_path,save_path=save_path)
    #
    # # 2. 加载和清洗数据
    # df_with_features,feature_columns = processor.all_process()
    if data_path.endswith('.csv'):
        df_with_features = pd.read_csv(data_path)
    else:
        df_with_features = data_path
    feature_columns = [
        '单位净值', '累计净值', '日增长率', '申购状态', '赎回状态', '分红送配',
        'MA_5', 'MA_20', 'Volatility_5', 'Volatility_20', 'Momentum_5', 'Momentum_10',
        'RSI_14', 'BB_Middle', 'BB_Upper', 'BB_Lower', 'BB_Position',
        'Price_Rank_20', 'trading_status', 'abnormal_move',
        'return_1d', 'return_5d', 'return_20d', 'volatility_5d', 'volatility_20d',
        'max_drawdown_20',"day_sin","day_cos","month_sin","month_cos"
    ]
    # 4. 准备训练数据
    training_data = prepare_training_data(
        df_with_features,
        feature_columns,
        context_length=context_length,
        prediction_length=prediction_length
    )

    # 5. 创建数据加载器
    train_loader, test_loader = create_fund_dataloaders(training_data)

    return {
        'train_loader': train_loader,
        'test_loader': test_loader,
        'training_data': training_data,
        'feature_names': feature_columns
    }
if __name__ == '__main__':
    data_processor = process_fund_data_for_training(
        r"F:\PyCharm_Project\FundStock_Prediction_Website\Data\Funds\050026.csv")
    print(data_processor['training_data']['scaler'])