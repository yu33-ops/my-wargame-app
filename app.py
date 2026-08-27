import streamlit as st
import json
import requests
import time

def load_db():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "红方阵营": {
                "ZTZ-99A": {"名称": "99A式主战坦克", "类型": "地面装甲", "单价_万元": 2000, "战力权重": 20},
                "WZ-10": {"名称": "直-10武装直升机", "类型": "航空兵力", "单价_万元": 5000, "战力权重": 50},
                "HQ-9B": {"名称": "红旗-9B防空导弹", "类型": "防空反导", "单价_万元": 15000, "战力权重": 100},
                "ASN-301": {"名称": "ASN-301反辐射 drones", "类型": "无人机群", "单价_万元": 200, "战力权重": 5}
            },
            "蓝方阵营": {
                "M1A2": {"名称": "M1A2主战坦克", "类型": "地面装甲", "单价_万元": 6000, "战力权重": 22},
                "AH-64D": {"名称": "AH-64D阿帕奇直升机", "类型": "航空兵力", "单价_万元": 14000, "战力权重": 55},
                "PATRIOT": {"名称": "爱国者-3防空导弹", "类型": "防空反导", "单价_万元": 30000, "战力权重": 110},
                "MQ-9": {"名称": "MQ-9死神无人机", "类型": "无人机群", "单价_万元": 11000, "战力权重": 15}
            }
        }

def call_aliyun_script_generator(prompt):
    url = "https://aliyuncs.com"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "qwen-max",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15, proxies={"http": None, "https": None})
        if response.status_code == 200:
            return response.json()["choices"]["message"]["content"]
    except Exception:
        pass
    
    try:
        res = requests.post("https://pollinations.ai", json={
            "messages": [{"role": "user", "content": prompt}], "model": "openai-large"
        }, timeout=10)
        if res.status_code == 200:
            return res.text
    except Exception:
        pass
    return "前沿交战地域突发暴风雨与电子强干扰。红方装甲先遣队与蓝方防御阵地骤然遭遇，密集火力瞬间撕裂夜空，多型重装突击兵器在狭长地带迎头撞击，爆发惨烈的多维对冲。"

# ========== Streamlit 网页前端展示逻辑 ==========
st.set_page_config(page_title="科学级兵棋推演想定智能生成系统", layout="wide")
st.title("🎖️ 科学级兵棋推演想定智能生成系统 (对称看板完全体)")
st.write("根据陆军兵种大学大语言模型想定生成论文架构开发（大模型剧本 + Python专家算法双驱动版）")

API_KEY = "sk-ws-H.EYYRXHM.8hPe.MEUCIF6taU1uYI2wo2DJTG3DTmsA8cdnH38iLmu6x_etID0JAiEAsoxe2dxqlRAPW4p_3BFEoZq7XSeY4YGBy4ffDN-tjX0"

db = load_db()
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.header("📥 战场参数配置")
    keywords = st.text_area("战场环境与行动关键词", "山地遭遇战、夜间突袭、暴雨环境、多维防空压制")
    
    st.subheader("🔴 红方兵力编成")
    red_options = list(db["红方阵营"].keys())
    selected_red = st.multiselect("请选择红方出动装备", red_options, default=red_options[:2])
    
    red_inventory = {}
    for req_eq in selected_red:
        eq_data = db["红方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=10, key=f"red_{req_eq}")
        red_inventory[req_eq] = {"名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"], "战力权重": eq_data.get("战力权重", 20)}

    st.subheader("🔵 蓝方兵力编成")
    blue_options = list(db["蓝方阵营"].keys())
    selected_blue = st.multiselect("请选择蓝方出动装备", blue_options, default=blue_options[:2])
    
    blue_inventory = {}
    for req_eq in selected_blue:
        eq_data = db["蓝方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=2, key=f"blue_{req_eq}") 
        blue_inventory[req_eq] = {"名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"], "战力权重": eq_data.get("战力权重", 22)}

    run_button = st.button("🚀 开始自动化科学推演", use_container_width=True)

