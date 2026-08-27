import streamlit as st
import json
import requests
import time
import pandas as pd  

def load_db():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "红方阵营": {
                "ZTD-05": {"名称": "05式两栖突击车", "类型": "两栖装甲", "单价_万元": 2500, "战力权重": 30},
                "075-LHD": {"名称": "075型两栖攻击舰", "类型": "立体登陆舰", "单价_万元": 300000, "战力权重": 500},
                "Z-19": {"名称": "直-19武装直升机", "类型": "低空火力", "单价_万元": 4000, "战力权重": 45},
                "CH-5": {"名称": "彩虹-5察打一体无人机", "类型": "无人机群", "单价_万元": 15000, "战力权重": 25}
            },
            "蓝方阵营": {
                "M60A3": {"名称": "M60A3主战坦克", "类型": "滩头反击装甲", "单价_万元": 1500, "战力权重": 15},
                "APACHE-E": {"名称": "AH-64E阿帕奇直升机", "类型": "反制航空兵", "单价_万元": 14000, "战力权重": 60},
                "PATRIOT-3": {"名称": "爱国者-3防空系统", "类型": "抗饱和打击", "单价_万元": 30000, "战力权重": 120},
                "BEACH-FORT": {"名称": "滩头加固永备碉堡", "类型": "岸防工事", "单价_万元": 500, "战力权重": 40}
            }
        }

def call_aliyun_script_generator(prompt):
    url = "https://aliyuncs.com"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "qwen-max",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 1500  # 💡 核心修复点1：强制加大Token上限，允许大模型吐出超长篇幅文本
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=25, proxies={"http": None, "https": None})
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception:
        pass
    
    try:
        res = requests.post("https://pollinations.ai", json={
            "messages": [{"role": "user", "content": prompt}], "model": "openai-large"
        }, timeout=15)
        if res.status_code == 200:
            return res.text
    except Exception:
        pass
    return "前沿交战地域突发暴风雨与电子强干扰。红方装甲先遣队与蓝方防御阵地骤然遭遇，密集火力瞬间撕裂夜空，多型重装突击兵器在狭长地带迎头撞击，爆发惨烈的多维对冲。"

# ========== Streamlit 网页前端展示逻辑 ==========
st.set_page_config(page_title="科学级兵棋推演想定智能生成系统", layout="wide")
st.title("🎖️ 科学级兵棋推演想定智能生成系统 (渡海登岛大文本版)")
st.write("根据陆军兵种大学大语言模型想定生成论文架构开发（两栖战役演练方案）")

API_KEY = "sk-ws-H.EYYRXHM.8hPe.MEUCIF6taU1uYI2wo2DJTG3DTmsA8cdnH38iLmu6x_etID0JAiEAsoxe2dxqlRAPW4p_3BFEoZq7XSeY4YGBy4ffDN-tjX0"

db = load_db()
col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.header("📥 跨海登陆参数配置")
    keywords = st.text_area("战场环境与行动关键词", "第一波次抢滩、联合火力准备、强电磁干扰、航道破障、蓝方滩头坚固工事反击")
    
    st.subheader("🔴 红方跨海登陆编成")
    red_options = list(db["红方阵营"].keys())
    selected_red = st.multiselect("请选择红方出动突击装备", red_options, default=red_options[:2])
    
    red_inventory = {}
    for req_eq in selected_red:
        eq_data = db["红方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=15, key=f"red_{req_eq}")
        red_inventory[req_eq] = {"名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"], "战力权重": eq_data.get("战力权重", 20)}

    st.subheader("🔵 蓝方岸防抗登编成")
    blue_options = list(db["蓝方阵营"].keys())
    selected_blue = st.multiselect("请选择蓝方守备拦截装备", blue_options, default=blue_options[:2])
    
    blue_inventory = {}
    for req_eq in selected_blue:
        eq_data = db["蓝方阵营"][req_eq]
        count = st.number_input(f"初始数量 ({eq_data['名称']})", min_value=1, max_value=100, value=10, key=f"blue_{req_eq}") 
        blue_inventory[req_eq] = {"名称": eq_data["名称"], "初始数量": count, "单价_万元": eq_data["单价_万元"], "战力权重": eq_data.get("战力权重", 22)}

    run_button = st.button("🚀 开始自动化渡海推演", use_container_width=True)

