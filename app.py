import streamlit as st
import json
import requests

# ========== 配置：填入你的阿里云百炼 DashScope API_KEY ==========
API_KEY = "sk-ws-H.EYYRXHM.8hPe.MEUCIF6taU1uYI2wo2DJTG3DTmsA8cdnH38iLmu6x_etID0JAiEAsoxe2dxqlRAPW4p_3BFEoZq7XSeY4YGBy4ffDN-tjX0"

def call_aliyun_llm(red_input, blue_input, keywords):
    """直接集成在网页内部的阿里云百炼标准 Chat 通道"""
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            database = json.load(f)
        with open("prompt_template.txt", "r", encoding="utf-8") as f:
            template = f.read()
    except Exception as e:
        return f"Error: 读取本地文件失败，请确保 data.json 和 prompt_template.txt 已上传到GitHub。原因: {e}"

    prompt = template.format(
        database_info=json.dumps(database, ensure_ascii=False, indent=2),
        red_input=red_input,
        blue_input=blue_input,
        keywords=keywords
    )

    # 阿里云百炼最新最标准的 OpenAI 兼容通道网址
    url = "https://aliyuncs.com"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "qwen-max",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        # 发送请求（云端无本地代理干扰，可直接畅通连接）
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            return f"Error: 阿里云拒绝了请求 (HTTP {response.status_code})。\n详细原因: {response.text}"
            
        res_body = response.json()
        return res_body["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: 请求网络连接失败。具体原因: {e}"

# ========== Streamlit 网页前端展示逻辑 ==========
st.set_page_config(page_title="作战仿真想定自动化生成系统", layout="wide")
st.title("🎖️ 作战仿真想定自动化生成系统 (论文标准版)")
st.write("根据陆军兵种大学大语言模型想定生成论文架构（思维链整合）开发")

# 1. 软件左侧输入区
st.sidebar.header("📥 推演参数输入")
red_input = st.sidebar.text_input("红方兵力编成", "10辆 99A式主战坦克, 2架 直-10武装直升机")
blue_input = st.sidebar.text_input("蓝方兵力编成", "8辆 M1A2主战坦克, 4架 AH-64阿帕奇武装直升机")
keywords = st.sidebar.text_area("战场行动与环境关键词", "山地遭遇战、夜间突袭、暴雨环境、蓝方低空伏击")

# 2. 软件核心运行按钮
if st.sidebar.button("🚀 开始自动化推演生成"):
    with st.spinner("大模型正在根据论文思维链进行逻辑推理，请稍候..."):
        try:
            # 直接调用上面写好的函数
            raw_result = call_aliyun_llm(red_input, blue_input, keywords)
            
            # 清理大模型可能返回的 Markdown 标记
            clean_result = raw_result.strip().strip("```json").strip("```")
            
            # 将大模型返回的中文 JSON 文本解析为 Python 可以识别的数据
            result_json = json.loads(clean_result)
            
            st.success("✨ 想定推演生成成功！")
            
            # 3. 展现结果：战场过程描述
            st.header("1. 🎬 战场想定过程描述")
            st.info(result_json.get("战场想定过程", "未生成过程"))
            
            # 4. 展现结果：数据损耗
            st.header("2. 📊 损耗结果统计")
            
            # 提取全中文嵌套的“推演结果”
            stats = result_json.get("推演结果", {})
            red_stats = stats.get("红方统计", {})
            blue_stats = stats.get("蓝方统计", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🔴 红方统计")
                st.write(f"**装备战损：** {red_stats.get('装备战损', '无')}")
                st.write(f"**经济损失：** {red_stats.get('经济损失_百万元', '0')} 百万元")
            with col2:
                st.subheader("🔵 蓝方统计")
                st.write(f"**装备战损：** {blue_stats.get('装备战损', '无')}")
                st.write(f"**经济损失：** {blue_stats.get('经济损失_百万元', '0')} 百万元")
                
            # 5. 展现结果：胜负判定
            st.header("3. 🏆 战术胜负判定")
            st.warning(stats.get("战术胜负判定", "未生成判定"))
            
        except Exception as e:
            st.error(f"解析大模型返回数据时出错。错误信息: {e}")
            if 'raw_result' in locals():
                st.text("大模型原始返回文本如下（可用于排查）：")
                st.code(raw_result)

