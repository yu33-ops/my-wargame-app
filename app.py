import streamlit as st
import json
import requests
import time
import re

# ========== 核心配置：填入你的阿里云百炼 API_KEY ==========
API_KEY = "sk-ws-H.EYYRXHM.8hPe.MEUCIF6taU1uYI2wo2DJTG3DTmsA8cdnH38iLmu6x_etID0JAiEAsoxe2dxqlRAPW4p_3BFEoZq7XSeY4YGBy4ffDN-tjX0"

def load_db():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"红方阵营": {}, "蓝方阵营": {}}

def call_wargame_engine(red_summary, blue_summary, keywords, database_info, template):
    """
    大模型战术推理引擎：严格控制大模型只输出战损数量，不让它算总价
    """
    prompt = template.format(
        database_info=json.dumps(database_info, ensure_ascii=False, indent=2),
        red_input=red_summary,
        blue_input=blue_summary,
        keywords=keywords
    )

    url = "https://aliyuncs.com"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen-max",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3  # 降低随机性，让大模型严格遵守格式
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=20)
        if response.status_code == 200:
            return response.json()["choices"]["message"]["content"]
    except Exception:
        pass

    # 离线兜底返回格式（确保云端报错时也有标准格式供Python计算）
    result_dict = {
        "战场想定过程": f"【离线引擎演示】交战地域爆发惨烈冲突，双方围绕 {keywords} 展开争夺，多型装备出现实质性对冲损耗。",
        "推演结果": {
            "红方统计": {"99A式主战坦克_损失数量": 2, "直-10武装直升机_损失数量": 1, "红旗-9B防空导弹_损失数量": 0, "ASN-301反辐射 drones_损失数量": 3},
            "蓝方统计": {"M1A2主战坦克_损失数量": 3, "AH-64D阿帕奇直升机_损失数量": 1, "爱国者-3防空导弹_损失数量": 0, "MQ-9死神无人机_损失数量": 2},
            "战术胜负判定": "双方互有消耗，战局陷入拉锯僵持阶段。"
        }
    }
    return json.dumps(result_dict, ensure_ascii=False)

# ========== Streamlit 网页展示前端 ==========
st.set_page_config(page_title="高级兵棋推演想定智能生成系统", layout="wide")
st.title("🎖️ 高级兵棋推演想定智能生成系统 (Python算损完全体)")

db = load_db()
col_left, col_right = st.columns([1, 1.2]) # 微调左右比例

with col_left:
    st.header("📥 战场参数配置")
    keywords = st.text_area("战场环境与行动关键词", "山地遭遇战、夜间突袭、暴雨环境、多维防空压制")
    
    # ---- 红方装备配置 ----
    st.subheader("🔴 红方兵力编成")
    red_options = list(db["红方阵营"].keys())
    selected_red = st.multiselect("请选择红方出动装备", red_options, default=red_options[:2])
    
    red_inventory = {}
    for req_eq in selected_red:
        eq_data = db["红方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=10, key=f"red_{req_eq}")
        red_inventory[req_eq] = {"名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"]}

    # ---- 蓝方装备配置 ----
    st.subheader("🔵 蓝方兵力编成")
    blue_options = list(db["蓝方阵营"].keys())
    selected_blue = st.multiselect("请选择蓝方出动装备", blue_options, default=blue_options[:2])
    
    blue_inventory = {}
    for req_eq in selected_blue:
        eq_data = db["蓝方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=10, key=f"blue_{req_eq}")
        blue_inventory[req_eq] = {"名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"]}

    run_button = st.button("🚀 开始大模型自动化推演", use_container_width=True)

