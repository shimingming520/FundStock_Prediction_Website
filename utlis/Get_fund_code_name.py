import os
import efinance as ef

def get_fund_name_ef(fund_code):
    """使用efinance获取基金名称"""
    try:
        fund_info = ef.fund.get_base_info(fund_code)
        return fund_info['基金简称']
    except Exception as e:
        return f"获取失败: {e}"
def get_fund_code_name():
    base_path = r"F:\PyCharm_Project\FundStock_Prediction_Website\Data\Funds"
    fund_code_name_list = []
    file_list = [f for f in os.listdir(base_path) if f.endswith('.csv')]
    for file in file_list:
        fund_code = file.split('.')[0]
        fund_name = get_fund_name_ef(fund_code)
        fund_code_name_list.append(fund_name + f"(代码:{fund_code})")
    return fund_code_name_list
if __name__ == '__main__':
    print(get_fund_name_ef("050026"))