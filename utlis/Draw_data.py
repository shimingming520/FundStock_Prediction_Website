import matplotlib
matplotlib.use('TkAgg')  # 在导入pyplot之前设置后端
import matplotlib.pyplot as plt
import pandas as pd
def get_data(data_path):
    data_dict = {}
    df = pd.read_csv(data_path)
    df['净值日期'] = pd.to_datetime(df['净值日期'])
    dates = df['净值日期']
    MA_5 = df['MA_5']
    data_dict['MA_5'] = MA_5
    data_dict['dates'] = dates
    return data_dict
    # print(MA_5)
    # print(dates)
    # # 创建图形
    # plt.figure(figsize=(12, 6))
    #
    # # 绘制曲线
    # plt.plot(dates, MA_5, linewidth=2, label='MA_5')
    #
    # # 设置标题和标签
    # plt.title('MA_5趋势图', fontsize=14)
    # plt.xlabel('时间', fontsize=12)
    # plt.ylabel('MA_5值', fontsize=12)
    #
    # # 旋转x轴标签以避免重叠
    # plt.xticks(rotation=45)
    #
    # # 添加网格和图例
    # plt.grid(True, alpha=0.3)
    # plt.legend()
    #
    # # 自动调整布局
    # plt.tight_layout()
    #
    # # 显示图形
    # plt.show()
# get_data(r"F:\PyCharm_Project\FundStock_Prediction_Website\Data\Funds\050026.csv")