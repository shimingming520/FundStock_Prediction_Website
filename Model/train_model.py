from utlis.FundTimeSeriesDataset import process_fund_data_for_training
from flowstate.configuration_flowstate import FlowStateConfig
from Model.flowstate.modeling_flowstate import FlowStateForPrediction
import torch.optim as optim
from torch.optim.lr_scheduler import CosineAnnealingLR
import torch
# 模型配置
config = FlowStateConfig(
    context_length=512,           # 上下文长度
    prediction_length=96,         # 预测长度
    embedding_feature_dim=128,    # 嵌入维度
    encoder_state_dim=256,        # 编码器状态维度
    encoder_num_layers=4,         # 编码器层数
    encoder_num_hippo_blocks=4,   # Hippo块数量
    decoder_type="legs",          # 解码器类型: "legs", "hlegs", "four"
    decoder_dim=64,               # 解码器维度
    decoder_patch_len=96,         # 解码器补丁长度
    quantiles=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],  # 分位数
    prediction_type="quantile",   # 预测类型
    with_missing=False,           # 是否处理缺失值
    batch_first=True,             # 批次维度在前
    scale_factor=1.0,             # 缩放因子
)

# 初始化模型
model = FlowStateForPrediction(config)


def train_model(model, train_loader, val_loader, epochs=100, learning_rate=1e-3):
    """
    训练FlowState模型
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # 优化器
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)

    # 损失函数 - 分位数损失
    def quantile_loss(predictions, targets, quantiles):
        """
        分位数损失函数
        predictions: (batch_size, num_quantiles, pred_length)
        targets: (batch_size, pred_length)
        """
        losses = []
        for i, q in enumerate(quantiles):
            error = targets.unsqueeze(1) - predictions[:, i, :]
            loss = torch.max((q - 1) * error, q * error)
            losses.append(loss.mean())
        return torch.stack(losses).mean()

    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        # 训练阶段
        model.train()
        train_loss = 0.0

        for batch_idx, (past_values, future_values) in enumerate(train_loader):
            past_values = past_values.to(device)
            future_values = future_values.to(device)

            optimizer.zero_grad()

            # 前向传播
            outputs = model(
                past_values=past_values,
                future_values=future_values,
                prediction_length=config.prediction_length,
                scale_factor=1.0,
                return_loss=True
            )

            # 计算损失
            loss = quantile_loss(
                outputs.prediction_outputs.squeeze(-1),
                future_values.squeeze(-1),
                config.quantiles
            )

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss += loss.item()

            if batch_idx % 100 == 0:
                print(f'Epoch: {epoch}, Batch: {batch_idx}, Loss: {loss.item():.4f}')

        # 验证阶段
        model.eval()
        val_loss = 0.0

        with torch.no_grad():
            for past_values, future_values in val_loader:
                past_values = past_values.to(device)
                future_values = future_values.to(device)

                outputs = model(
                    past_values=past_values,
                    prediction_length=config.prediction_length,
                    scale_factor=1.0
                )

                loss = quantile_loss(
                    outputs.prediction_outputs.squeeze(-1),
                    future_values.squeeze(-1),
                    config.quantiles
                )
                val_loss += loss.item()

        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)

        train_losses.append(avg_train_loss)
        val_losses.append(avg_val_loss)

        scheduler.step()

        print(f'Epoch {epoch + 1}/{epochs}')
        print(f'Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}')
        print(f'Learning Rate: {scheduler.get_last_lr()[0]:.6f}')
        print('-' * 50)

    return train_losses, val_losses

data_processor = process_fund_data_for_training(r"F:\PyCharm_Project\FundStock_Prediction_Website\Data\Funds\050026.csv")
print(data_processor)