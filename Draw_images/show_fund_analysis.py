import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utlis.FundDataProcessor import FundDataProcessor

def show_fund_analysis(df,analysis_type="移动平均线",detail=None):
    """
    基金综合分析图表
    """
    df['净值日期'] = pd.to_datetime(df['净值日期'])
    if analysis_type == "移动平均线":
        show_MA_analysis(df,detail)
    elif analysis_type == "布林带分析":
        show_bollinger_bands(df)
    elif analysis_type == "RSI指标":
        show_RSI_analysis(df)
    elif analysis_type == "波动率分析":
        show_volatility_analysis(df)
    elif analysis_type == "动量分析":
        show_momentum_analysis(df)
    elif analysis_type == "综合技术分析":
        show_comprehensive_analysis(df)


def show_MA_analysis(df,detail=None):
    """移动平均线分析"""
    fig = go.Figure()
    # 对净值数据进行归一化，使第一个数据点为0%
    first_value = df['单位净值'].iloc[0]
    df['单位净值_normalized'] = (df['单位净值'] - first_value) / first_value

    # 对移动平均线也进行同样的归一化处理
    df['MA_5_normalized'] = (df['MA_5'] - first_value) / first_value
    df['MA_10_normalized'] = (df['MA_10'] - first_value) / first_value
    df['MA_20_normalized'] = (df['MA_20'] - first_value) / first_value
    df['MA_30_normalized'] = (df['MA_30'] - first_value) / first_value

    # 单位净值
    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['单位净值_normalized'],
        mode='lines',
        name='单位净值',
        line=dict(color='blue', width=1.2),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>净值变化: %{y:.2%}<extra></extra>'
    ))
    # # 在右上角添加最大和最小值的文本注释
    # annotations = [
    #     dict(
    #         x=0.98,  # x位置（相对于画布，0-1之间）
    #         y=0.98,  # y位置（相对于画布，0-1之间）
    #         xref="paper",
    #         yref="paper",
    #         text=f"最大净值: {title_detail[0]:.2}<br>最小净值: {title_detail[1]:.2}<br>当前净值: {title_detail[-1]:.2}",
    #         showarrow=False,
    #         bgcolor="rgba(255,255,255,0.8)",  # 半透明背景
    #         bordercolor="lightgray",
    #         borderwidth=1,
    #         borderpad=8,
    #         font=dict(size=11, color="black"),
    #         align="left"
    #     )
    # ]
    # 移动平均线
    ma_config = {
        'MA_5_normalized': {'name': 'MA_5', 'color': 'black'},
        'MA_10_normalized': {'name': 'MA_10', 'color': 'orange'},
        'MA_20_normalized': {'name': 'MA_20', 'color': 'red'},
        'MA_30_normalized': {'name': 'MA_30', 'color': 'green'}
    }

    for ma_col, config in ma_config.items():
        if ma_col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['净值日期'],
                y=df[ma_col],
                mode='lines',
                name=config['name'],
                line=dict(color=config['color'], width=1, dash='solid'),
                hovertemplate=f'日期: %{{x|%Y-%m-%d}}<br>{config["name"]}: %{{y:.2%}}<extra></extra>',
                showlegend=True
            ))

    fig.update_layout(
        title=detail,
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
        ),
        height=500,
        # annotations=annotations
    )
    # 修正属性名称：spikemode 而不是 spike_mode
    fig.update_xaxes(
        showspikes=True,
        spikecolor='black',
        spikethickness=1,
        spikedash='dot',
        spikemode='across',  # 正确的属性名
        spikesnap='cursor'
    )

    # 添加交叉信号分析
    st.plotly_chart(fig, use_container_width=True)

    # 技术分析说明
    with st.expander("移动平均线分析说明"):
        st.write("""
        **移动平均线(MA)分析:**
        - **MA_5(5日线)**: 短期趋势，黑色线
        - **MA_10(10日线)**: 中期趋势，橙色线  
        - **MA_20(20日线)**: 中长期趋势，红色线
        - **MA_30(30日线)**: 长期趋势，绿色线

        **交易信号:**
        - 金叉: 短期MA上穿长期MA，买入信号
        - 死叉: 短期MA下穿长期MA，卖出信号
        - 多头排列: 短期>中期>长期，上涨趋势
        - 空头排列: 短期<中期<长期，下跌趋势
        """)