with col_right:
    st.header("📄 渡海登岛想定推演报告")
    
    if run_button:
        red_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['远程名称'] if '远程名称' in v else v['名称']}" for k, v in red_inventory.items()])
        blue_summary = ", ".join([f"{v['初始数量']}辆/架/套 {v['远程名称'] if '远程名称' in v else v['名称']}" for k, v in blue_inventory.items()])
        
        # ==================== ⚙️ 核心算法层 ====================
        w_jamming_modifier = 0.4 if "电磁干扰" in keywords else 1.0 
        w_fort_modifier = 1.3 if "坚固工事" in keywords else 1.0  
        
        red_total_force = 0
        for k, v in red_inventory.items():
            current_weight = v["战力权重"]
            if "无人机" in v["名称"]: current_weight *= w_jamming_modifier
            red_total_force += v["初始数量"] * current_weight

        blue_total_force = 0
        for k, v in blue_inventory.items():
            current_weight = v["战力权重"]
            if "碉堡" in v["名称"] or "工事" in v["名称"]: current_weight *= w_fort_modifier
            blue_total_force += v["初始数量"] * current_weight

        if blue_total_force == 0: blue_total_force = 1
        force_ratio = red_total_force / blue_total_force

        if force_ratio >= 2.5:
            winner = "红方突击群大胜，成功攻占滩头并巩固登岛阵地"
            victory_text = f"【红方成功突击登岛】：红方波次展现了毁灭性的跨海联合突击能力（总战力积分 {red_total_force:.0f}）。在密集的破障机动下，红方突击车群成功撕裂蓝方第一道抗登防线，建立稳固的滩头阵地，后续重装部队开始多点接力卸载。"
            red_loss_rate, blue_loss_rate = 0.20, 0.85 
        elif force_ratio <= 0.4:
            winner = "蓝方岸防群胜利，红方抢滩进攻群被彻底击退"
            victory_text = f"【蓝方成功阻击反登陆】：蓝方依托海基火网与反装甲防御工事（总战力积分 {blue_total_force:.0f}），对红方贸然抵滩的两栖突击编队实施了灾难性的反制拦截。红方破障行动失败，攻势被彻底击退。"
            red_loss_rate, blue_loss_rate = 0.90, 0.15 
        else:
            winner = "两军在滩头阵地爆发白热化反复拉锯僵持"
            victory_text = f"【滩头惨烈僵持拉锯】：两军两栖力量与守备部队爆发白热化的水际攻防战（红方 {red_total_force:.0f} 对 蓝方 {blue_total_force:.0f}）。红方先遣队艰难涉水抵滩，两军在沙滩阵地爆发极为惨烈的反复拉锯消耗战。"
            red_loss_rate, blue_loss_rate = 0.45, 0.50 

        red_loss_text_list = []
        red_total_cost = 0
        for k, v in red_inventory.items():
            loss_num = int(v["初始数量"] * red_loss_rate)
            loss_num = max(0, min(loss_num, v["初始数量"]))
            if loss_num > 0:
                red_loss_text_list.append(f"{v['远程名称'] if '远程名称' in v else v['名称']} 损失 {loss_num} 辆/架/套")
                red_total_cost += loss_num * v["单价_万元"]

        blue_loss_text_list = []
        blue_total_cost = 0
        for k, v in blue_inventory.items():
            loss_num = int(v["初始数量"] * blue_loss_rate)
            loss_num = max(0, min(loss_num, v["初始数量"]))
            if loss_num > 0:
                blue_loss_text_list.append(f"{v['远程名称'] if '远程名称' in v else v['名称']} 损失 {loss_num} 辆/架/套")
                blue_total_cost += loss_num * v["单价_万元"]
        # ==============================================================================

        # 💡 核心修复点2：注入严厉的【三阶段强制骨架】指令，彻底粉碎大模型偷懒写短文本的恶习！
        ai_prompt = (
            f"你是一位精通两栖两栖战役推演的军事想定主笔专家。请根据以下真实推演参数，必须写出一篇字数在 350 到 500 字之间、气势宏大、极具战术细节的详实两栖交战想定过程文本。"
            f"当前战场参数：红方初始群【{red_summary}】，在【{keywords}】的背景下强攻；蓝方派遣【{blue_summary}】依托工事死守阻击。算法最终测算的局势胜负判定为【{winner}】。"
            f"【硬性写作框架规范】：你必须严格分为以下三个部分依次详细长篇扩写，字数必须充实饱满，禁止合并简写："
            f"一、一阶段【远程联合火力准备】：详细描述红方导弹与无人机升空压制蓝方防空，海浪颠簸及强电磁干扰下的火力博弈场景；"
            f"二、二阶段【水际滩头抗阻破障】：详细描写两栖突击车群在暴风雨和硝烟中强行冲滩，蓝方碉堡火网全开扫射，障碍物和雷障爆破的惨烈细节；"
            f"三、三阶段【纵深核心阵地夺控】：结合最终结局【{winner}】，用长篇篇幅详实剖析两军围绕滩头主阵地的最后白热化对冲。直接输出想定纯文本，去掉任何多余客套废话！"
        )

        with st.spinner("🚀 火力骨架已强制注入，大语言模型正在全量渲染详实渡海登岛想定描述..."):
            ai_battle_process = call_aliyun_script_generator(ai_prompt)
            st.success("✨ 渡海登岛长篇战役想定推演完成！")
            
            # 展示两栖战役描述
            st.subheader("🎬 1. 渡海登岛联合战役想定描述（AI大模型三阶段渲染生成）")
            st.info(ai_battle_process)
            
            # 展示精确战损
            st.subheader("📊 2. 两栖抗阻精确战损统计（军事算法层计算）")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 🔴 红方抢滩突击群损耗")
                if red_loss_text_list:
                    st.error("\n".join([f"- {item}" for item in red_loss_text_list]))
                else:
                    st.success("- 先遣突击队无明显装备损耗")
                st.metric(label="红方抢滩损失总额", value=f"{red_total_cost} 万元")
                    
            with c2:
                st.markdown("### 🔵 蓝方守岛岸防群损耗")
                if blue_loss_text_list:
                    st.error("\n".join([f"- {item}" for item in blue_loss_text_list]))
                else:
                    st.success("- 岸防工事集群未受实质损耗")
                st.metric(label="蓝方抗登损失总额", value=f"{blue_total_cost} 万元")
            
            # ==================== 标准二维排序靠左柱状图 ====================
            st.subheader("📈 3. 两栖双边战损经济开支直观对比 (单位: 万元)")
            chart_dataframe = pd.DataFrame(
                {
                    "经济损失总额(万元)": [red_total_cost, blue_total_cost, 0, 0, 0]
                },
                index=["01.🔴 红方抢滩群", "02.🔵 蓝方守岛群", "03. ", "04.  ", "05.   "]  
            )
            st.bar_chart(chart_dataframe)

            # 展现战术判定
            st.subheader("🏆 4. 总体两栖攻防胜负判定（算法客观判定）")
            st.warning(victory_text)
            
    else:
        st.write("👈 请在左侧动态调整兵力数量。系统将自动调用大模型全量长篇扩写。")










