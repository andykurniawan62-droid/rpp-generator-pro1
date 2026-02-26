import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime

# --- KONFIGURASI API ---
GEMINI_API_KEY = "AIzaSyB-nk0E9Laiqg5x6rI7m6tNoqWMLSSDn7Q"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-001')

# --- LOGIKA PEMBATASAN (LIMITER) ---
# Menggunakan session_state untuk simulasi limit per pengguna
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

MAX_FREE_TRIAL = 5

# --- FUNGSI PDF ---
class RPP_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'RENCANA PELAKSANAAN PEMBELAJARAN (RPP)', 0, 1, 'C')
        self.ln(5)

def create_pdf(text, sekolah):
    pdf = RPP_PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    # Membersihkan karakter agar aman di PDF
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    return pdf.output(dest='S')

# --- TAMPILAN ---
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝")

# Header Identitas
st.markdown(f"""
    <div style="background-color:#007BFF;padding:20px;border-radius:10px;text-align:center;">
        <h1 style="color:white;margin:0;">AI RPP GENERATOR PRO</h1>
        <p style="color:white;font-weight:bold;">Karya: ANDY KURNIAWAN (WA: 081338370402)</p>
    </div>
""", unsafe_allow_html=True)

# Cek Kuota
if st.session_state.usage_count >= MAX_FREE_TRIAL:
    st.error("🚫 BATAS PENGGUNAAN GRATIS TERCAPAI")
    st.info("""
        **Daftar Harga Versi Full:**
        * **Versi Full (50x Generate):** Rp 200.000
        * **Versi Full + Pemeliharaan:** Rp 600.000
        
        Hubungi Pak Andy Kurniawan: **081338370402** untuk aktivasi.
    """)
    st.stop()

st.write(f"📊 Sisa kuota gratis Anda: **{MAX_FREE_TRIAL - st.session_state.usage_count}x**")

# --- INPUT PENGGUNA ---
with st.form("form_rpp"):
    st.subheader("🏢 Data Administrasi")
    col1, col2 = st.columns(2)
    with col1:
        nama_sekolah = st.text_input("Nama Sekolah")
        nama_kepsek = st.text_input("Nama Kepala Sekolah")
        nip_kepsek = st.text_input("NIP Kepala Sekolah")
    with col2:
        nama_guru = st.text_input("Nama Guru")
        nip_guru = st.text_input("NIP Guru")
        mapel = st.selectbox("Mata Pelajaran SD", [
            "Pendidikan Agama dan Budi Pekerti", "Pendidikan Pancasila", 
            "Bahasa Indonesia", "Matematika", "IPAS", "Seni Musik", 
            "Seni Rupa", "Seni Teater", "Seni Tari", "PJOK", 
            "Bahasa Inggris", "Muatan Lokal", "PLH", "TIK"
        ])

    st.subheader("📖 Detail Pembelajaran")
    c1, c2, c3 = st.columns(3)
    with c1:
        model_belajar = st.selectbox("Model Pembelajaran", [
            "Problem Based Learning (PBL)", "Project Based Learning (PjBL)", 
            "Discovery Learning", "Inquiry Learning", "Contextual Learning", 
            "Kooperatif (STAD)", "Project Citizen", "Blended Learning", 
            "Flipped Classroom", "Demonstrasi", "Role Playing", 
            "Think Pair Share", "Problem Solving", "Mind Mapping", "Ceramah Plus"
        ])
    with c2:
        fase = st.selectbox("Fase/Kelas/Semester", [
            "Fase A / Kelas 1 / Ganjil", "Fase A / Kelas 1 / Genap",
            "Fase A / Kelas 2 / Ganjil", "Fase A / Kelas 2 / Genap",
            "Fase B / Kelas 3 / Ganjil", "Fase B / Kelas 3 / Genap",
            "Fase B / Kelas 4 / Ganjil", "Fase B / Kelas 4 / Genap",
            "Fase C / Kelas 5 / Ganjil", "Fase C / Kelas 5 / Genap",
            "Fase C / Kelas 6 / Ganjil", "Fase C / Kelas 6 / Genap"
        ])
    with c3:
        jumlah_pertemuan = st.number_input("Jumlah Pertemuan", min_value=1, max_value=15, value=1)

    alokasi = st.text_input("Alokasi Waktu Tiap Pertemuan", placeholder="Contoh: 2 x 35 Menit")
    tanggal = st.text_input("Tanggal Tiap Pertemuan", placeholder="Contoh: 12 Feb, 19 Feb...")
    
    tujuan = st.text_area("Tujuan Pembelajaran")
    materi = st.text_area("Detail Materi Pokok")

    submitted = st.form_submit_button("🚀 GENERATE RPP")

# --- LOGIKA GENERATE ---
if submitted:
    if not nama_sekolah or not mapel or not materi:
        st.warning("Mohon lengkapi data utama (Sekolah, Mapel, Materi)!")
    else:
        try:
            with st.spinner("AI sedang merancang RPP profesional..."):
                prompt = f"""
                Buatlah RPP lengkap untuk SD:
                Sekolah: {nama_sekolah}
                Kepala Sekolah: {nama_kepsek} (NIP: {nip_kepsek})
                Guru: {nama_guru} (NIP: {nip_guru})
                Mata Pelajaran: {mapel}
                Fase/Kelas: {fase}
                Model: {model_belajar}
                Jumlah Pertemuan: {jumlah_pertemuan}
                Alokasi/Pertemuan: {alokasi}
                Tanggal: {tanggal}
                Tujuan: {tujuan}
                Materi: {materi}

                Susun dalam format: Identitas, Kompetensi Inti/Capaian, Tujuan, Materi Lengkap, 
                Langkah Kegiatan (Pendahuluan, Inti, Penutup) per pertemuan, dan Instrumen Penilaian.
                Di bagian akhir, buatkan tempat tanda tangan untuk Kepala Sekolah dan Guru.
                """

                response = model.generate_content(prompt)
                hasil_rpp = response.text
                
                # Update Kuota
                st.session_state.usage_count += 1
                
                st.success("✅ RPP BERHASIL DISUSUN")
                st.markdown(hasil_rpp)
                
                # Fitur PDF
                pdf_data = create_pdf(hasil_rpp, nama_sekolah)
                st.download_button(
                    label="📥 DOWNLOAD SEBAGAI PDF",
                    data=pdf_data,
                    file_name=f"RPP_{mapel}_{nama_sekolah}.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# Footer
st.markdown("---")
st.caption(f"© 2026 AI Generator Pro - Andy Kurniawan. Versi Gratis: {st.session_state.usage_count}/{MAX_FREE_TRIAL}")
