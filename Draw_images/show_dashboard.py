import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utlis.Get_Lately_Data import Get_Lately_Data

def show_MA(data_path,Lately_time):
    df = Get_Lately_Data(data_path,Lately_time)
    df['净值日期'] = pd.to_datetime(df['净值日期'])
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['单位净值'],
        mode='lines',
        name='单位净值',
        line=dict(color='blue', width=1, dash='solid'),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>单位净值: %{y:.4f}<extra></extra>',  # 修正日期格式和y轴标签
        showlegend=True  # 确保显示在图例中
    ))
    fig2.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['MA_5'],
        mode='lines',
        name='MA_5',
        line=dict(color='black', width=1, dash='solid'),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>单位净值: %{y:.4f}<extra></extra>',  # 修正日期格式和y轴标签
        showlegend=True  # 确保显示在图例中
    ))
    fig2.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['MA_10'],
        mode='lines',
        name='MA_10',
        line=dict(color='yellow', width=1, dash='solid'),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>单位净值: %{y:.4f}<extra></extra>',  # 修正日期格式和y轴标签
        showlegend = True  # 确保显示在图例中
    ))
    # 添加MA_20均线
    fig2.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['MA_20'],
        mode='lines',
        name='MA_20',
        line=dict(color='red', width=1),
        marker=dict(size=4, symbol='diamond'),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>单位净值: %{y:.4f}<extra></extra>',  # 修正日期格式和y轴标签
        text=[f'MA_20: {y:.3f}' for y in df['MA_20']],
        # textposition="bottom center",
        # textfont=dict(size=9, color='red'),
        showlegend = True  # 确保显示在图例中
    ))
    fig2.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['MA_30'],
        mode='lines',  # 添加markers以便更好显示标签
        name='MA_30',  # 修改名称与实际数据一致
        line=dict(color='green', width=1, dash='solid'),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>单位净值: %{y:.4f}<extra></extra>',  # 修正日期格式和y轴标签
        # 添加标签相关配置
        text=[f'MA_20: {y:.2f}' for y in df['MA_20']],  # 标签文本
        # textposition="top center",  # 标签位置
        # textfont=dict(size=10, color='red'),  # 标签字体
        showlegend=True  # 确保显示在图例中
    ))
    fig2.update_layout(
        title='基金净值与移动平均线',
        # xaxis_title='日期',
        # yaxis_title='净值',
        hovermode='x unified',  # 统一悬停显示
        yaxis=dict(
            tickformat='.2%',  # 显示为百分比，保留2位小数
            # title='净值百分比'
        ),
        xaxis=dict(
            tickformat='%Y-%m-%d',  # 设置x轴刻度格式
            type='date'
        ),
        legend=dict(
            orientation="h",  # 水平图例
            yanchor="bottom", # 锚点在底部
            y=1.02, # 在图像上方
            xanchor="center",
            x=0.5,           # 水平居中
            bgcolor='rgba(255,255,255,0.8)',  # 半透明背景
            bordercolor='lightgray',
            borderwidth=1
        )
    )
    # 修正属性名称：spikemode 而不是 spike_mode
    fig2.update_xaxes(
        showspikes=True,
        spikecolor='black',
        spikethickness=1,
        spikedash='dot',
        spikemode='across',  # 正确的属性名
        spikesnap='cursor'
    )

    st.plotly_chart(fig2, use_container_width=True)
