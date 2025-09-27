import streamlit as st
from utlis.Draw_data import get_data
import matplotlib.pyplot as plt
def show_dashboard():
    data_dict = get_data(r"F:\PyCharm_Project\FundStock_Prediction_Website\Data\Funds\050026.csv")
    st.title("基金数据看板")
    # 使用Matplotlib绘制折线图
    x = data_dict['dates']
    y = data_dict['MA_5']
    df_data =1
    st.line_chart(df_data)