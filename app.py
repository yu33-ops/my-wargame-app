import streamlit as st
import json
import requests
import time

# ==================== 1. 核心配置：阿里云 API_KEY ====================
API_KEY = "sk-ws-H.EYYRXHM.8hPe.MEUCIF6taU1uYI2wo2DJTG3DTmsA8cdnH38iLmu6x_etID0JAiEAsoxe2dxqlRAPW4p_3BFEoZq7XSeY4YGBy4ffDN-tjX0"

# ==================== 2. 前端美化：重装备视觉画廊映射表 ====================
EQUIPMENT_IMAGES = {
    "99A式主战坦克": "https://178.com",  
    "直-10武装直升机": "https://itc.cn",
    "红旗-9B防空导弹": "https://sinaimg.cn",
    "ASN-301反辐射 drones": "https://bjd.com.cn",
    
    "M1A2主战坦克": "https://sinaimg.cn",
    "AH-64D阿帕奇直升机": "https://sinaimg.cn",
    "爱国者-3防空导弹": "https://lhv.hk",
    "MQ-9死神无人机": "https://zhimg.com"
}

# ==================== 3. 知识存储层：国产达梦数据库（带持久化兜底） ====================
def load_db_from_dm():
    db_data = {"红方阵营": {}, "蓝方阵营": {}}
    fallback_db = {
        "红方阵营": {
            "ZTZ-99A": {"名称": "99A式主战坦克", "类型": "地面装甲", "单价_万元": 2000, "战力权重": 20, "作战范围": "5km直射", "战斗半径_km": 400, "简介": "直射突击兵器"},
            "WZ-10": {"名称": "直-10武装直升机", "类型": "航空兵力", "单价_万元": 5000, "战力权重": 50, "作战范围": "防区外突击", "战斗半径_km": 300, "简介": "树梢机动反装甲"},
            "HQ-9B": {"名称": "红旗-9B防空导弹", "类型": "防空反导", "单价_万元": 15000, "战力权重": 100, "作战范围": "200km相控阵", "战斗半径_km": 0, "简介": "体系核心防空节点"},
            "ASN-301": {"名称": "ASN-301反辐射 drones", "类型": "无人机群", "单价_万元": 200, "战力权重": 5, "作战范围": "280km巡飞", "战斗半径_km": 150, "简介": "自杀式雷达压制"}
        },
        "蓝方阵营": {
            "M1A2": {"名称": "M1A2主战坦克", "类型": "地面装甲", "单价_万元": 6000, "战力权重": 22, "作战范围": "4km直射", "战斗半径_km": 450, "简介": "高数字化贫铀装甲"},
            "AH-64D": {"名称": "AH-64D阿帕奇直升机", "类型": "航空兵力", "单价_万元": 14000, "战力权重": 55, "作战范围": "长弓雷达区", "战斗半径_km": 480, "简介": "全天候重型武装"},
            "PATRIOT": {"名称": "爱国者-3防空导弹", "类型": "防空反导", "单价_万元": 30000, "战力权重": 110, "作战范围": "160km末端", "战斗半径_km": 0, "简介": "末端反导控制网"},
            "MQ-9": {"名称": "MQ-9死神无人机", "类型": "无人机群", "单价_万元": 11000, "战力权重": 15, "作战范围": "地狱火射程", "战斗半径_km": 1200, "简介": "长航时察打一体"}
        }
    }
    try:
        import dmPython
        conn = dmPython.connect(server="127.0.0.1", port=5236, user="SYSDBA", password="YOUR_PASSWORD")
        cursor = conn.cursor()
        cursor.execute("SELECT CODE, NAME, EQ_TYPE, PRICE_WAN, COMBAT_RANGE, COMBAT_RADIUS, FORCE_WEIGHT, DESCRIPTION FROM RED_FORCES")
        for row in cursor.fetchall():
            db_data["红方阵营"][row[0]] = {
                "名称": row[1], "类型": row[2], "单价_万元": row[3],
                "作战范围": row[4], "战斗半径_km": row[5], "战力权重": row[6], "简介": row[7]
            }
        cursor.execute("SELECT CODE, NAME, EQ_TYPE, PRICE_WAN, COMBAT_RANGE, COMBAT_RADIUS, FORCE_WEIGHT, DESCRIPTION FROM BLUE_FORCES")
        for row in cursor.fetchall():
            db_data["蓝方阵营"][row[0]] = {
                "名称": row[1], "类型": row[2], "单价_万元": row[3],
                "作战范围": row[4], "战斗半径_km": row[5], "战力权重": row[6], "简介": row[7]
            }
        cursor.close()
        conn.close()
        return db_data
    except Exception:
        return fallback_db

# ==================== 4. 任务调度层：阿里云百炼大模型 AI 剧本生成接口 ====================
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

# ==================== 5. 前端展示层布局（Streamlit Web 架构） ====================
st.set_page_config(page_title="高级兵棋推演想定智能生成系统", layout="wide")
st.title("🎖️ 高级兵棋推演想定智能生成系统")
st.write("根据陆军兵种大学大语言模型自动化想定生成论文架构开发（大模型剧本 + Python专家算法双驱动版）")

