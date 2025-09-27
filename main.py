from Model.flowstate.modeling_flowstate import FlowStateForPrediction
from Scrapy_Data.get_funds_history_data import Get_Fund_History_Data
from utlis.FundDataProcessor import FundDataProcessor
from utlis.FundTimeSeriesDataset import FundTimeSeriesDataset
from datetime import datetime
now_date = datetime.now()
# 格式化为字符串
formatted_date = now_date.strftime("%Y-%m-%d")
fund_df = Get_Fund_History_Data('050026', start_date='1999-02-01', end_date=formatted_date)
funddataprocessor = FundDataProcessor(fund_df, r'F:\PyCharm_Project\FundStock_Prediction_Website\Data\FundS\050026.csv')
df, columns = funddataprocessor.all_process()
if __name__ == '__main__':
    pass