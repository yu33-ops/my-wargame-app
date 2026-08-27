import streamlit as st
import json
from main import generate_scenario_data

# 设置软件网页标题
st.title("🎖️ 作战仿真想定自动化生成系统 (论文青春版)")
st.write("根据陆军兵种大学大语言模型想定生成论文架构开发")

# 1. 软件左侧输入区
st.sidebar.header("📥 推演参数输入")
red_input = st.sidebar.text_input("红方兵力编成", "10辆 99A式主战坦克, 2架 直-10武装直升机")
blue_input = st.sidebar.text_input("蓝方兵力编成", "8辆 M1A2主战坦克, 4架 AH-64阿帕奇武装直升机")
keywords = st.sidebar.text_area("战场行动与环境关键词", "山地遭遇战、夜间突袭、暴雨环境、蓝方低空伏击")

# 2. 软件核心运行按钮
if st.sidebar.button("🚀 开始自动化推演生成"):
    with st.spinner("大模型正在根据论文思维链进行逻辑推理，请稍候..."):
        try:
            # 调用后台大模型
            raw_result = generate_scenario_data(red_input, blue_input, keywords)
            
            # 将大模型返回的JSON文本，解析为网页可以显示的卡片
            result_json = json.loads(raw_text=raw_result.strip().strip("```json").strip("```"))
            
            st.success("✨ 想定推演生成成功！")
            
            # 3. 展现结果：战场过程描述
            st.header("1. 🎬 战场想定过程描述")
            st.info(result_json["battle_process"])
            
            # 4. 展现结果：数据损耗
            st.header("2. 📊 损耗结果统计")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🔴 红方统计")
                st.write(f"**装备战损：** {result_json['results']['red_side']['losses']}")
                st.write(f"**经济损失：** {result_json['results']['red_side']['economic_loss_million_rmb']} 百万元")
            with col2:
                st.subheader("🔵 蓝方统计")
                st.write(f"**装备战损：** {result_json['results']['blue_side']['losses']}")
                st.write(f"**经济损失：** {result_json['results']['blue_side']['economic_loss_million_rmb']} 百万元")
                
            # 5. 展现结果：胜负判定
            st.header("3. 🏆 战术胜负判定")
            st.warning(result_json["results"]["victory_determination"])
            
        except Exception as e:
            st.error(f"解析大模型返回数据时出错，可能是API_KEY有误或大模型未返回标准JSON。错误信息: {e}")
            if 'raw_result' in locals():
                st.text("大模型原始返回文本如下：")
                st.code(raw_result)
