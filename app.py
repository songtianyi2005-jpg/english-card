import csv
import os
import datetime
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL"))
key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY"))
supabase = create_client(url, key)

today = datetime.date.today().isoformat()

# 判断是否在云端运行
IS_CLOUD = os.environ.get("HOME") == "/home/appuser"  # 这是 Streamlit 云端的默认路径

st.set_page_config(layout="wide")

FILE = "words.csv"
st.title("宋国强的单词卡片")

def delete_word(target_word):
    supabase.table("words").delete().eq("word", target_word).execute()

def update_memory(target_word, success):
    # 先从云端查这个词
    res = supabase.table("words").select("*").eq("word", target_word).execute()
    if not res.data:
        return
    row = res.data[0]

    current_interval = int(row.get("interval") or 1)
    new_interval = current_interval * 2 if success else 1

    import datetime
    next_date = (datetime.date.today() + datetime.timedelta(days=new_interval)).isoformat()

    # 更新云端数据
    supabase.table("words").update({
        "interval": new_interval,
        "next_review": next_date
    }).eq("word", target_word).execute()

    # 从云端查数据
response = supabase.table("words").select("*").execute()
rows = response.data
review_words = []
for row in rows:
    next_review = row["next_review"]
    if next_review <= today:
        review_words.append(row)

if len(review_words) == 0:
    st.balloons()
    st.success("🎉 太棒了！今天的单词都复习完了！明天再来吧。")
    st.stop()

st.info(f'今天还有{len(review_words)}个单词需要复习。')

st.write(f'共收集了{len(rows)}个单词')

for row in review_words:
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
            # 如果在云端，显示下载按钮；如果在本地，显示删除按钮
            if IS_CLOUD:
                st.caption("云端暂不支持直接删除")
            else:
                if st.button("🗑️ 删除", key=f"del_{row['word']}", use_container_width=True):
                    delete_word(row["word"])
                    st.rerun()

        with col3:
            with st.expander("点击查看释义和例句"):
                meaning = row.get("meaning") or "待补充"
                example = row.get("example") or ""
                st.write(f'释义：{meaning}')
                if example:
                    st.write(f'例句：{example}')

        st.write("---")
        col_a, col_b = st.columns(2)
        if col_a.button("❌ 忘记了", key=f"forget_{row['word']}", use_container_width=True):
            update_memory(row["word"], success=False)
            st.rerun()

        if col_b.button("✅ 记住了", key=f"know_{row['word']}", use_container_width=True):
            update_memory(row["word"], success=True)
            st.rerun()

        st.caption(f'记录时间：{row["time"]}')

