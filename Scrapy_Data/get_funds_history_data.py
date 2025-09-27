# 导入需要的模块
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 不限制显示宽度
def convert_date_column(df, date_column='净值日期',date_format='%Y-%m-%d'):
    """
    通用日期列转换函数，处理各种输入类型
    """
    # 检查当前类型
    current_dtype = df[date_column].dtype
    print(f"当前数据类型: {current_dtype}")
    # 根据不同类型进行处理
    if df['净值日期'].dtype == 'object':  # 字符串类型
        df['净值日期'] = pd.to_datetime(df['净值日期']).dt.strftime(date_format)
    elif 'datetime' in str(df['净值日期'].dtype):  # 已经是datetime类型
        df['净值日期'] = df['净值日期'].dt.strftime(date_format)
    else:
        # 其他类型（如整数时间戳）
        df['净值日期'] = pd.to_datetime(df['净值日期']).dt.strftime(date_format)
    # 转换为datetime类型（自动推断格式）
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    # 检查转换是否成功
    null_count = df[date_column].isnull().sum()
    if null_count > 0:
        print(f"警告: {null_count} 个日期转换失败")
    # 格式化为目标格式
    df[date_column] = df[date_column].dt.strftime(date_format)
    return df

"""
其中，每个参数的意义是：
type：lsjz表示历史净值
code：表示基金代码，如050026表示博时医疗保健行业混合
page：表示获取的数据的页码
per：表示获取的数据每页显示的条数
sdate：表示开始时间
edate：表示结束时间
"""
def get_html(code, start_date, end_date, page=1, per=20):
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={0}&page={1}&sdate={2}&edate={3}&per={4}'.format(
        code, page, start_date, end_date, per)
    rsp = requests.get(url)
    html = rsp.text
    return html


def Get_Fund_History_Data(code, start_date, end_date, page=1, per=20):
    # 获取html
    html = get_html(code, start_date, end_date, page, per)
    soup = BeautifulSoup(html, 'html.parser')
    # 获取总页数
    pattern = re.compile('pages:(.*),')
    result = re.search(pattern, html).group(1)
    total_page = int(result)
    # 获取表头信息
    heads = []
    # for head in soup.findAll("th"):
    for head in soup.find_all("th"):
        heads.append(head.contents[0])
    # print(heads)
    # 数据存取列表
    records = []
    # 获取每一页的数据
    current_page = 1
    while current_page <= total_page:
        html = get_html(code, start_date, end_date, current_page, per)
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)
        # print(soup.find_all("tbody")[0].find_all("tr"))
        # 获取数据
        for row in soup.find_all("tbody")[0].find_all("tr"):
            row_records = []
            for record in row.find_all('td'):
                val = record.contents
                # 处理空值
                if val == []:
                    row_records.append(np.nan)
                else:
                    row_records.append(val[0])
            # 记录数据
            records.append(row_records)
        # 下一页
        current_page = current_page + 1
    # 将数据转换为Dataframe对象
    np_records = np.array(records)
    fund_df = pd.DataFrame()
    for col, col_name in enumerate(heads):
        fund_df[col_name] = np_records[:, col]
    # 使用示例
    fund_df = convert_date_column(fund_df, '净值日期')
    # 按照日期排序
    fund_df['净值日期'] = pd.to_datetime(fund_df['净值日期'], format='%Y-%m-%d')
    """
        by='净值日期': 指定按照"净值日期"这一列进行排序
        axis=0: 按行排序（默认值，通常可以省略）
        ascending=True: 升序排列（从早到晚）
        .reset_index(drop=True)
        reset_index(): 重置索引，将原来的索引变成普通列
        drop=True: 不保留原来的索引，直接丢弃
    
        将"净值日期"列设置为新的索引
        fund_df = fund_df.set_index('净值日期')
        数据类型处理
    """
    fund_df = fund_df.sort_values(by='净值日期', axis=0, ascending=True).reset_index(drop=True)
    fund_df['单位净值'] = fund_df['单位净值'].astype(float)
    fund_df['累计净值'] = fund_df['累计净值'].astype(float)
    # fund_df['日增长率'] = fund_df['日增长率'].str.strip('%').astype(float)
    # fund_df = fund_df.rename(columns={'日增长率': '日增长率(%)'})
    # 按指定列顺序重新索引
    desired_columns = ['净值日期', '单位净值', "累计净值", '日增长率', '申购状态',"赎回状态","分红送配"]
    fund_df = fund_df.reindex(columns=desired_columns)

    # 如果有些列不存在，使用fill_value参数
    fund_df = fund_df.reindex(columns=desired_columns, fill_value=0)
    return fund_df

if __name__ == '__main__':
    from datetime import datetime

    now = datetime.now()

    # 格式化为字符串
    formatted_date = now.strftime("%Y-%m-%d")
    from utlis.FundDataProcessor import FundDataProcessor
    fund_df = Get_Fund_History_Data('050026', start_date='1999-02-01', end_date=formatted_date)
    funddataprocessor = FundDataProcessor(fund_df,r'F:\PyCharm_Project\FundStock_Prediction_Website\Data\FundS\050026.csv')
    df, columns = funddataprocessor.all_process()
    print(df)
    # print(fund_df)
    # fig, axes = plt.subplots(nrows=2, ncols=1)
    # fund_df[['单位净值', '累计净值']].plot(ax=axes[0])
    # fund_df['日增长率'].plot(ax=axes[1])
    # plt.show()