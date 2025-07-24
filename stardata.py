import streamlit as st
import pandas as pd
import openai
import asyncio
from playwright.async_api import async_playwright

# 设置页面
st.set_page_config(page_title="短视频AI分析助手", layout="wide")
st.title("🎬 零代码短视频分析工具")

# 侧边栏配置
with st.sidebar:
    st.header("设置")
    api_key = st.text_input("输入OpenAI API密钥", type="password")
    platform = st.selectbox("选择平台", ["抖音", "小红书", "视频号", "支付宝生活号"])
    account_id = st.text_input("账号ID", "MS4wLjABAAAAv7iSu0e7CwqPhRxX7uOZSwOVdXJ7uUY7zv-0X9zX4Y8")
    st.info("找不到账号ID？在APP中打开个人主页，分享链接里找")

# 数据采集函数
async def get_video_data(platform, account):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 根据平台选择采集方式
        if platform == "抖音":
            await page.goto(f"https://www.douyin.com/user/{account}")
            await page.wait_for_timeout(5000)
            # 模拟滚动
            for _ in range(3):
                await page.mouse.wheel(0, 10000)
                await page.wait_for_timeout(2000)
            
            # 获取视频数据
            videos = await page.query_selector_all(".ECMy_Zdt")
            data = []
            for video in videos[:5]:  # 只取前5个
                try:
                    item = {
                        "标题": await video.eval_on_selector(".HfXFpS43", "el => el.textContent"),
                        "播放量": await video.eval_on_selector(".jjKJTfbr", "el => el.textContent"),
                        "点赞数": await video.eval_on_selector(".J6LhbnwS", "el => el.textContent"),
                        "发布时间": await video.eval_on_selector(".Xil5i8pH", "el => el.textContent")
                    }
                    data.append(item)
                except:
                    continue
            return data
        
        # 其他平台类似（实际使用时需要补充）
        return [
            {"标题": "示例视频1", "播放量": "10万", "点赞数": "1.2万", "发布时间": "3天前"},
            {"标题": "示例视频2", "播放量": "8.5万", "点赞数": "0.9万", "发布时间": "1周前"}
        ]

# AI分析函数
def analyze_with_ai(data, api_key):
    openai.api_key = api_key
    
    # 构建分析提示
    prompt = f"""
    你是一个专业的短视频分析师，请根据以下视频数据给出分析报告：
    {data}
    
    报告需要包含：
    1. 内容主题分布分析
    2. 最佳发布时间段建议
    3. 三个具体的改进建议
    4. 预测下一个热门话题
    
    用中文回复，分点列出，使用表情符号增加可读性。
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    
    return response.choices[0].message['content'].strip()

# 主界面
if st.button("开始分析", type="primary"):
    if not api_key:
        st.error("请输入OpenAI API密钥！")
    else:
        with st.spinner("🚀 正在采集数据..."):
            data = asyncio.run(get_video_data(platform, account_id))
        
        st.success(f"成功获取{len(data)}个视频数据！")
        
        # 显示数据表格
        st.subheader("视频数据概览")
        df = pd.DataFrame(data)
        st.dataframe(df)
        
        with st.spinner("🧠 AI分析中..."):
            analysis = analyze_with_ai(data, api_key)
        
        st.subheader("📊 智能分析报告")
        st.markdown(analysis)
        
        # 提供改进建议
        st.subheader("💡 优化工具包")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("下载分析报告", analysis, file_name="短视频分析报告.txt")
        with col2:
            st.button("生成视频脚本")
        with col3:
            st.button("定时发布计划")

# 使用说明
st.sidebar.markdown("""
## 使用指南
1. 获取OpenAI API密钥（免费）
2. 选择平台和输入账号ID
3. 点击"开始分析"按钮
4. 查看AI生成的报告

## 常见问题
❓ **如何获取API密钥？**  
登录OpenAI平台 → 点击右上角头像 → View API Keys → Create new key

❓ **账号ID找不到怎么办？**  
在APP中打开个人主页 → 点击分享 → 复制链接 → 链接中的一串字符就是ID
""")