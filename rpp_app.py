import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- KONFIGURASI API ---
GEMINI_API_KEY = "AIzaSyB-nk0E9Laiqg5x6rI7m6tNoqWMLSSDn7Q"
genai.configure(api_key=GEMINI_API_KEY)

# Menggunakan 1.5 Flash karena kuota 2.0 Anda sedang penuh/limit
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# --- LOGIKA PEMBATASAN (SESSION BASED) ---
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

MAX_FREE_TRIAL = 5

# --- FUNGSI PDF ---
class RPP_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'RENCANA PELAKSANAAN PEMBELAJARAN (RPP)', 0, 1, 'C')
        self.ln(5)

def create_pdf(text):
    pdf = RPP_PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    return pdf.output(dest='S')

# --- TAMPILAN ---
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝")

st.markdown(f"""
    <div style="background-color:#007BFF;padding:20px;border-radius:10px;text-align:center;margin-bottom:20px;">
        <h1 style="color:white;margin:0;">AI RPP GENERATOR PRO</h1>
        <p style="color:white;font-weight:bold;margin:5px;">Karya: ANDY KURNIAWAN (WA: 081338370402)</p>
    </div>
""", unsafe_allow_html=True)

if st.session_state.usage_count >= MAX_FREE_TRIAL:
    st.error("🚫 BATAS PENGGUNAAN GRATIS TERCAPAI")
    st.info("""
        **Daftar Harga Versi Full:**
        * **Versi Full (50x Generate):** Rp 200.000
        * **Versi Full + Pemeliharaan:** Rp 600.000
        
        Hubungi Pak Andy Kurniawan: **081338370402** untuk aktivasi.
    """)
    st.stop()

# --- FORM INPUT ---
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
            "Pendidikan Agama", "Pendidikan Pancasila", "Bahasa Indonesia", 
            "Matematika", "IPAS", "Seni Musik", "Seni Rupa", "PJOK", "Bahasa Inggris"
        ])

    st.subheader("📖 Detail Pembelajaran")
    c1, c2, c3 = st.columns(3)
    with c1:
        model_belajar = st.selectbox("Model Pembelajaran", [
            "PBL", "PjBL", "Discovery Learning", "Inquiry", "Contextual", "STAD", "Demonstrasi", "Mind Mapping"
        ])
    with c2:
        fase = st.text_input("Fase/Kelas/Semester", value="Fase B / Kelas 4 / Ganjil")
    with c3:
        # Permintaan: Maksimal 15 pertemuan
        jml_pertemuan = st.slider("Jumlah Pertemuan", 1, 15, 1)

    alokasi = st.text_input("Alokasi Waktu per Pertemuan (Contoh: 2x35 Menit)")
    tanggal = st.text_area("Tanggal tiap Pertemuan (Pisahkan dengan koma)")
    
    tujuan = st.text_area("Tujuan Pembelajaran")
    materi = st.text_area("Detail Materi Pokok")

    submitted = st.form_submit_button("🚀 GENERATE RPP")

if submitted:
    if not nama_sekolah or not materi:
        st.warning("Data sekolah dan materi wajib diisi!")
    else:
        try:
            with st.spinner("Menghubungi AI (Mohon tunggu, kuota gratis terbatas)..."):
                # PROMPT DIPERTEGAS UNTUK JUMLAH PERTEMUAN
                prompt = f"""
                Buatlah RPP lengkap sesuai identitas berikut:
                Sekolah: {nama_sekolah} | Guru: {nama_guru} | Kepsek: {nama_kepsek}
                Mapel: {mapel} | Kelas: {fase} | Model: {model_belajar}
                Alokasi Waktu: {alokasi} | Tanggal: {tanggal}

                INSTRUKSI KHUSUS:
                1. Buat RPP ini untuk TEPAT {jml_pertemuan} kali pertemuan.
                2. Untuk SETIAP pertemuan (Pertemuan 1 sampai {jml_pertemuan}), tuliskan secara terpisah:
                   - Tujuan Spesifik Pertemuan tersebut
                   - Langkah Pendahuluan, Inti, dan Penutup secara mendalam.
                3. Materi Pokok: {materi}
                4. Tujuan Umum: {tujuan}
                5. Sertakan instrumen penilaian di bagian akhir.
                """

                response = model.generate_content(prompt)
                
                st.session_state.usage_count += 1
                st.success(f"✅ RPP Berhasil Dibuat! (Penggunaan: {st.session_state.usage_count}/{MAX_FREE_TRIAL})")
                
                st.markdown("---")
                st.markdown(response.text)
                
                # Tombol PDF
                pdf_output = create_pdf(response.text)
                st.download_button(
                    label="📥 DOWNLOAD SEBAGAI PDF",
                    data=pdf_output,
                    file_name=f"RPP_{mapel}_{jml_pertemuan}_Pertemuan.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            if "429" in str(e):
                st.error("⚠️ KUOTA API GOOGLE HABIS (LIMIT).")
                st.info("Akun gratis Google memiliki batas limit. Silakan tunggu 1-2 menit atau coba lagi besok. Jika ingin lancar tanpa gangguan limit, disarankan beralih ke API Key berbayar.")
            else:
                st.error(f"Terjadi kesalahan: {e}")

st.markdown("---")
st.caption(f"© 2026 AI Generator Pro - Andy Kurniawan. Sisa Sesi: {MAX_FREE_TRIAL - st.session_state.usage_count}")
