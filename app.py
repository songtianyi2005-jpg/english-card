import csv
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

FILE = "words.csv"
st.title("宋国强的单词卡片")

def delete_word(target_word):
    rows = []
    with open(FILE, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row["word"] != target_word:
                rows.append(row)

    with open(FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if not os.path.exists(FILE):
    st.warning("还没有words.csv，先去运行collect_words.py收集几个词吧。")
    st.stop()
with open(FILE, "r", encoding='UTF-8', newline="") as f:
    rows = list(csv.DictReader(f))

st.write(f'共收集了{len(rows)}个单词')

for row in rows:
    with st.container(border=True):
        st.subheader(row['word'])

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            html_btn = f"""
            <style>
                /* 移除默认边距，让按钮贴紧 */
                body {{
                    margin: 0;
                    padding: 0;
                }}
                .audio-btn {{
                    background-color: #f0f2f6; /* 浅色模式背景 */
                    color: #31333F;            /* 浅色模式文字（黑灰） */
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    padding: 8px 16px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    width: 100%;
                    box-sizing: border-box;
                    transition: all 0.2s;
                }}
                /* 鼠标悬停时的效果 */
                .audio-btn:hover {{
                    border-color: #FF4B4B;
                    color: #FF4B4B;
                }}

                /* 如果系统/浏览器是深色模式，自动切换成深色按钮 */
                @media (prefers-color-scheme: dark) {{
                    .audio-btn {{
                        background-color: #262730;
                        color: #FAFAFA; /* 纯白文字 */
                        border: 1px solid rgba(250, 250, 250, 0.2);
                    }}
                    .audio-btn:hover {{
                        border-color: #FF4B4B;
                        color: #FF4B4B;
                    }}
                }}
            </style>
            <button class="audio-btn" onclick="var msg = new SpeechSynthesisUtterance('{row['word']}'); msg.lang='en-US'; window.speechSynthesis.speak(msg);">
                🔊 听发音
            </button>
            """
            components.html(html_btn, height=40)

        with col2:
            # 新增：删除按钮
            if st.button("🗑️ 删除", key=f"del_{row['word']}", use_container_width=True):
                delete_word(row["word"])  # 调用删除函数
                st.rerun()  # 强制网页重新加载，立刻刷新列表

        with col3:
            with st.expander("点击查看释义和例句"):
                meaning = row.get("meaning") or "待补充"
                example = row.get("example") or ""
                st.write(f'释义：{meaning}')
                if example:
                    st.write(f'例句：{example}')

        st.caption(f'记录时间：{row["time"]}')

