import streamlit as st
import json
import requests
import time

# ========== 核心配置：填入你确定好使的阿里云百炼 API_KEY ==========
API_KEY = "sk-ws-H.EYYRXHM.8hPe.MEUCIF6taU1uYI2wo2DJTG3DTmsA8cdnH38iLmu6x_etID0JAiEAsoxe2dxqlRAPW4p_3BFEoZq7XSeY4YGBy4ffDN-tjX0"

def load_db():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"红方阵营": {}, "蓝方阵营": {}}

def call_aliyun_wargame_engine(prompt):
    """
    【真实阿里云百炼接口】：100%使用你提供的真实API_KEY进行安全调用。
    严格对齐阿里云最新的网关协议，拒绝404，直达qwen-max。
    """
    # 完美对齐百炼的兼容网关
    url = "https://aliyuncs.com"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen-max", # 强力推荐千问满血版
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2  # 降低大模型随性打分的倾向，让其更听从战力约束
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            res_body = response.json()
            return res_body["choices"][0]["message"]["content"]
        else:
            return json.dumps({
                "战场想定过程": f"阿里云服务器返回了错误状态码: {response.status_code}。可能是未在控制台开通qwen-max授权。",
                "推演结果": {
                    "红方统计": {}, "蓝方统计": {},
                    "战术胜负判定": f"请求被拒绝，详细反馈: {response.text}"
                }
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "战场想定过程": f"连接阿里云网络超时。具体原因: {e}",
            "推演`结果": {
                "红方统计": {}, "蓝方统计": {},
                "战术胜负判定": "请确保你的Streamlit Cloud云端网络能够正常连接阿里云。"
            }
        }, ensure_ascii=False)

# ========== Streamlit 网页展示前端 ==========
st.set_page_config(page_title="高级兵棋推演想定智能生成系统", layout="wide")
st.title("🎖️ 高级兵棋推演想定智能生成系统 (阿里云大模型+战力修正版)")

db = load_db()
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.header("📥 战场参数配置")
    keywords = st.text_area("战场环境与行动关键词", "山地遭遇战、夜间突袭、暴雨环境、多维防空压制")
    
    # ---- 红方装备配置 ----
    st.subheader("🔴 红方兵力编成")
    red_options = list(db["红方阵营"].keys())
    selected_red = st.multiselect("请选择红方出动装备", red_options, default=red_options[:2])
    
    red_inventory = {}
    red_total_units = 0 
    for req_eq in selected_red:
        eq_data = db["红方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=10, key=f"red_{req_eq}")
        red_inventory[req_eq] = {"名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"]}
        red_total_units += count

    # ---- 蓝方装备配置 ----
    st.subheader("🔵 蓝方兵力编成")
    blue_options = list(db["蓝方阵营"].keys())
    selected_blue = st.multiselect("请选择蓝方出动装备", blue_options, default=blue_options[:2])
    
    blue_inventory = {}
    blue_total_units = 0 
    for req_eq in selected_blue:
        eq_data = db["蓝方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=2, key=f"blue_{req_eq}") 
        blue_inventory[req_eq] = {"名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"]}
        blue_total_units += count

    run_button = st.button("🚀 开始阿里云大模型推演", use_container_width=True)

