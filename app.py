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

# 2. Vaqt taymeri (Masalan: 5 daqiqa = 300 soniya)
# Agarda haqiqiy imtihon vaqtini qo'ymoqchi bo'lsangiz, soniyani ko'paytiring (Masalan, 180 daqiqa = 10800 soniya)
TOTAL_TIME = 300 

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()

elapsed_time = time.time() - st.session_state.start_time
remaining_time = max(0, int(TOTAL_TIME - elapsed_time))

mins, secs = divmod(remaining_time, 60)
timer_text = f"⏱️ Qolgan vaqt: {mins:02d}:{secs:02d}"

if remaining_time == 0:
    st.error("🚨 Vaqt tugadi! Test avtomatik yakunlanadi.")
else:
    st.info(timer_text)

st.divider()

# 3. O'qituvchi uchun savollar bazasi (Shu yerdan savollarni o'zgartirishingiz mumkin)
questions = [
    {
        "id": 1,
        "type": "choice",
        "question": "Quyidagi kvadrat tenglamaning ildizlari yig'indisini toping: $x^2 - 7x + 12 = 0$",
        "options": ["5", "7", "12", "-7"],
        "correct": "7"
    },
    {
        "id": 2,
        "type": "choice",
        "question": "Agar $\\log_2 x = 5$ bo'lsa, $x$ ning qiymatini toping.",
        "options": ["10", "25", "32", "64"],
        "correct": "32"
    },
    {
        "id": 3,
        "type": "open",
        "question": "Ochiq test (Javobni son shaklida yozing): $\\int_0^2 3x^2 dx$ aniq integralni hisoblang.",
        "correct": "8"
    }
]

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

# PDF Sertifikat yaratish funksiyasi (Xatosiz variant)
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
    pdf.cell(0, 30, "Sana: 22.10.2026", ln=True, align="C")
    
    # Ma'lumotni to'g'ri bayt ko'rinishida qaytarish
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
