import pandas as pd
import os
import sys
# 添加utils所在目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# 或者直接添加当前目录的父目录
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
def Get_Lately_Data(data_path,Lately_time=None,start_date=None,end_date=None):
    if str(data_path).endswith('.csv'):
        df_origin = pd.read_csv(data_path)
    else:
        df_origin = data_path
    df_origin['净值日期'] = pd.to_datetime(df_origin['净值日期'])
    if Lately_time:
        if Lately_time == '成立以来':
            df = df_origin.copy()
        elif Lately_time == "近1个月":
            last_date = df_origin['净值日期'].max()
            one_month_ago = last_date - pd.DateOffset(months=1)
            # 筛选数据
            df = df_origin[df_origin['净值日期'] >= one_month_ago]
        elif Lately_time == "近3个月":
            last_date = df_origin['净值日期'].max()
            one_month_ago = last_date - pd.DateOffset(months=3)
            # 筛选数据
            df = df_origin[df_origin['净值日期'] >= one_month_ago]
        elif Lately_time == "近6个月":
            last_date = df_origin['净值日期'].max()
            one_month_ago = last_date - pd.DateOffset(months=6)
            # 筛选数据
            df = df_origin[df_origin['净值日期'] >= one_month_ago]
        elif Lately_time == "近1年":
            last_date = df_origin['净值日期'].max()
            one_month_ago = last_date - pd.DateOffset(months=12)
            # 筛选数据
            df = df_origin[df_origin['净值日期'] >= one_month_ago]
        elif Lately_time == "近3年":
            last_date = df_origin['净值日期'].max()
            one_month_ago = last_date - pd.DateOffset(months=36)
            # 筛选数据
            df = df_origin[df_origin['净值日期'] >= one_month_ago]
        elif Lately_time == "近5年":
            last_date = df_origin['净值日期'].max()
            one_month_ago = last_date - pd.DateOffset(months=60)
            # 筛选数据
            df = df_origin[df_origin['净值日期'] >= one_month_ago]
        elif Lately_time == "近10年":
            last_date = df_origin['净值日期'].max()
            one_month_ago = last_date - pd.DateOffset(months=120)
            # 筛选数据
            df = df_origin[df_origin['净值日期'] >= one_month_ago]
        else:
            raise ValueError("没有这个值")
    else:
        # 过滤数据
        mask = (df_origin['净值日期'] >= pd.Timestamp(start_date)) & \
               (df_origin['净值日期'] <= pd.Timestamp(end_date))
        df = df_origin.loc[mask]
    return df

if __name__ == '__main__':
    print(Get_Lately_Data(r"F:\PyCharm_Project\FundStock_Prediction_Website\Data\Funds\050026.csv", '近1年'))