db = load_db_from_dm()
col_left, col_right = st.columns([1, 1.2])

# ---- 5.1 左侧输入控制面板 ----
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
        red_inventory[req_eq] = {
            "名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"], 
            "战力权重": eq_data["战力权重"], "战斗半径": eq_data["战斗半径_km"]
        }

    st.subheader("🔵 蓝方兵力编成")
    blue_options = list(db["蓝方阵营"].keys())
    selected_blue = st.multiselect("请选择蓝方出动装备", blue_options, default=blue_options[:2])
    
    blue_inventory = {}
    for req_eq in selected_blue:
        eq_data = db["蓝方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=2, key=f"blue_{req_eq}") 
        blue_inventory[req_eq] = {
            "名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"], 
            "战力权重": eq_data["战力权重"], "战斗半径": eq_data["战斗半径_km"]
        }

    run_button = st.button("🚀 开始自动化科学推演", use_container_width=True)

# ---- 5.2 右侧成果与画廊渲染面板 ----
with col_right:
    st.header("📄 作战仿真想定推演报告")
    
    st.subheader("📷 当前参战核心主战装备点阅")
    all_selected_names = [v["名称"] for k, v in red_inventory.items()] + [v["名称"] for k, v in blue_inventory.items()]
    
    if all_selected_names:
        img_cols = st.columns(len(all_selected_names))
        for idx, eq_name in enumerate(all_selected_names):
            with img_cols[idx]:
                img_url = EQUIPMENT_IMAGES.get(eq_name, "https://placeholder.com")
                st.image(img_url, caption=f"⚔️ {eq_name}", use_container_width=True)
                
    st.markdown("---")

    if run_button:
        red_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['名称']}" for k, v in red_inventory.items()])
        blue_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['名称']}" for k, v in blue_inventory.items()])
        
        # 加权算法
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
            victory_text = f"【红方压倒性大胜】：红方集结了绝对优势兵力（总战力积分 {red_total_force:.0f}），对蓝方防线（总战力积分 {blue_total_force:.0f}）形成高达 {force_ratio:.1f} 倍的碾压优势。在强大的突击纵深火力下，蓝方阵地全面崩溃。"
            red_loss_rate, blue_loss_rate = 0.15, 0.90 
        elif force_ratio <= 0.4:
            winner = "蓝方"
            victory_text = f"【蓝方防守大胜】：蓝方依托有利地形与火网防御（总战力积分 {blue_total_force:.0f}），对红方推进突击编队（总战力积分 {red_total_force:.0f}）实施了毁灭性的饱和打击，红方攻势被彻底瓦解，全线溃退。"
            red_loss_rate, blue_loss_rate = 0.85, 0.10 
        else:
            winner = "战局僵持"
            victory_text = f"【惨烈拉锯僵持】：双方交战地域的总战力规模处于势均力敌态势（红方 {red_total_force:.0f} 对 蓝方 {blue_total_force:.0f}）。两军编制要素相互克制，爆发惨烈拉锯，战场陷入僵持阻击阶段。"
            red_loss_rate, blue_loss_rate = 0.40, 0.45 

        red_loss_text_list = []
        red_total_cost = 0
        for k, v in red_inventory.items():
            loss_num = max(0, min(int(v["初始数量"] * red_loss_rate), v["初始数量"]))
            if "无人机" in v["名称"] and winner != "红方": 
                loss_num = max(0, min(int(v["初始数量"] * min(red_loss_rate * 1.5, 1.0)), v["初始数量"]))
            if loss_num > 0:
                red_loss_text_list.append(f"{v['名称']} 损失 {loss_num} 辆/架/套")
                red_total_cost += loss_num * v["单价_万元"]

        blue_loss_text_list = []
        blue_total_cost = 0
        for k, v in blue_inventory.items():
            loss_num = max(0, min(int(v["初始数量"] * blue_loss_rate), v["初始数量"]))
            if "无人机" in v["名称"] and winner != "蓝方": 
                loss_num = max(0, min(int(v["初始数量"] * min(blue_loss_rate * 1.5, 1.0)), v["初始数量"]))
            if loss_num > 0:
                blue_loss_text_list.append(f"{v['名称']} 损失 {loss_num} 辆/架/套")
                blue_total_cost += loss_num * v["单价_万元"]

        ai_prompt = f"""你是一位军事仿真想定推演的场景主笔。请根据以下真实的参数，写一段 300 到 400 字、极具硝烟感、详实的现代交战想定片段动态场景描述。
【交战背景】：红方派遣【{red_summary}】在【{keywords}】的环境中强攻；蓝方迅速出动【{blue_summary}】进行阻击。
【真实推演判定】：在这场冲突中，最终的结果判定为【{winner}】。
【写作红线要求】：
1. 纯写具有强烈临场感的交战文学描述，绝对不要包含任何 JSON、数字数字或财务总价。
2. 必须突出【{keywords}】里的恶劣天气环境对两军视线和雷达感知的反制干扰。




