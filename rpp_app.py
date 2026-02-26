import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- KONFIGURASI API KEY ---
GEMINI_API_KEY = "AIzaSyB-nk0E9Laiqg5x6rI7m6tNoqWMLSSDn7Q"

# Konfigurasi model Gemini dengan versi terbaru yang lebih stabil
genai.configure(api_key=GEMINI_API_KEY)
# Menggunakan 'gemini-1.5-flash-latest' untuk menghindari error 404
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- FUNGSI GENERATE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'RENCANA PELAKSANAAN PEMBELAJARAN (RPP)', 0, 1, 'C')
        self.ln(5)

def create_pdf(text):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Membersihkan karakter non-latin1 agar tidak error saat buat PDF
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S')

# --- TAMPILAN APLIKASI ---
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝")

st.title("📝 AI RPP Generator Pro")
st.info("Masukkan detail pembelajaran di bawah ini untuk membuat RPP otomatis.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        mata_pelajaran = st.text_input("Mata Pelajaran", placeholder="Contoh: Fisika")
        kelas = st.text_input("Kelas/Semester", placeholder="Contoh: XII / Ganjil")
    with col2:
        alokasi_waktu = st.text_input("Alokasi Waktu", placeholder="Contoh: 2 JP")
        topik = st.text_input("Topik Utama", placeholder="Contoh: Hukum Newton")

    materi_pokok = st.text_area("Detail Materi atau Tujuan Khusus", 
                                placeholder="Tuliskan materi atau KD yang ingin dimasukkan...")

# Tombol Generate
if st.button("✨ Buat RPP Sekarang"):
    if not mata_pelajaran or not materi_pokok:
        st.warning("Harap isi setidaknya Mata Pelajaran dan Detail Materi!")
    else:
        try:
            with st.spinner("🤖 Sedang menghubungi AI..."):
                prompt = f"""
                Buatlah Rencana Pelaksanaan Pembelajaran (RPP) yang rapi:
                Mata Pelajaran: {mata_pelajaran}
                Kelas: {kelas}
                Alokasi Waktu: {alokasi_waktu}
                Topik: {topik}
                Detail: {materi_pokok}
                
                Format: Identitas, Tujuan, Langkah-langkah (Pendahuluan, Inti, Penutup), dan Penilaian.
                """
                
                response = model.generate_content(prompt)
                
                if response.text:
                    st.success("✅ RPP Berhasil Dibuat!")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    # Generate PDF
                    pdf_output = create_pdf(response.text)
                    
                    st.download_button(
                        label="📥 Unduh RPP sebagai PDF",
                        data=pdf_output,
                        file_name=f"RPP_{mata_pelajaran}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("AI memberikan jawaban kosong. Coba lagi.")
                
        except Exception as e:
            st.error(f"Terjadi Kendala: {str(e)}")
            st.info("Tips: Pastikan koneksi internet stabil dan API Key masih berlaku.")

st.markdown("---")
st.caption("AI RPP Generator • 2026")
