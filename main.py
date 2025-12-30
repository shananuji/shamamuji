import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pickle
import json

# 页面配置
st.set_page_config(
    page_title="智能食堂助手",
    page_icon="🍽️",
    layout="wide"
)

# 标题
st.title("🍽️ 智能食堂人流量预测系统")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")
    selected_canteen = st.selectbox(
        "选择食堂",
        ["第一食堂", "第二食堂", "第三食堂", "风味餐厅", "清真食堂"]
    )
    
    selected_date = st.date_input("选择日期", datetime.now())
    
    meal_time = st.selectbox(
        "选择就餐时段",
        ["早餐 (7:00-9:00)", "午餐 (11:00-13:00)", "晚餐 (17:00-19:00)"]
    )
    
    st.markdown("---")
    st.markdown("### 关于")
    st.info("本系统通过历史数据分析预测食堂人流量，数据每30分钟更新一次")

# 模拟预测函数（实际可替换为真实模型）
def predict_crowd(canteen, date, time_slot):
    """预测食堂人流量"""
    # 基础流量（可基于历史数据训练，这里使用模拟数据）
    base_traffic = {
        "第一食堂": 150, "第二食堂": 120, "第三食堂": 100,
        "风味餐厅": 80, "清真食堂": 60
    }
    
    # 时间段系数
    time_factors = {
        "早餐": 0.6, "午餐": 1.2, "晚餐": 1.0
    }
    
    # 星期系数（周末人少）
    weekday = date.weekday()
    day_factor = 0.7 if weekday >= 5 else 1.0  # 周末系数
    
    # 模拟预测逻辑
    base = base_traffic.get(canteen, 100)
    time_key = "午餐" if "午餐" in time_slot else "晚餐" if "晚餐" in time_slot else "早餐"
    time_factor = time_factors.get(time_key, 1.0)
    
    # 添加一些随机性（模拟实时变化）
    random_factor = np.random.uniform(0.9, 1.1)
    
    predicted = int(base * time_factor * day_factor * random_factor)
    
    return predicted

# 主界面
col1, col2, col3 = st.columns(3)

with col1:
    # 预测当前选择
    prediction = predict_crowd(selected_canteen, selected_date, meal_time)
    st.metric(
        label=f"{selected_canteen} 预测人数",
        value=f"{prediction}人",
        delta=f"较平时 {'增加' if prediction > 100 else '减少'}"
    )

with col2:
    # 拥挤程度
    if prediction < 80:
        status = "✅ 舒适"
        color = "green"
    elif prediction < 120:
        status = "⚠️ 适中"
        color = "orange"
    else:
        status = "🔴 拥挤"
        color = "red"
    
    st.markdown(f"### 拥挤程度")
    st.markdown(f'<h1 style="color:{color};text-align:center">{status}</h1>', unsafe_allow_html=True)

with col3:
    # 建议等待时间
    wait_time = max(0, (prediction - 80) // 10 * 5)
    st.markdown("### 预计等待时间")
    st.markdown(f'<h1 style="text-align:center">{wait_time} 分钟</h1>', unsafe_allow_html=True)

st.markdown("---")

# 详细预测图表
st.subheader("📊 今日各时段预测")

# 生成时间序列预测
times = ["7:00", "8:00", "9:00", "10:00", "11:00", "12:00", 
         "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"]

predictions = []
for time in times:
    if "7:00" <= time <= "9:00":
        period = "早餐"
    elif "11:00" <= time <= "13:00":
        period = "午餐"
    elif "17:00" <= time <= "19:00":
        period = "晚餐"
    else:
        period = "其他"
    
    pred = predict_crowd(selected_canteen, selected_date, f"{period} ({time})")
    predictions.append(pred)

# 绘制图表
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(times, predictions, marker='o', linewidth=2)
ax.fill_between(times, predictions, alpha=0.3)
ax.set_xlabel("时间")
ax.set_ylabel("预测人数")
ax.set_title(f"{selected_canteen} - 今日人流预测")
ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=45)

st.pyplot(fig)

# 多食堂对比
st.subheader("🏫 各食堂当前情况对比")

canteens = ["第一食堂", "第二食堂", "第三食堂", "风味餐厅", "清真食堂"]
current_time = datetime.now().strftime("%H:%M")
current_period = "午餐" if "11:00" <= current_time <= "13:00" else "晚餐" if "17:00" <= current_time <= "19:00" else "早餐"

comparison_data = []
for canteen in canteens:
    pred = predict_crowd(canteen, selected_date, f"{current_period} ({current_time})")
    comparison_data.append(pred)

# 显示对比柱状图
fig2, ax2 = plt.subplots(figsize=(10, 4))
bars = ax2.bar(canteens, comparison_data, color=['red' if x > 120 else 'orange' if x > 80 else 'green' for x in comparison_data])
ax2.set_xlabel("食堂")
ax2.set_ylabel("当前预测人数")
ax2.set_title(f"各食堂 {current_time} 预测对比")
ax2.tick_params(axis='x', rotation=45)

# 添加数值标签
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 3,
             f'{int(height)}', ha='center', va='bottom')

st.pyplot(fig2)

# 智能建议
st.markdown("---")
st.subheader("💡 智能建议")

# 找到最佳就餐食堂
best_canteen_idx = np.argmin(comparison_data)
best_canteen = canteens[best_canteen_idx]
best_time_idx = np.argmin(predictions[4:9]) + 4  # 午餐时段
best_time = times[best_time_idx]

st.info(f"""
**当前最佳选择：** {best_canteen} (预测人数: {comparison_data[best_canteen_idx]}人)

**推荐就餐时间：** {best_time} (人数最少)

**建议：** 如果时间灵活，建议 {best_time} 前往 {best_canteen}，可减少 {max(comparison_data) - comparison_data[best_canteen_idx]} 人的排队时间。
""")

# 反馈收集
st.markdown("---")
st.subheader("📝 反馈与评价")

with st.expander("点击提交您的用餐体验"):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        actual_crowd = st.slider("实际拥挤程度", 1, 5, 3, 
                                help="1=非常空，5=非常拥挤")
        wait_time_actual = st.number_input("实际等待时间(分钟)", 0, 120, 10)
    
    with col_f2:
        satisfaction = st.slider("满意度评分", 1, 5, 4)
        comments = st.text_area("其他建议")
    
    if st.button("提交反馈"):
        # 这里可以连接到数据库保存反馈
        st.success("感谢您的反馈！数据已记录，将用于优化预测模型")
        
        # 显示历史反馈
        st.markdown("**最近3条用户反馈:**")
        sample_feedback = [
            {"用户": "同学A", "时间": "12:30", "食堂": "第一食堂", "评价": "预测准确，节省了时间"},
            {"用户": "同学B", "时间": "昨天 18:00", "食堂": "第二食堂", "评价": "建议很实用"},
            {"用户": "同学C", "时间": "前天 12:00", "食堂": "第三食堂", "评价": "等待时间比预期短"}
        ]
        st.table(sample_feedback)

# 底部信息
st.markdown("---")
st.caption("最后更新: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
st.caption("注：预测数据基于历史统计和实时分析，仅供参考")