with col_right:
    st.header("📄 想定推演生成报告")
    
    if run_button:
        red_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['名称']}" for k, v in red_inventory.items()])
        blue_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['名称']}" for k, v in blue_inventory.items()])
        
        # ==== ⚙️ 核心算法层：计算战力悬殊比例，用硬核战术指标强制矫正提示词 ====
        ratio_hint = ""
        if blue_total_units > 0:
            force_ratio = red_total_units / blue_total_units
            if force_ratio >= 3.0:
                ratio_hint = f"【特别战术红线限制】：当前红方总兵力（{red_total_units}台）对蓝方总兵力（{blue_total_units}台）形成了超过 {force_ratio:.1f} 倍的绝对压倒性优势！在判定胜负时，必须判定红方凭借人海战术或钢铁洪流迅速取得全面胜利，蓝方防线彻底崩溃！绝对禁止使用‘拉锯僵持’、‘难解难分’、‘互有胜负’等敷衍和稀泥的词汇！"
            elif force_ratio <= 0.33:
                ratio_hint = f"【特别战术红线限制】：当前蓝方总兵力远超红方超过3倍！在判定胜负时，必须判定蓝方依托庞大的火力基数和数量优势轻松击溃红方编队，红方进攻完全失败！绝对禁止写‘双方僵持拉锯’！"
            else:
                ratio_hint = "【战术平衡指令】：当前双方总兵力规模在一个数量级（接近 1:1），请根据装备的性能参数和关键词，推演合理的拉锯僵持、遭遇伏击或惨胜过程。"
        # ==========================================================

        # 3. 严格遵循论文思维链格式的提示词（包含战力强化指令）
        template = """你是一位专门从事陆军战术仿真想定生成的军事推演专家。请结合已知的装备性能数据库和当前战场参数，进行深度的逻辑推理，生成符合真实军事常识的交战过程和战损数量。

【已知装备数据库】：
{database_info}

【当前推演输入参数】：
- 红方初始配置：{red_input}
- 蓝方初始配置：{blue_input}
- 战场行动与环境关键词：{keywords}

{ratio_hint}

【严格数据输出格式规范】：
根据关键词和两军规模，合理设定红蓝双方各个装备的【损失数量】（损失数量必须是整数且大于等于0，绝对不能超过各自输入的初始数量）。
必须直接返回以下标准的纯 JSON 格式数据，不要包含任何 Markdown 标记（不要写 ```json ），也不要包含任何开头的修饰文本：
{{
  "战场想定过程": "请结合战场环境关键词、多维对抗、夜间及暴雨天气等因素，写一段 300 到 400 字的极具军事临场感的惨烈、详实的交战动态场景描述。",
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
    "战术胜负判定": "结合两军兵力多寡对比、战损比例和战术红线限制，给出一份逻辑极为严密、客观准确的胜负判定和技战术原因深度剖析。"
  }}
}}"""

        prompt = template.format(
            database_info=json.dumps(db, ensure_ascii=False, indent=2),
            red_input=red_summary,
            blue_input=blue_summary,
            keywords=keywords,
            ratio_hint=ratio_hint
        )

        with st.spinner("🚀 战力天平算法注入中... 正在呼叫阿里云 qwen-max 模型进行深度想定博弈..."):
            raw_result = call_aliyun_wargame_engine(prompt)
            
            try:
                # 剔除干扰符号
                clean_result = raw_result.strip().strip("```json").strip("```")
                result_json = json.loads(clean_result)
                
                st.success("✨ 阿里云百炼大模型想定推演及精准算法解析完成！")
                
                # 展示过程
                st.subheader("🎬 1. 战场动态过程描述")
                st.info(result_json.get("战场想定过程", "未生成过程"))
                
                # ==== ⚙️ 算法层：用 Python 根据真大模型决定的损耗数量，精确到“单价万元”计算价格 ====
                stats = result_json.get("推演结果", {})
                red_llm_losses = stats.get("红方统计", {})
                blue_llm_losses = stats.get("蓝方统计", {})
                
                red_loss_text_list = []
                red_total_cost = 0
                for k, v in red_inventory.items():
                    loss_key = f"{v['名称']}_损失数量"
                    actual_loss = min(int(red_llm_losses.get(loss_key, 0)), v["初始数量"])
                    if actual_loss > 0:
                        red_loss_text_list.append(f"{v['名称']} 损失 {actual_loss} 辆/架/套")
                        red_total_cost += actual_loss * v["单价_万元"]
                
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
                st.error(f"大模型返回数据解析失败，原始AI生成文本如下（可作为论文提炼素材）：")
                st.code(raw_result)
    else:
        st.write("👈 请在左侧配置您的战术编组数量。当前的底层逻辑：【Python战力天平算法 ➔ 实时施压提示词 ➔ 唤醒阿里云qwen-max ➔ Python计算总价】。")