def show_bollinger_bands(df):
    """布林带分析"""
    if 'BB_Upper' not in df.columns or 'BB_Lower' not in df.columns:
        st.warning("布林带数据未计算，请先运行特征工程")
        return

    fig = go.Figure()

    # 布林带区域
    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['BB_Upper'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['BB_Lower'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(173,216,230,0.3)',
        name='布林带',
        hovertemplate='日期: %{x|%Y-%m-%d}<br>布林带范围<extra></extra>'
    ))

    # 单位净值和中轨
    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['单位净值'],
        mode='lines',
        name='单位净值',
        line=dict(color='blue', width=2),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>单位净值: %{y:.4f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['BB_Middle'],
        mode='lines',
        name='中轨(MA20)',
        line=dict(color='red', width=1, dash='dash'),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>中轨: %{y:.4f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['BB_Upper'],
        mode='lines',
        name='上轨',
        line=dict(color='gray', width=1),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>上轨: %{y:.4f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['BB_Lower'],
        mode='lines',
        name='下轨',
        line=dict(color='gray', width=1),
        hovertemplate='日期: %{x|%Y-%m-%d}<br>下轨: %{y:.4f}<extra></extra>'
    ))

    fig.update_layout(
        title='布林带分析',
        hovermode='x unified',
        yaxis=dict(title='净值'),
        xaxis=dict(title='日期'),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # 布林带位置分析
    if 'BB_Position' in df.columns:
        st.subheader("布林带位置分析")
        latest_bb_pos = df['BB_Position'].iloc[-1]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("当前布林带位置", f"{latest_bb_pos:.2%}")

        with col2:
            if latest_bb_pos > 0.8:
                st.metric("信号", "超买区域", delta="警惕")
            elif latest_bb_pos < 0.2:
                st.metric("信号", "超卖区域", delta="机会")
            else:
                st.metric("信号", "正常区域", delta="中性")

    with st.expander("布林带分析说明"):
        st.write("""
        **布林带分析:**
        - **上轨**: MA20 + 2倍标准差
        - **中轨**: 20日移动平均线
        - **下轨**: MA20 - 2倍标准差

        **交易信号:**
        - 价格触及上轨: 可能超买，考虑卖出
        - 价格触及下轨: 可能超卖，考虑买入
        - 布林带收窄: 波动率降低，可能即将突破
        - 布林带扩张: 波动率增加，趋势可能加速
        """)


def show_RSI_analysis(df):
    """RSI指标分析"""
    if 'RSI_14' not in df.columns:
        st.warning("RSI数据未计算，请先运行特征工程")
        return

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('单位净值', 'RSI指标'),
                        row_heights=[0.7, 0.3])

    # 单位净值
    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['单位净值'],
        mode='lines',
        name='单位净值',
        line=dict(color='blue', width=2)
    ), row=1, col=1)

    # RSI指标
    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['RSI_14'],
        mode='lines',
        name='RSI_14',
        line=dict(color='purple', width=2)
    ), row=2, col=1)

    # 添加RSI参考线
    fig.add_hline(y=70, line_dash="dash", line_color="red",
                  annotation_text="超买线", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green",
                  annotation_text="超卖线", row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray",
                  row=2, col=1)

    fig.update_layout(
        title='RSI相对强弱指标分析',
        hovermode='x unified',
        height=600
    )

    fig.update_yaxes(title_text="净值", row=1, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    fig.update_xaxes(title_text="日期", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # RSI当前状态分析
    latest_rsi = df['RSI_14'].iloc[-1]
    st.subheader("RSI当前状态")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前RSI值", f"{latest_rsi:.2f}")

    with col2:
        if latest_rsi > 70:
            st.metric("市场状态", "超买", delta="卖出信号", delta_color="inverse")
        elif latest_rsi < 30:
            st.metric("市场状态", "超卖", delta="买入信号")
        else:
            st.metric("市场状态", "中性", delta="持有")

    with st.expander("RSI指标说明"):
        st.write("""
        **RSI相对强弱指标:**
        - **超买区域(70以上)**: 市场可能过热，考虑卖出
        - **超卖区域(30以下)**: 市场可能过冷，考虑买入
        - **中性区域(30-70)**: 市场正常波动

        **使用技巧:**
        - RSI背离: 价格创新高而RSI未创新高，可能反转
        - RSI在50以上为强势，50以下为弱势
        - 结合其他指标使用效果更佳
        """)


def show_volatility_analysis(df):
    """波动率分析"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('单位净值', '波动率'),
                        row_heights=[0.6, 0.4])

    # 单位净值
    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['单位净值'],
        mode='lines',
        name='单位净值',
        line=dict(color='blue', width=2)
    ), row=1, col=1)

    # 波动率
    if 'Volatility_20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['净值日期'],
            y=df['Volatility_20'],
            mode='lines',
            name='20日波动率',
            line=dict(color='red', width=2)
        ), row=2, col=1)

    if 'volatility_20d' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['净值日期'],
            y=df['volatility_20d'],
            mode='lines',
            name='收益率波动率',
            line=dict(color='orange', width=1)
        ), row=2, col=1)

    fig.update_layout(
        title='波动率分析',
        hovermode='x unified',
        height=600
    )

    fig.update_yaxes(title_text="净值", row=1, col=1)
    fig.update_yaxes(title_text="波动率", row=2, col=1)
    fig.update_xaxes(title_text="日期", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)

    # 波动率统计
    st.subheader("波动率统计")
    if 'Volatility_20' in df.columns:
        recent_vol = df['Volatility_20'].tail(30).mean()
        historical_vol = df['Volatility_20'].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("近期波动率", f"{recent_vol:.4f}")
        with col2:
            st.metric("历史平均波动率", f"{historical_vol:.4f}")
        with col3:
            change = (recent_vol - historical_vol) / historical_vol
            st.metric("变化", f"{change:+.2%}")


def show_momentum_analysis(df):
    """动量分析"""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('单位净值', '动量指标'),
                        row_heights=[0.6, 0.4])

    # 单位净值
    fig.add_trace(go.Scatter(
        x=df['净值日期'],
        y=df['单位净值'],
        mode='lines',
        name='单位净值',
        line=dict(color='blue', width=2)
    ), row=1, col=1)

    # 动量指标
    if 'Momentum_5' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['净值日期'],
            y=df['Momentum_5'],
            mode='lines',
            name='5日动量',
            line=dict(color='green', width=1)
        ), row=2, col=1)

    if 'Momentum_10' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['净值日期'],
            y=df['Momentum_10'],
            mode='lines',
            name='10日动量',
            line=dict(color='red', width=1)
        ), row=2, col=1)

    # 添加零线
    fig.add_hline(y=0, line_dash="dash", line_color="black", row=2, col=1)

    fig.update_layout(
        title='动量指标分析',
        hovermode='x unified',
        height=600
    )

    fig.update_yaxes(title_text="净值", row=1, col=1)
    fig.update_yaxes(title_text="动量", tickformat='.2%', row=2, col=1)
    fig.update_xaxes(title_text="日期", row=2, col=1)

    st.plotly_chart(fig, use_container_width=True)


def show_comprehensive_analysis(df):
    """综合技术分析"""
    st.subheader("综合技术分析仪表板")
    # 创建多个子图
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        subplot_titles=('价格与移动平均线', '布林带', 'RSI', '动量'),
                        row_heights=[0.3, 0.25, 0.2, 0.25])

    # 1. 价格与移动平均线
    fig.add_trace(go.Scatter(
        x=df['净值日期'], y=df['单位净值'],
        name='单位净值', line=dict(color='blue', width=2)
    ), row=1, col=1)
    for ma_col, color in [('MA_5', 'black'),('MA_10', 'orange'), ('MA_20', 'red'), ('MA_30', 'green')]:
        if ma_col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['净值日期'], y=df[ma_col],
                name=ma_col, line=dict(color=color, width=1),hovertemplate='日期: %{x|%Y-%m-%d}<br>净值变化: %{y:.2%}<extra></extra>'
            ), row=1, col=1)

    # 2. 布林带
    if all(col in df.columns for col in ['BB_Upper', 'BB_Lower', 'BB_Middle']):
        fig.add_trace(go.Scatter(
            x=df['净值日期'], y=df['BB_Upper'],
            name='上轨', line=dict(color='gray', width=1),hovertemplate='日期: %{x|%Y-%m-%d}<br>净值变化: %{y:.2%}<extra></extra>',
            showlegend=False
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=df['净值日期'], y=df['BB_Lower'],
            name='下轨', line=dict(color='gray', width=1),
            fill='tonexty', fillcolor='rgba(173,216,230,0.3)',hovertemplate='日期: %{x|%Y-%m-%d}<br>净值变化: %{y:.2%}<extra></extra>',
            showlegend=False
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=df['净值日期'], y=df['单位净值'],
            name='价格', line=dict(color='blue', width=1),hovertemplate='日期: %{x|%Y-%m-%d}<br>净值变化: %{y:.2%}<extra></extra>',
            showlegend=False
        ), row=2, col=1)

    # 3. RSI
    if 'RSI_14' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['净值日期'], y=df['RSI_14'],
            name='RSI', line=dict(color='purple', width=1)
        ), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)

    # 4. 动量
    if 'Momentum_10' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['净值日期'], y=df['Momentum_10'],
            name='10日动量', line=dict(color='orange', width=1)
        ), row=4, col=1)
        fig.add_hline(y=0, line_dash="dash", line_color="black", row=4, col=1)

    # fig.update_layout(
    #     title='基金综合技术分析',
    #     hovermode='x unified',
    #     height=800
    # )
    fig.update_layout(
        title='基金综合技术分析',
        # xaxis_title='日期',
        # yaxis_title='净值',
        hovermode='x unified',  # 统一悬停显示
        # yaxis=dict(
        #     tickformat='.2%',  # 显示为百分比，保留2位小数
        #     # title='净值百分比'
        # ),
        xaxis=dict(
            tickformat='%Y-%m-%d',  # 设置x轴刻度格式
            type='date'
        ),
        legend=dict(
            # orientation="h",  # 水平图例
            # yanchor="bottom", # 锚点在底部
            # y=1.02, # 在图像上方
            # xanchor="center",
            # x=0.5,           # 水平居中
            bgcolor='rgba(255,255,255,0.8)',  # 半透明背景
            bordercolor='lightgray',
            borderwidth=1
        ),
        height=800,
        # annotations=annotations
    )
    # 修正属性名称：spikemode 而不是 spike_mode
    fig.update_xaxes(
        showspikes=True,
        spikecolor='black',
        spikethickness=1,
        spikedash='dot',
        spikemode='across',  # 正确的属性名
        spikesnap='cursor'
    )
    st.plotly_chart(fig, use_container_width=True)


# Streamlit 界面
