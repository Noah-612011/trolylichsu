import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components
from openai import OpenAI

# ======================
# 🌐 KẾT NỐI OPENAI
# ======================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ======================
# ⚙️ CẤU HÌNH TRANG
# ======================
st.set_page_config(page_title="Trợ lý Lịch sử Việt Nam", layout="centered")

# ======================
# 🧠 TRẠNG THÁI
# ======================
if "audio_unlocked" not in st.session_state:
    st.session_state["audio_unlocked"] = False

st.title("📚 TRỢ LÝ LỊCH SỬ VIỆT NAM (AI)")
st.write("👉 Bấm *BẬT ÂM THANH*, sau đó nhập câu hỏi rồi bấm *Trả lời*.")

# ======================
# 🔓 NÚT BẬT ÂM THANH
# ======================
if st.button("🔊 BẬT ÂM THANH (1 lần)"):
    js = """
    <script>
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            if (ctx.state === 'suspended') ctx.resume();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            gain.gain.value = 0;
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.05);
        } catch(e) {}
    </script>
    """
    components.html(js, height=0)
    st.session_state["audio_unlocked"] = True
    st.success("Âm thanh đã mở khoá!")

# ======================
# 🎓 HÀM TRẢ LỜI LỊCH SỬ BẰNG AI
# ======================
def tra_loi_AI(cau_hoi: str):
    prompt_system = """
    Bạn là trợ lý lịch sử Việt Nam. Trả lời chính xác, dễ hiểu, đầy đủ,
    không bịa, chỉ dựa trên dữ kiện lịch sử thật.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": cau_hoi}
        ],
        max_tokens=300
    )

    return response.choices[0].message.content

# ======================
# 💬 GIAO DIỆN
# ======================
cau_hoi = st.text_input("❓ Nhập câu hỏi lịch sử:")

if st.button("📖 Trả lời"):
    if not cau_hoi.strip():
        st.warning("Bạn chưa nhập câu hỏi!")
        st.stop()

    tra_loi = tra_loi_AI(cau_hoi)
    st.success(tra_loi)

    # Tạo giọng nói
    try:
        mp3_fp = BytesIO()
        gTTS(text=tra_loi, lang="vi").write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_b64 = base64.b64encode(mp3_fp.read()).decode()
    except:
        st.error("Lỗi tạo giọng nói.")
        audio_b64 = None

    # Phát audio
    if audio_b64:
        unlocked = "true" if st.session_state["audio_unlocked"] else "false"

        audio_html = f"""
        <div id="tts"></div>
        <script>
          (function(){{
            const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent);
            const unlocked = {unlocked};
            const audio = document.createElement('audio');
            audio.src = "data:audio/mp3;base64,{audio_b64}";
            audio.controls = true;
            audio.playsInline = true;
            document.getElementById("tts").appendChild(audio);

            if (!isIOS && unlocked) {{
                audio.autoplay = true;
                audio.play().catch(()=>{{}});
            }}
          }})();
        </script>
        """

        components.html(audio_html, height=120)
