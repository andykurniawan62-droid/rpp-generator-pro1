import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- KONFIGURASI API KEY ---
GEMINI_API_KEY = "AIzaSyB-nk0E9Laiqg5x6rI7m6tNoqWMLSSDn7Q"

# Konfigurasi model Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
    # Gunakan multi_cell untuk teks panjang agar otomatis pindah baris
    pdf.multi_cell(0, 10, txt=text)
    return pdf.output(dest='S')

# --- TAMPILAN APLIKASI ---
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝")

st.title("📝 AI RPP Generator Pro")
st.info("Aplikasi ini akan membuat RPP lengkap berdasarkan materi yang Anda masukkan.")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        mata_pelajaran = st.text_input("Mata Pelajaran", placeholder="Contoh: Biologi")
        kelas = st.text_input("Kelas/Semester", placeholder="Contoh: XI / Genap")
    with col2:
        alokasi_waktu = st.text_input("Alokasi Waktu", placeholder="Contoh: 2 JP (2 x 45 Menit)")
        topik = st.text_input("Topik Utama", placeholder="Contoh: Sistem Pencernaan")

    materi_pokok = st.text_area("Detail Materi / Kompetensi Dasar", 
                                placeholder="Masukkan poin-poin materi yang ingin dibahas...")

# Tombol Generate
if st.button("✨ Buat RPP Sekarang"):
    if not mata_pelajaran or not materi_pokok:
        st.warning("Harap isi Mata Pelajaran dan Detail Materi!")
    else:
        try:
            with st.spinner("🤖 AI sedang menyusun RPP terbaik untuk Anda..."):
                prompt = f"""
                Buatlah Rencana Pelaksanaan Pembelajaran (RPP) Kurikulum Merdeka/K13 yang lengkap:
                Mata Pelajaran: {mata_pelajaran}
                Kelas: {kelas}
                Alokasi Waktu: {alokasi_waktu}
                Topik: {topik}
                Detail Materi: {materi_pokok}
                
                Struktur RPP:
                1. Tujuan Pembelajaran
                2. Langkah Pembelajaran (Pendahuluan, Inti, Penutup)
                3. Media & Sumber Belajar
                4. Jenis Asesmen/Penilaian
                
                Tuliskan dalam format yang rapi dan profesional.
                """
                
                response = model.generate_content(prompt)
                rpp_result = response.text
                
                st.success("✅ RPP Selesai!")
                st.markdown("---")
                st.markdown(rpp_result)
                
                # Opsi Download PDF
                pdf_bytes = create_pdf(rpp_result.encode('latin-1', 'ignore').decode('latin-1'))
                
                st.download_button(
                    label="📥 Unduh RPP sebagai PDF",
                    data=pdf_bytes,
                    file_name=f"RPP_{mata_pelajaran}_{topik}.pdf",
                    mime="application/pdf"
                )
                
        except Exception as e:
            st.error(f"Gagal generate: {e}")

st.markdown("---")
st.caption("Powered by Gemini AI • 2026")
