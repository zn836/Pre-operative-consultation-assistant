import streamlit as st
import os
import re
from pathlib import Path
from dotenv import load_dotenv
import requests
from prompts import get_qa_prompt, get_suggested_questions_prompt, get_expert_answer_prompt

# 加载环境变量
load_dotenv()

# API配置 - 千问API
API_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
API_KEY = "sk-0d3e8da3cba84377828e32b50562da9c"  # 请替换为您的千问API Key
MODEL_NAME = "qwen-plus"  # 可选: qwen-turbo, qwen-plus, qwen-max

# 页面配置
st.set_page_config(
    page_title="术前谈话助手",
    page_icon="🏥",
    layout="wide"
)

# 自定义CSS - 修复手机端显示问题
st.markdown("""
<style>
    /* 推荐问题按钮样式 - 支持文字换行 */
    .recommended-questions button {
        white-space: normal !important;
        word-wrap: break-word !important;
        word-break: break-word !important;
        height: auto !important;
        min-height: 2.5rem !important;
        padding: 0.75rem 1rem !important;
        text-align: left !important;
        line-height: 1.5 !important;
    }

    /* 手机端优化 */
    @media (max-width: 768px) {
        .recommended-questions button {
            font-size: 0.9rem !important;
            padding: 0.6rem 0.8rem !important;
        }

        /* 确保按钮容器不超出屏幕 */
        .recommended-questions {
            width: 100% !important;
            overflow: hidden !important;
        }

        /* 按钮文字换行 */
        .recommended-questions button p {
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }
    }

    /* 答案框样式 */
    .answer-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)



# 初始化 session state
if 'current_video' not in st.session_state:
    st.session_state.current_video = None
if 'subtitles' not in st.session_state:
    st.session_state.subtitles = []
if 'suggested_questions' not in st.session_state:
    st.session_state.suggested_questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = ""
if 'video_time' not in st.session_state:
    st.session_state.video_time = 0
if 'video_start_time' not in st.session_state:
    st.session_state.video_start_time = 0
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None
if 'last_timestamps' not in st.session_state:
    st.session_state.last_timestamps = []
if 'current_user_question' not in st.session_state:
    st.session_state.current_user_question = ""
if 'relevant_content' not in st.session_state:
    st.session_state.relevant_content = ""
if 'expert_answer' not in st.session_state:
    st.session_state.expert_answer = None
if 'show_expert_button' not in st.session_state:
    st.session_state.show_expert_button = False


def parse_subtitles(subtitle_file):
    """解析字幕文件"""
    subtitles = []
    try:
        with open(subtitle_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    # 解析格式：[00:00:00.620 - 00:00:12.300] 文本内容
                    match = re.match(r'\[([\d:\.]+)\s*-\s*([\d:\.]+)\]\s*(.+)', line)
                    if match:
                        start_time = match.group(1)
                        end_time = match.group(2)
                        text = match.group(3)
                        subtitles.append({
                            'start': start_time,
                            'end': end_time,
                            'text': text
                        })
    except Exception as e:
        st.error(f"字幕文件解析失败: {str(e)}")
    return subtitles


def time_to_seconds(time_str):
    """将时间字符串转换为秒数"""
    try:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
        return hours * 3600 + minutes * 60 + seconds
    except:
        return 0


def get_relevant_subtitle_content(subtitles, timestamp, context_range=3):
    """
    获取指定时间点附近的字幕内容

    Args:
        subtitles: 字幕列表
        timestamp: 目标时间戳字符串
        context_range: 前后扩展的字幕条数

    Returns:
        相关字幕内容的字符串
    """
    target_seconds = time_to_seconds(timestamp)

    # 找到最接近的字幕索引
    closest_index = -1
    min_diff = float('inf')

    for i, sub in enumerate(subtitles):
        sub_seconds = time_to_seconds(sub['start'])
        diff = abs(sub_seconds - target_seconds)
        if diff < min_diff:
            min_diff = diff
            closest_index = i

    if closest_index == -1:
        return ""

    # 获取前后范围内的字幕
    start_index = max(0, closest_index - context_range)
    end_index = min(len(subtitles), closest_index + context_range + 1)

    relevant_subs = subtitles[start_index:end_index]

    # 格式化输出
    content = '\n'.join([
        f"[{sub['start']} - {sub['end']}] {sub['text']}"
        for sub in relevant_subs
    ])

    return content


def extract_timestamp_from_answer(answer):
    """从回答中提取时间戳（支持多个时间点）"""
    timestamps = []

    # 匹配多种格式的时间戳
    patterns = [
        r'时间点\s*\d*[:：]\s*([\d:\.]+)',  # 时间点: 00:02:15 或 时间点1: 00:02:15
        r'【视频位置】\s*([\d:\.]+)',         # 【视频位置】00:02:15
        r'\[([\d:\.]+)\]',                   # [00:02:15]
        r'(\d{2}:\d{2}:\d{2}(?:\.\d+)?)'     # 通用时间格式
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, answer)
        for match in matches:
            timestamp = match.group(1)
            if timestamp not in timestamps:
                timestamps.append(timestamp)

    # 返回第一个时间戳（主要时间点）
    return timestamps[0] if timestamps else None


def extract_all_timestamps(answer):
    """从回答中提取所有时间戳"""
    timestamps = []

    patterns = [
        r'时间点\s*\d*[:：]\s*([\d:\.]+)',  # 支持 "时间点: 00:02:15" 或 "时间点1: 00:02:15"
        r'【视频位置】\s*([\d:\.]+)',
        r'\[([\d:\.]+)\]'
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, answer)
        for match in matches:
            timestamp = match.group(1)
            if timestamp not in timestamps:
                timestamps.append(timestamp)

    return timestamps


def remove_timestamp_section(answer):
    """移除回答中的时间点列表部分，只保留详细回答"""
    # 匹配并移除 "**第一步: 列出相关时间点**" 到 "**第二步: 详细回答**" 之间的内容
    # 包括各种可能的格式变体
    patterns = [
        r'\*\*第一步[:：]?\s*列出相关时间点\*\*.*?\*\*第二步[:：]?\s*详细回答\*\*',
        r'第一步[:：]?\s*列出相关时间点.*?第二步[:：]?\s*详细回答',
        r'时间点\s*\d+[:：].*?(?=\n\n|\*\*|$)',
    ]

    cleaned_answer = answer
    for pattern in patterns:
        cleaned_answer = re.sub(pattern, '', cleaned_answer, flags=re.DOTALL)

    # 清理多余的空行
    cleaned_answer = re.sub(r'\n{3,}', '\n\n', cleaned_answer)
    cleaned_answer = cleaned_answer.strip()

    return cleaned_answer


def call_qwen_api(question, subtitles_text):
    """调用GPT API"""
    try:
        # 使用prompts.py中的提示词
        full_prompt = get_qa_prompt(subtitles_text, question)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.7,
            "top_p": 0.8
        }

        response = requests.post(API_BASE_URL, headers=headers, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"API调用失败: {response.status_code} - {response.text}"
    except Exception as e:
        return f"调用API时出错: {str(e)}"


def call_expert_answer_api(question, relevant_content, timestamp):
    """调用专家回答API"""
    try:
        # 使用prompts.py中的ANSWER_PROMPT
        full_prompt = get_expert_answer_prompt(question, relevant_content, timestamp)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": full_prompt}
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.8
        }
        
        response = requests.post(API_BASE_URL, headers=headers, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"API调用失败: {response.status_code} - {response.text}"
    except Exception as e:
        return f"调用API时出错: {str(e)}"


def generate_suggested_questions(subtitles_text):
    """生成推荐问题"""
    try:
        # 使用prompts.py中的提示词
        prompt = get_suggested_questions_prompt(subtitles_text[:1000])

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }

        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 300,
            "temperature": 0.8
        }

        response = requests.post(API_BASE_URL, headers=headers, json=data, timeout=60)

        if response.status_code == 200:
            result = response.json()
            answer_text = result['choices'][0]['message']['content']
            questions = [q.strip() for q in answer_text.strip().split('\n') if q.strip()]
            # 清理问题格式（移除可能的编号）
            cleaned_questions = []
            for q in questions:
                q = re.sub(r'^\d+[\.\)]\s*', '', q)  # 移除 "1. " 或 "1) " 格式
                if q:
                    cleaned_questions.append(q)
            return cleaned_questions[:5]
        return []
    except:
        return []


# 自动加载视频（隐藏选择功能）
video_folder = Path("video")
if video_folder.exists():
    video_files = list(video_folder.glob("*.mp4")) + list(video_folder.glob("*.avi")) + list(video_folder.glob("*.mov"))
    video_names = [f.name for f in video_files]

    if video_names:
        # 自动选择第一个视频文件
        selected_video = video_names[0]

        # 当视频改变时，加载新视频和字幕
        if selected_video != st.session_state.current_video:
            st.session_state.current_video = selected_video
            video_path = video_folder / selected_video

            # 清空之前的答案和时间戳
            st.session_state.last_answer = None
            st.session_state.last_timestamps = []
            st.session_state.video_time = 0
            st.session_state.video_start_time = 0

            # 加载对应的字幕文件
            subtitle_path = video_path.with_suffix('.txt')
            if subtitle_path.exists():
                st.session_state.subtitles = parse_subtitles(subtitle_path)

                # 生成推荐问题
                subtitles_text = '\n'.join([f"[{s['start']}] {s['text']}" for s in st.session_state.subtitles])
                st.session_state.suggested_questions = generate_suggested_questions(subtitles_text)
            else:
                st.session_state.subtitles = []

        # 视频播放区
        #st.markdown("### 🎬 视频播放")
        video_path = video_folder / selected_video

        # 如果需要跳转，更新状态
        if st.session_state.video_time > 0:
            st.session_state.video_start_time = st.session_state.video_time
            st.session_state.video_time = 0

        if st.session_state.video_start_time > 0:
            st.video(str(video_path), start_time=int(st.session_state.video_start_time))
        else:
            st.video(str(video_path))

        # 问答区
        #st.markdown("### 💬 智能问答")

        # 使用聊天输入框（类似ChatGPT移动端）
        user_question = st.chat_input("请输入您的问题，例如:术前需要做哪些准备?")

        # 如果有新输入，自动触发提问
        ask_button = False
        if user_question:
            ask_button = True

        # 创建一行多列布局：播放按钮、专家解答按钮
        col1, col2 = st.columns([1, 1])

        with col1:
            # 按钮状态：只有当有时间戳时才启用
            play_disabled = not bool(st.session_state.last_timestamps)
            if st.button("📍 播放内容",
                        key="jump_most_relevant",
                        type="primary" if not play_disabled else "secondary",
                        disabled=play_disabled,
                        use_container_width=True):
                if st.session_state.last_timestamps:
                    timestamp = st.session_state.last_timestamps[0]
                    st.session_state.video_time = time_to_seconds(timestamp)
                    st.rerun()

        with col2:
            # 按钮状态：只有当有时间戳时才启用
            expert_disabled = not bool(st.session_state.last_timestamps)
            if st.button("👨‍⚕️ 详细解答",
                        key="get_expert_answer",
                        type="primary" if not expert_disabled else "secondary",
                        disabled=expert_disabled,
                        use_container_width=True):
                if st.session_state.last_timestamps:
                    with st.spinner("正在获取详细回答..."):
                        timestamp = st.session_state.last_timestamps[0]
                        # 使用第一步的内容概要作为输入
                        expert_answer = call_expert_answer_api(
                            st.session_state.current_user_question,
                            st.session_state.last_answer,  # 使用内容概要
                            timestamp
                        )
                        st.session_state.expert_answer = expert_answer
                        st.rerun()

        # 处理提问
        if ask_button and user_question:
            if st.session_state.subtitles:
                # 立即清空之前的状态，让按钮变灰
                st.session_state.last_answer = None
                st.session_state.last_timestamps = []
                st.session_state.expert_answer = None
                st.session_state.show_expert_button = False

                with st.spinner("正在查找相关片段..."):
                    # 准备字幕文本
                    subtitles_text = '\n'.join([
                        f"[{s['start']} - {s['end']}] {s['text']}"
                        for s in st.session_state.subtitles
                    ])

                    # 第一步：调用SYSTEM_PROMPT，只获取时间点和简要描述
                    answer = call_qwen_api(user_question, subtitles_text)

                    # 提取最相关的时间戳（只取第一个）
                    all_timestamps = extract_all_timestamps(answer)
                    most_relevant_timestamp = [all_timestamps[0]] if all_timestamps else []

                    # 移除时间点列表部分，只保留描述
                    cleaned_answer = remove_timestamp_section(answer)

                    # 存储到 session_state
                    st.session_state.current_user_question = user_question
                    st.session_state.last_answer = cleaned_answer
                    st.session_state.last_timestamps = most_relevant_timestamp

                    # 如果找到了时间戳，显示专家回答按钮
                    if most_relevant_timestamp:
                        st.session_state.show_expert_button = True

                    st.rerun()  # 刷新页面以更新按钮状态
            else:
                st.error("❌ 请先选择包含字幕文件的视频")

        # 显示回答（在外部显示，这样按钮点击后仍然可见）
        if st.session_state.last_answer:
            # 如果没有找到时间点，显示提示信息
            if not st.session_state.last_timestamps:
                st.info("💡 视频中未找到与该问题直接相关的具体时间点，请重新询问或者找医生咨询详细问题！")

            # 显示专家详细解答
            if st.session_state.expert_answer:
                st.markdown('<div class="answer-box" style="background-color: #f0fff4; border-left-color: #38a169;">', unsafe_allow_html=True)
                st.markdown("#### 👨‍⚕️ 专家详细解答:")
                st.markdown(st.session_state.expert_answer)
                st.markdown('</div>', unsafe_allow_html=True)


        # 推荐问题区
        if st.session_state.suggested_questions:
            st.markdown("### 💡 猜你可能想问")
            st.markdown('<div class="recommended-questions">', unsafe_allow_html=True)

            # 每个问题独立成行,避免挤在一起
            for idx, question in enumerate(st.session_state.suggested_questions):
                if st.button(question, key=f"suggest_{idx}", use_container_width=True):
                    # 直接处理提问逻辑
                    if st.session_state.subtitles:
                        # 立即清空之前的状态
                        st.session_state.last_answer = None
                        st.session_state.last_timestamps = []
                        st.session_state.expert_answer = None
                        st.session_state.show_expert_button = False

                        with st.spinner("正在查找相关片段..."):
                            # 准备字幕文本
                            subtitles_text = '\n'.join([
                                f"[{s['start']} - {s['end']}] {s['text']}"
                                for s in st.session_state.subtitles
                            ])

                            # 调用API获取答案
                            answer = call_qwen_api(question, subtitles_text)

                            # 提取时间戳
                            all_timestamps = extract_all_timestamps(answer)
                            most_relevant_timestamp = [all_timestamps[0]] if all_timestamps else []

                            # 移除时间点列表部分
                            cleaned_answer = remove_timestamp_section(answer)

                            # 存储到 session_state
                            st.session_state.current_user_question = question
                            st.session_state.last_answer = cleaned_answer
                            st.session_state.last_timestamps = most_relevant_timestamp

                            if most_relevant_timestamp:
                                st.session_state.show_expert_button = True

                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ video 文件夹中没有找到视频文件")
else:
    st.error("❌ 未找到 video 文件夹，请创建该文件夹并放入视频文件")

# 页脚
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #888;">💡 视频问答助手 | Powered by Streamlit & 阿里云千问</div>',
    unsafe_allow_html=True
)
