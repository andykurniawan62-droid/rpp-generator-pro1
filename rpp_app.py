import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- AMBIL API KEY DARI SISTEM KEAMANAN (SECRETS) ---
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-001')
else:
    st.error("⚠️ API Key tidak ditemukan! Silakan masukkan di Settings > Secrets.")
    st.stop()

# --- LOGIKA PEMBATASAN ---
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
    st.info(f"Hubungi Pak Andy Kurniawan: **081338370402** untuk aktivasi versi FULL.")
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
    fase = st.text_input("Fase/Kelas/Semester", value="Fase B / Kelas 4 / Ganjil")
    jml_pertemuan = st.number_input("Jumlah Pertemuan (1-15)", min_value=1, max_value=15, value=1)
    
    data_pertemuan = []
    list_model = ["PBL", "PjBL", "Discovery Learning", "Inquiry Learning", "Contextual", "STAD", "Demonstrasi", "Mind Mapping"]

    for i in range(int(jml_pertemuan)):
        with st.expander(f"📍 Konfigurasi Pertemuan Ke-{i+1}", expanded=(i==0)):
            c1, c2, c3 = st.columns([2,1,1])
            with c1:
                m = st.selectbox(f"Model P{i+1}", list_model, key=f"m_{i}")
            with c2:
                w = st.text_input(f"Waktu P{i+1}", value="2x35 Menit", key=f"w_{i}")
            with c3:
                t = st.text_input(f"Tanggal P{i+1}", placeholder="Tgl-Bln-Thn", key=f"t_{i}")
            data_pertemuan.append({"no": i+1, "model": m, "waktu": w, "tgl": t})
    
    st.markdown("---")
    tujuan = st.text_area("Tujuan Pembelajaran Umum")
    materi = st.text_area("Detail Materi Pokok (KD/CP)")

    submitted = st.form_submit_button("🚀 GENERATE RPP")

if submitted:
    if not nama_sekolah or not materi:
        st.warning("Mohon isi Nama Sekolah dan Detail Materi!")
    else:
        try:
            with st.spinner("AI sedang memproses RPP..."):
                jadwal_str = ""
                for p in data_pertemuan:
                    jadwal_str += f"- Pertemuan {p['no']}: Model {p['model']}, Waktu {p['waktu']}, Tanggal {p['tgl']}\n"

                prompt = f"""
                Buatlah RPP profesional untuk SD:
                Sekolah: {nama_sekolah} | Guru: {nama_guru} | Kepsek: {nama_kepsek}
                Mapel: {mapel} | Kelas: {fase}
                JADWAL PERTEMUAN ({jml_pertemuan} Kali): {jadwal_str}
                Materi Pokok: {materi} | Tujuan Umum: {tujuan}
                Sertakan langkah pembelajaran detail per pertemuan dan instrumen penilaian.
                """
                response = model.generate_content(prompt)
                st.session_state.usage_count += 1
                st.success(f"✅ BERHASIL! (Sisa Kuota: {MAX_FREE_TRIAL - st.session_state.usage_count})")
                st.markdown(response.text)
                
                pdf_bytes = create_pdf(response.text)
                st.download_button(label="📥 DOWNLOAD SEBAGAI PDF", data=pdf_bytes, file_name=f"RPP_{mapel}.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Terjadi Kendala: {e}")

st.markdown("---")
st.caption(f"© 2026 AI Generator Pro - Andy Kurniawan")