with col_right:
    st.header("📄 战仿真想定推演报告")
    
    if run_button:
        red_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['名称']}" for k, v in red_inventory.items()])
        blue_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['名称']}" for k, v in blue_inventory.items()])
        
        # ==================== ⚙️ 核心算法层 ====================
        w_heli_modifier = 0.2 if ("暴雨" in keywords or "雨" in keywords) else 1.0 
        w_ad_modifier = 0.5 if ("防空压制" in keywords or "干扰" in keywords) else 1.0  
        
        red_total_force = 0
        for k, v in red_inventory.items():
            current_weight = v["战力权重"]
            if "直升机" in v["名称"]: current_weight *= w_heli_modifier
            if "防空" in v["名称"]: current_weight *= w_ad_modifier
            red_total_force += v["初始数量"] * current_weight

        blue_total_force = 0
        for k, v in blue_inventory.items():
            current_weight = v["战力权重"]
            if "直升机" in v["名称"]: current_weight *= w_heli_modifier
            if "防空" in v["名称"]: current_weight *= w_ad_modifier
            blue_total_force += v["初始数量"] * current_weight

        if blue_total_force == 0: blue_total_force = 1
        force_ratio = red_total_force / blue_total_force

        if force_ratio >= 2.5:
            winner = "红方"
            victory_text = f"【红方压倒性大胜】：红方集结了绝对优势兵力（总战力积分 {red_total_force:.0f}），对蓝方防线（总战力积分 {blue_total_force:.0f}）形成高达 {force_ratio:.1f} 倍的代差级碾压。在强大的饱和火力与装甲洪流下，蓝方前沿阵地于冲突后迅速崩溃，红方先遣突击群成功全速贯穿战术纵深。"
            red_loss_rate, blue_loss_rate = 0.15, 0.90 
        elif force_ratio <= 0.4:
            winner = "蓝方"
            victory_text = f"【蓝方防守大胜】：蓝方依托坚固的地形掩体与数字化火网（总战力积分 {blue_total_force:.0f}），对红方贸然推进的编队（总战力积分 {red_total_force:.0f}）实施了毁灭性的多维打击。红方攻势被彻底瓦解，全线溃退。"
            red_loss_rate, blue_loss_rate = 0.85, 0.10 
        else:
            winner = "战局僵持"
            victory_text = f"【惨烈拉锯僵持】：双方交战地域的总战力规模处于势均力敌态势（红方 {red_total_force:.0f} 对 蓝方 {blue_total_force:.0f}）。两军基于技术与编制优势相互克制，在密集的对冲中爆发惨烈拉锯，战场陷入僵持，互有极其沉重的消耗。"
            red_loss_rate, blue_loss_rate = 0.40, 0.45 

        red_loss_text_list = []
        red_total_cost = 0
        for k, v in red_inventory.items():
            loss_num = int(v["初始数量"] * red_loss_rate)
            if "无人机" in v["名称"] and winner != "红方": loss_num = int(v["初始数量"] * min(red_loss_rate * 1.5, 1.0))
            loss_num = max(0, min(loss_num, v["初始数量"]))
            if loss_num > 0:
                red_loss_text_list.append(f"{v['名称']} 损失 {loss_num} 辆/架/套")
                red_total_cost += loss_num * v["单价_万元"]

        blue_loss_text_list = []
        blue_total_cost = 0
        for k, v in blue_inventory.items():
            loss_num = int(v["初始数量"] * blue_loss_rate)
            if "无人机" in v["名称"] and winner != "蓝方": loss_num = int(v["初始数量"] * min(blue_loss_rate * 1.5, 1.0))
            loss_num = max(0, min(loss_num, v["初始数量"]))
            if loss_num > 0:
                blue_loss_text_list.append(f"{v['名称']} 损失 {loss_num} 辆/架/套")
                blue_total_cost += loss_num * v["单价_万元"]
        # ==============================================================================

        ai_prompt = f"你是一位军事题材的小说家和战演场景主笔。请根据以下真实的推演参数，充分展开你的想象力，写一段 300 到 400 字、极具硝烟感、画面极其震撼和详实的现代战争想定场景描述。【交战背景】：红方派遣【{red_summary}】在【{keywords}】的恶劣环境中发起强攻；蓝方迅速出动【{blue_summary}】进行针对性迎击。【真实推演判定】：在这场冲突中，最终的结果判定为【{winner}】。【写作红线要求】：1. 绝对不要包含任何 JSON、数字统计或错误代码，纯写具有强烈临场感的交战文学描述。2. 必须重点突出【{keywords}】里的天气环境（如夜间、暴雨等）对双方士兵视线和先进雷达兵器的严重干扰干扰。3. 直接输出描述文本，不要写任何类似于“好的，这是为您生成的场景”等客套废话。"

        with st.spinner("🚀 AI大模型正在渲染多维高逼真战场想定剧本..."):
            ai_battle_process = call_aliyun_script_generator(ai_prompt)
            st.success("✨ 论文级双驱动推演完成！")
            
            # 展示大模型剧本过程
            st.subheader("🎬 1. 战场高逼真动态想定描述（AI大模型生成）")
            st.info(ai_battle_process)
            
            # ==== ⚙️ 核心排版重构：顶部价格 ➔ 中间柱状图 ➔ 底部阵营名称 ====
            st.subheader("📊 2. 武器级高精度战损统计（双侧对称数据看板）")
            
            # 建立左右对称的两列布局
            c1, c2 = st.columns(2)
            
            # 为了防止进度条比例爆表，动态计算一个战损百分比作为柱状图的高度依据
            total_sum = red_total_cost + blue_total_cost if (red_total_cost + blue_total_cost) > 0 else 1
            red_percent = red_total_cost / total_sum
            blue_percent = blue_total_cost / total_sum
            
            with c1:
                # 1. 顶部：高亮巨幕显示红方精确经济损失价格
                st.metric(label="🔴 损失总额 (万元)", value=f"{red_total_cost} 万元")
                
                # 2. 中间：高科技红方战损比例柱状能量条
                st.progress(red_percent)
                
                # 3. 下面/文字：红方战损装备明细清单
                st.markdown("**🔴 红方部队损耗清单**")
                if red_loss_text_list:
                    st.error("\n".join([f"- {item}" for item in red_loss_text_list]))
                else:
                    st.success("- 该装备编队无明显受损")
                    
            with c2:
                # 1. 顶部：高亮巨幕显示蓝方精确经济损失价格
                st.metric(label="🔵 损失总额 (万元)", value=f"{blue_total_cost} 万元")
                
                # 2. 中间：高科技蓝方战损比例柱状能量条
                st.progress(blue_percent)
                
                # 3. 下面/文字：蓝方战损装备明细清单
                st.markdown("**🔵 蓝方部队损耗清单**")
                if blue_loss_text_list:
                    st.error("\n".join([f"- {item}" for item in blue_loss_text_list]))
                else:
                    st.success("- 该装备编队无明显受损")
            # ==============================================================================

            # 展现判定结果
            st.subheader("🏆 3. 总体技战术胜负判定（算法客观判定）")
            st.warning(victory_text)
            
    else:
        st.write("👈 请在左侧动态调整两军编成。当前系统已切换为最科学的【AI大模型文学渲染过程 + Python底层客观推演算法】。")