with col_right:
    st.header("📄 想定推演生成报告")
    
    if run_button:
        # 1. 组装输入描述
        red_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['名称']}" for k, v in red_inventory.items()])
        blue_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['名称']}" for k, v in blue_inventory.items()])
        
        # 2. 强制要求大模型返回各个装备具体损失数量的“硬核指令模板”
        template = """你是一位精通军事推演的AI。请根据已知数据库和输入的红蓝双方初始数量、战场关键词，推演战争过程。
【已知装备数据库】：{database_info}
【初始红方】：{red_input}
【初始蓝方】：{blue_input}
【交战环境】：{keywords}

【严格任务要求】：
请根据关键词和性能克制关系，合理设定红蓝双方各个装备的【损失数量】（损失数量绝对不能超过初始数量）。
必须严格按照以下 JSON 格式输出，不要带有任何多余的解释文本：
{{
  "战场想定过程": "写一段300字左右的逼真交战过程描述",
  "推演结果": {{
    "红方统计": {{
      "99A式主战坦克_损失数量": 填写数字,
      "直-10武装直升机_损失数量": 填写数字,
      "红旗-9B防空导弹_损失数量": 填写数字,
      "ASN-301反辐射 drones_损失数量": 填写数字
    }},
    "蓝方统计": {{
      "M1A2主战坦克_损失数量": 填写数字,
      "AH-64D阿帕奇直升机_损失数量": 填写数字,
      "爱国者-3防空导弹_损失数量": 填写数字,
      "MQ-9死神无人机_损失数量": 填写数字
    }},
    "战术胜负判定": "战术胜负判定及原因分析"
  }}
}}"""

        with st.spinner("大模型正在进行战术博弈推理..."):
            raw_result = call_wargame_engine(red_summary, blue_summary, keywords, db, template)
            
            try:
                clean_result = raw_result.strip().strip("```json").strip("```")
                result_json = json.loads(clean_result)
                
                st.success("✨ 想定数据推演及算法解析完成！")
                
                # 展示过程
                st.subheader("🎬 1. 战场动态过程描述")
                st.info(result_json.get("战场想定过程", "未生成过程"))
                
                # ==== ⚙️ 核心算法层：用 Python 代码根据大模型决定的损耗数量，精准计算总价格 ====
                stats = result_json.get("推演结果", {})
                red_llm_losses = stats.get("红方统计", {})
                blue_llm_losses = stats.get("蓝方统计", {})
                
                # 计算红方战损与价格
                red_loss_text_list = []
                red_total_cost = 0
                for k, v in red_inventory.items():
                    loss_key = f"{v['名称']}_损失数量"
                    # 让大模型给出的损失数量跟用户输入的初始数量取最小值，防止大模型“作弊”让损失大于初始
                    actual_loss = min(int(red_llm_losses.get(loss_key, 0)), v["初始数量"])
                    if actual_loss > 0:
                        red_loss_text_list.append(f"{v['名称']} 损失 {actual_loss} 辆/架/套")
                        red_total_cost += actual_loss * v["单价_万元"]
                
                # 计算蓝方战损与价格
                blue_loss_text_list = []
                blue_total_cost = 0
                for k, v in blue_inventory.items():
                    loss_key = f"{v['名称']}_损失数量"
                    actual_loss = min(int(blue_llm_losses.get(loss_key, 0)), v["初始数量"])
                    if actual_loss > 0:
                        blue_loss_text_list.append(f"{v['名称']} 损失 {actual_loss} 辆/架/套")
                        blue_total_cost += actual_loss * v["单价_万元"]

                # ======================================================================
                
                # 3. 漂亮地渲染计算后的真实结果
                st.subheader("📊 2. 精准算法战损统计")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### 🔴 红方战损报告")
                    if red_loss_text_list:
                        st.error("\n".join([f"- {item}" for item in red_loss_text_list]))
                    else:
                        st.success("- 无明显装备损耗")
                    # 汇率/金额动态展示
                    st.metric(label="红方精确经济损失", value=f"{red_total_cost} 万元")
                        
                with c2:
                    st.markdown("### 🔵 蓝方战损报告")
                    if blue_loss_text_list:
                        st.error("\n".join([f"- {item}" for item in blue_loss_text_list]))
                    else:
                        st.success("- 无明显装备损耗")
                    st.metric(label="蓝方精确经济损失", value=f"{blue_total_cost} 万元")
                
                st.subheader("🏆 3. 总体战术胜负判定")
                st.warning(stats.get("战术胜负判定", "未生成判定"))
                
            except Exception as e:
                st.error(f"解析想定数据时出错，大模型原始输出如下：")
                st.code(raw_result)
    else:
        st.write("👈 请在左侧动态调整兵力数量，点击按钮体验精准战损计算。")

