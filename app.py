import streamlit as st
from fpdf import FPDF
import time

st.set_page_config(page_title="Matematika Milliy Sertifikat Testi", page_icon="🧮", layout="centered")

st.title("🧮 Matematika fanidan Milliy Sertifikat Test Tizimi")
st.write("O'quvchilar bilimini baholash va sertifikatlash platformasi.")

# 1. O'quvchi ma'lumotlari
st.subheader("👤 O'quvchi ma'lumotlari")
student_name = st.text_input("Ism va familiyangizni kiriting:", placeholder="Masalan: Ali Valiyev")

if not student_name:
    st.warning("⚠️ Testni boshlash uchun iltimos ism-familiyangizni kiriting.")
    st.stop()

# ⏱️ TEST VAQTI (Bu yerga test necha daqiqa bo'lishini yozing. Masalan: 60 daqiqa)
TEST_DAQIQA = 60  
TOTAL_TIME = TEST_DAQIQA * 60 

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

elapsed_time = time.time() - st.session_state.start_time
remaining_time = max(0, int(TOTAL_TIME - elapsed_time))

mins, secs = divmod(remaining_time, 60)
st.info(f"⏱️ Qolgan vaqt: {mins:02d}:{secs:02d}")

if remaining_time == 0:
    st.error("🚨 Vaqt tugadi! Test avtomatik yakunlanadi.")

st.divider()

# =========================================================================
# ✍️ O'QITUVCHI DIQQATIGA: SAVOLLARINGIZNI SHU YERGA ODDIY MATN DEK COPY-PASTE QILING!
# Format: Savol | Variant1, Variant2, Variant3, Variant4 | To'g'ri javob
# Ochiq test bo'lsa variantlar o'rniga "ochiq" deb yozing.
# =========================================================================
SAVOLLAR_MATNI = """
Quyidagi kvadrat tenglamaning ildizlari yig'indisini toping: $x^2 - 7x + 12 = 0$ | 5, 7, 12, -7 | 7
Agar $\log_2 x = 5$ bo'lsa, $x$ ning qiymatini toping. | 10, 25, 32, 64 | 32
Ochiq test: $\int_0^2 3x^2 dx$ aniq integralni hisoblang. | ochiq | 8
Uchburchakning ichki burchaklari yig'indisini toping. | 90, 180, 270, 360 | 180
5-savol matnini shu yerga yozing | variant1, variant2, variant3, variant4 | variant2
"""
# =========================================================================

# Matnni avtomatik savollarga ajratish (Kodni o'zgartirmang)
questions = []
for idx, line in enumerate(SAVOLLAR_MATNI.strip().split('\n'), 1):
    parts = line.split('|')
    if len(parts) == 3:
        q_text = parts[0].strip()
        opts = [o.strip() for o in parts[1].split(',')]
        ans = parts[2].strip()
        
        if parts[1].strip().lower() == "ochiq":
            questions.append({"id": idx, "type": "open", "question": q_text, "correct": ans})
        else:
            questions.append({"id": idx, "type": "choice", "question": q_text, "options": opts, "correct": ans})

user_answers = {}

# Savollarni ekranga chiqarish
for q in questions:
    st.markdown(f"### Savol {q['id']}:")
    st.markdown(q['question'])
    
    if q['type'] == "choice":
        user_answers[q['id']] = st.radio("Javobni tanlang:", q['options'], key=f"q_{q['id']}", index=None)
    elif q['type'] == "open":
        user_answers[q['id']] = st.text_input("Javobingizni yozing:", key=f"q_{q['id']}").strip()
        
    st.divider()

# PDF Sertifikat yaratish funksiyasi
def generate_pdf(name, score, percent, level):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_line_width(5)
    pdf.set_draw_color(0, 102, 204)
    pdf.rect(10, 10, 277, 190)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 40, "MILLIY SERTIFIKAT", ln=True, align="C")
    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(51, 51, 51)
    pdf.cell(0, 15, "Ushbu sertifikat matematika fanidan muvaffaqiyatli o'tgan o'quvchiga beriladi:", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 25, name.upper(), ln=True, align="C")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(51, 51, 60)
    pdf.cell(0, 15, f"To'plagan bali: {score} / {len(questions)} ({percent:.1f}%)", ln=True, align="C")
    pdf.cell(0, 15, f"Berilgan Daraja: {level}", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 12)
    pdf.cell(0, 30, f"Sana: 22.10.2026", ln=True, align="C")
    return bytes(pdf.output())

# 4. Natijalarni hisoblash
if st.button("📝 Testni yakunlash va natijani ko'rish", type="primary") or remaining_time == 0:
    correct_count = 0
    total_questions = len(questions)
    
    st.markdown("## 📊 Natijalar:")
    for q in questions:
        u_ans = user_answers.get(q['id'])
        c_ans = q['correct']
        if str(u_ans) == str(c_ans):
            correct_count += 1
            st.success(f"✅ **Savol {q['id']}: To'g'ri!**")
        else:
            st.error(f"❌ **Savol {q['id']}: Noto'g'ri.** (To'g'ri javob: {c_ans})")
            
    percentage = (correct_count / total_questions) * 100
    st.metric(label="Umumiy ball", value=f"{correct_count} / {total_questions}", delta=f"{percentage:.1f}%")
    
    level = None
    if percentage >= 86:
        st.balloons()
        level = "A daraja (Oliy)"
    elif percentage >= 70:
        level = "B daraja (O'rta)"
        
    if level:
        st.success(f"🎉 Tabriklaymiz! Siz **{level}** sertifikatini qo'lga kiritdingiz!")
        pdf_bytes = generate_pdf(student_name, correct_count, percentage, level)
        st.download_button(
            label="📥 Rasmiy Sertifikatni PDF formatida yuklab olish",
            data=pdf_bytes,
            file_name=f"Sertifikat_{student_name}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("🔄 Afsuski, sertifikat olish uchun ball yetarli bo'lmadi (Kamida 70% kerak).")
