import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# --- 1. Page Configuration ---
st.set_page_config(page_title="Novel Translator Pro", layout="wide")

# Custom CSS for Font & UI
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Myanmar:wght@400;700&display=swap');
    .stTextArea textarea {
        font-family: 'Noto Sans Myanmar', 'Pyidaungsu', 'Myanmar Text', sans-serif !important;
        font-size: 19px !important;
        line-height: 1.6 !important;
    }
    .stButton button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# Default Instruction
DEFAULT_INST = """သင်သည် မြန်မာစာလုံးပေါင်းသတ်ပုံနှင့် ဝတ္ထုအနှုန်းအဖွဲ့တွင် အထူးကျွမ်းကျင်သော ဘာသာပြန်ဆရာဖြစ်သည်။

စည်းကမ်းချက်များ:
1. 'ခဲ့' ကို လုံးဝ (လုံးဝ) မသုံးရ။
2. '၎င်း၊ ယင်း၊ မူ၊ အကယ်၍၊ သို့မဟုတ်' လုံးဝမသုံးရ။
3. ဇာတ်ကောင်စကားပြောလျှင် 'အပြောဟန်' ကိုသာ သုံးပါ။"""

if "result" not in st.session_state:
    st.session_state.result = ""

# --- 2. Sidebar Settings ---
with st.sidebar:
    st.title("⚙️ Settings")
    api_key = st.text_input("Gemini API Key:", type="password")
    model_name = st.selectbox("Model Version:", ["gemini-2.5-flash", "gemini-2.5-pro"])
    st.markdown("---")
    st.subheader("📝 Instructions")
    user_instruction = st.text_area("AI ကို ပေးမည့် ညွှန်ကြားချက်များ:", value=DEFAULT_INST, height=300)

# --- 3. Main UI ---
st.title("📖 Novel Translator Pro")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Source Text (English)")
    input_text = st.text_area("Paste English here...", height=450)
    
    if st.button("ဘာသာပြန်မည်", type="primary"):
        if not api_key:
            st.warning("Sidebar တွင် API Key ထည့်ပါ။")
        elif not input_text:
            st.error("စာသားထည့်ပါ။")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name=model_name, system_instruction=user_instruction,
                                              generation_config= {
                    "temperature": 0.8, # 0.8 က ဝတ္ထုအတွက် အကောင်းဆုံးပါ
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                }) 
                with st.spinner("ဘာသာပြန်နေပါသည်..."):
                    response = model.generate_content(input_text)
                    st.session_state.result = response.text
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")

with col2:
    st.subheader("Translated Text (Burmese)")
    output_area = st.text_area("Result...", value=st.session_state.result, height=450)
    
    if st.session_state.result:
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            clean_text = st.session_state.result.replace("'", "\\'").replace("\n", "\\n")
            copy_button_html = f"""
            <button onclick="copyToClipboard()" style="width: 100%; background-color: #007bff; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                Copy ကူးမည်
            </button>
            <script>
            function copyToClipboard() {{
                const text = `{clean_text}`;
                navigator.clipboard.writeText(text).then(function() {{
                    alert('စာသားများကို Clipboard ထဲသို့ ကူးယူပြီးပါပြီ!');
                }});
            }}
            </script>
            """
            components.html(copy_button_html, height=50)
            
        with btn_col2:
            st.download_button(
                label="Download (.txt) ဖိုင်သိမ်းမည်",
                data=st.session_state.result,
                file_name="translated_novel.txt",
                mime="text/plain"
            )
