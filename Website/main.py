import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import os
import matplotlib
matplotlib.use('TkAgg')  # 在导入pyplot之前设置后端
import matplotlib.pyplot as plt
import re
import pandas as pd
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
# from show_content.show_dashboard import show_dashboard

class FundStockApp:
    def __init__(self):
        self.config_path = 'config.yaml'
        self.setup_page()
        self.authenticator = self.setup_auth()

    def setup_page(self):
        st.set_page_config(
            page_title="基金股票预测系统",
            page_icon="📈",
            layout="wide"
        )

    def setup_auth(self):
        with open(self.config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.load(file, Loader=SafeLoader)

        return stauth.Authenticate(
            self.config['credentials'],
            self.config['cookie']['name'],
            self.config['cookie']['key'],
            self.config['cookie']['expiry_days']
        )

    def has_role(self, role_name):
        """检查当前用户是否拥有指定角色"""
        username = st.session_state.get("username")
        if not username:
            return False

        # 从配置文件中获取用户角色
        user_roles = self.config['credentials']['usernames'].get(username, {}).get('roles', [])
        return role_name in user_roles

    def is_super_admin(self):
        """检查当前用户是否是超级管理员"""
        return self.has_role('admin') or st.session_state.get('username') == 'admin'

    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            st.error(f"保存配置文件失败: {e}")
            return False

    def validate_password(self, password):
        """验证密码强度"""
        if len(password) < 8:
            return False, "密码长度至少8位"

        if not re.search(r'[a-z]', password):
            return False, "密码必须包含至少一个小写字母"

        if not re.search(r'[A-Z]', password):
            return False, "密码必须包含至少一个大写字母"

        if not re.search(r'[@$!%*?&]', password):
            return False, "密码必须包含至少一个特殊字符 (@$!%*?&)"

        return True, "密码强度符合要求"

    def show_dashboard(self):

        df = pd.read_csv(r"F:\PyCharm_Project\FundStock_Prediction_Website\Data\Funds\050026.csv")
        df['净值日期'] = pd.to_datetime(df['净值日期'])

        # # 方法3.1：使用Plotly Express
        # fig = px.line(
        #     df,
        #     x='净值日期',
        #     y='MA_5',
        #     title='基金MA_5指标走势图',
        #     labels={'净值日期': '日期', 'MA_5': 'MA_5指标'}
        # )
        #
        # # 自定义样式
        # fig.update_traces(
        #     line=dict(color='red', width=3, dash='solid'),  # 颜色、宽度、线型
        #     marker=dict(size=4)  # 数据点大小
        # )
        #
        # fig.update_layout(
        #     title_x=0.5,  # 标题居中
        #     title_font_size=20,
        #     xaxis_title='日期',
        #     yaxis_title='MA_5值',
        #     hovermode='x unified'  # 悬停模式
        # )
        #
        # st.plotly_chart(fig, use_container_width=True)

        # 方法3.2：使用Plotly Graph Objects（更精细控制）
        fig2 = go.Figure()

        fig2.add_trace(go.Scatter(
            x=df['净值日期'],
            y=df['MA_5'],
            mode='lines',
            name='MA_5',
            line=dict(color='blue', width=1.5, dash='solid'),
            hovertemplate='日期: %{x}<br>MA_5: %{y:.2f}<extra></extra>'
        ))

        fig2.update_layout(
            title='基金MA_5指标走势图',
            xaxis_title='日期',
            yaxis_title='MA_5指标',
            template='plotly_white',
            hovermode='x unified'
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

        fig2.update_yaxes(
            showspikes=True,
            spikecolor='black',
            spikethickness=1,
            spikedash='dot',
            spikemode='across',  # 正确的属性名
            spikesnap='cursor'
        )

        st.plotly_chart(fig2, use_container_width=True)

        # # 显示用户角色信息
        # if self.is_super_admin():
        #     st.success("🔧 您以超级管理员身份登录")
        # elif self.has_role('editor'):
        #     st.info("✏️ 您以编辑者身份登录")
        # elif self.has_role('viewer'):
        #     st.info("👀 您以查看者身份登录")

    def show_prediction(self):
        st.title("智能预测")
        st.write("这里是智能预测页面")

    def show_stock_analysis(self):
        st.title("股票分析")
        st.write("这里是股票分析页面")

    def show_fund_analysis(self):
        st.title("基金分析")
        st.write("这里是基金分析页面")

    def show_settings(self):
        st.title("系统设置")

        # 显示用户权限信息
        if self.is_super_admin():
            st.success("🔧 超级管理员权限：可以访问所有功能")
        else:
            st.info("👤 普通用户权限")

        # 创建选项卡来组织设置功能
        tab_names = ["密码设置", "个人信息"]

        # 只有超级管理员可以看到用户管理选项卡
        if self.is_super_admin():
            tab_names.append("用户管理")

        tabs = st.tabs(tab_names)

        with tabs[0]:  # 密码设置
            self.show_password_settings()

        with tabs[1]:  # 个人信息
            self.show_personal_info()

        if self.is_super_admin() and len(tabs) > 2:
            with tabs[2]:  # 用户管理
                self.show_user_management()

    def show_password_settings(self):
        """显示密码设置页面"""
        st.header("修改密码")

        # 显示密码要求
        with st.expander("密码要求"):
            st.write("""
            - 至少8位长度
            - 至少包含一个小写字母 (a-z)
            - 至少包含一个大写字母 (A-Z)  
            - 至少包含一个特殊字符 (@$!%*?&)
            """)

        # 方法1：使用内置的reset_password功能
        try:
            if self.authenticator.reset_password(
                    username=st.session_state["username"],
                    location='main'
            ):
                if self.save_config():
                    st.success('密码修改成功并已保存到配置文件')
                else:
                    st.error('密码修改成功但保存配置文件失败')
        except Exception as e:
            error_msg = str(e)
            if "Password must" in error_msg:
                st.error("密码不符合强度要求，请查看上面的密码要求")
            else:
                st.error(f"密码修改错误: {e}")

    def show_personal_info(self):
        """显示和修改个人信息"""
        st.header("个人信息")
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**用户名:** {st.session_state['username']}")
            st.write(f"**姓名:** {st.session_state['name']}")
            st.write(f"**邮箱:** {st.session_state.get('email', '未设置')}")

            # 显示用户角色
            roles = self.config['credentials']['usernames'][st.session_state['username']].get('roles', [])
            if roles:
                st.write(f"**角色:** {', '.join(roles)}")
            else:
                st.write("**角色:** 普通用户")

        with col2:
            # 只有超级管理员可以修改角色
            if self.is_super_admin():
                st.subheader("角色管理")
                current_roles = self.config['credentials']['usernames'][st.session_state['username']].get('roles', [])

                role_options = ['admin', 'editor', 'viewer']
                selected_roles = st.multiselect(
                    "选择角色",
                    options=role_options,
                    default=current_roles
                )

                if st.button("更新角色"):
                    if self.update_user_roles(st.session_state['username'], selected_roles):
                        st.success("角色更新成功")
                    else:
                        st.error("角色更新失败")

            # 更新个人信息功能
            st.subheader("更新信息")
            new_name = st.text_input("新姓名", value=st.session_state['name'], key="new_name")
            new_email = st.text_input("新邮箱", value=st.session_state.get('email', ''), key="new_email")

            if st.button("更新个人信息"):
                if self.update_user_info(st.session_state['username'], new_name, new_email):
                    st.success("个人信息更新成功")
                    # 更新session状态
                    st.session_state['name'] = new_name
                    if new_email:
                        st.session_state['email'] = new_email
                else:
                    st.error("更新失败")

    def update_user_roles(self, username, roles):
        """更新用户角色"""
        try:
            if username in self.config['credentials']['usernames']:
                self.config['credentials']['usernames'][username]['roles'] = roles
                return self.save_config()
            return False
        except Exception as e:
            st.error(f"更新用户角色错误: {e}")
            return False

    def update_user_info(self, username, new_name, new_email):
        """更新用户信息"""
        try:
            if username in self.config['credentials']['usernames']:
                self.config['credentials']['usernames'][username]['name'] = new_name
                if new_email:
                    self.config['credentials']['usernames'][username]['email'] = new_email

                return self.save_config()
            return False
        except Exception as e:
            st.error(f"更新用户信息错误: {e}")
            return False

    def show_user_management(self):
        """用户管理功能（仅超级管理员）"""
        st.header("用户管理")
        st.success("🔧 超级管理员功能")

        # 显示密码要求
        with st.expander("密码要求说明"):
            st.write("""
            新建用户的密码必须满足以下要求：
            - 至少8位长度
            - 至少包含一个小写字母 (a-z)
            - 至少包含一个大写字母 (A-Z)  
            - 至少包含一个特殊字符 (@$!%*?&)
            """)

        # 添加新用户
        st.subheader("添加新用户")
        with st.form("add_user_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_username = st.text_input("用户名", key="new_username")
            with col2:
                new_name = st.text_input("姓名", key="new_user_name")
            with col3:
                new_email = st.text_input("邮箱", key="new_user_email")

            new_password = st.text_input("密码", type="password", key="new_user_pass")
            confirm_password = st.text_input("确认密码", type="password", key="new_user_confirm_pass")

            # 角色选择（只有超级管理员可以设置）
            role_options = ['admin', 'editor', 'viewer']
            selected_roles = st.multiselect("分配角色", options=role_options, default=['viewer'])

            # 实时密码强度检查
            if new_password:
                is_valid, message = self.validate_password(new_password)
                if is_valid:
                    st.success("✓ " + message)
                else:
                    st.error("✗ " + message)

            if st.form_submit_button("添加用户"):
                if self.add_new_user(new_username, new_name, new_email, new_password, confirm_password, selected_roles):
                    st.success("用户添加成功")
                else:
                    st.error("用户添加失败")

        # 用户列表
        st.subheader("用户列表")
        users = self.config['credentials']['usernames']
        for username, user_info in users.items():
            with st.expander(f"{user_info.get('name', '无名')} ({username})"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"邮箱: {user_info.get('email', '未设置')}")
                    roles = user_info.get('roles', [])
                    st.write(f"角色: {', '.join(roles) if roles else '普通用户'}")
                with col2:
                    if username != st.session_state['username']:  # 不能删除自己
                        if st.button(f"删除", key=f"delete_{username}"):
                            if self.delete_user(username):
                                st.success(f"用户 {username} 已删除")
                                st.rerun()

    def add_new_user(self, username, name, email, password, confirm_password, roles=None):
        """添加新用户"""
        if roles is None:
            roles = ['viewer']

        if not username or not name or not password:
            st.error("用户名、姓名和密码不能为空")
            return False

        if password != confirm_password:
            st.error("密码不匹配")
            return False

        # 验证密码强度
        is_valid, message = self.validate_password(password)
        if not is_valid:
            st.error(f"密码强度不足: {message}")
            return False

        if username in self.config['credentials']['usernames']:
            st.error("用户名已存在")
            return False

        try:
            # 哈希密码
            hashed_password = stauth.Hasher([password]).generate()[0]

            # 添加新用户
            self.config['credentials']['usernames'][username] = {
                'email': email if email else '',
                'name': name,
                'password': hashed_password,
                'roles': roles
            }

            return self.save_config()
        except Exception as e:
            st.error(f"添加用户错误: {e}")
            return False

    def delete_user(self, username):
        """删除用户"""
        if username == st.session_state['username']:
            st.error("不能删除当前登录的用户")
            return False

        try:
            del self.config['credentials']['usernames'][username]
            return self.save_config()
        except Exception as e:
            st.error(f"删除用户错误: {e}")
            return False

    def run(self):
        # 登录
        try:
            self.authenticator.login(location='main')
        except Exception as e:
            st.error(f"登录错误: {e}")

        # 状态处理
        if st.session_state.get("authentication_status"):
            self.show_main_app()
        elif st.session_state.get("authentication_status") is False:
            st.error('用户名/密码不正确')
        elif st.session_state.get("authentication_status") is None:
            st.warning('请输入用户名和密码')

    def show_main_app(self):
        with st.sidebar:
            st.title(f"欢迎, {st.session_state['name']}!")

            # 显示用户角色
            if self.is_super_admin():
                st.success("🔧 超级管理员")
            elif self.has_role('editor'):
                st.info("✏️ 编辑者")
            elif self.has_role('viewer'):
                st.info("👀 查看者")

            st.divider()

            self.authenticator.logout('退出登录', location='sidebar')
            st.divider()

            # 基本菜单项
            menu_items = ["📊 数据看板", "🤖 智能预测", "📈 股票分析", "💰 基金分析", "⚙️ 系统设置"]

            page = st.radio("导航菜单", menu_items)

        if page == "📊 数据看板":
            self.show_dashboard()
        elif page == "🤖 智能预测":
            self.show_prediction()
        elif page == "📈 股票分析":
            self.show_stock_analysis()
        elif page == "💰 基金分析":
            self.show_fund_analysis()
        elif page == "⚙️ 系统设置":
            self.show_settings()


if __name__ == "__main__":
    app = FundStockApp()
    app.run()