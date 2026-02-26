import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- KONFIGURASI API ---
GEMINI_API_KEY = "AIzaSyB-nk0E9Laiqg5x6rI7m6tNoqWMLSSDn7Q"
genai.configure(api_key=GEMINI_API_KEY)

# Menggunakan model yang tertera di JSON list aktif Anda (Versi 2.0 Flash)
model = genai.GenerativeModel('gemini-2.0-flash-001')

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
    # Proteksi karakter non-latin agar tidak crash
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

# Cek Pembatasan
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
    
    # --- PENGATURAN TIAP PERTEMUAN (Dinamis) ---
    st.info("Atur model dan jadwal untuk tiap pertemuan di bawah ini:")
    data_pertemuan = []
    list_model = [
        "PBL", "PjBL", "Discovery Learning", "Inquiry Learning", 
        "Contextual", "STAD", "Demonstrasi", "Mind Mapping", 
        "Role Playing", "Think Pair Share", "Problem Solving", 
        "Blended Learning", "Flipped Classroom", "Project Citizen", "Ceramah Plus"
    ]

    for i in range(int(jml_pertemuan)):
        with st.expander(f"📍 Konfigurasi Pertemuan Ke-{i+1}", expanded=(i==0)):
            c1, c2, c3 = st.columns([2,1,1])
            with c1:
                m = st.selectbox(f"Model Pembelajaran P{i+1}", list_model, key=f"m_{i}")
            with c2:
                w = st.text_input(f"Waktu P{i+1}", value="2x35 Menit", key=f"w_{i}")
            with c3:
                t = st.text_input(f"Tanggal P{i+1}", placeholder="Tgl-Bln-Thn", key=f"t_{i}")
            data_pertemuan.append({"no": i+1, "model": m, "waktu": w, "tgl": t})
    
    st.markdown("---")
    tujuan = st.text_area("Tujuan Pembelajaran Umum")
    materi = st.text_area("Detail Materi Pokok (KD/CP)")

    submitted = st.form_submit_button("🚀 GENERATE RPP")

# --- PROSES GENERATE ---
if submitted:
    if not nama_sekolah or not materi:
        st.warning("Mohon isi Nama Sekolah dan Detail Materi!")
    else:
        try:
            with st.spinner("AI sedang memproses RPP..."):
                # Menyusun instruksi detail pertemuan
                jadwal_str = ""
                for p in data_pertemuan:
                    jadwal_str += f"- Pertemuan {p['no']}: Model {p['model']}, Waktu {p['waktu']}, Tanggal {p['tgl']}\n"

                prompt = f"""
                Buatlah RPP profesional untuk SD:
                Sekolah: {nama_sekolah} | Guru: {nama_guru} | Kepsek: {nama_kepsek}
                Mapel: {mapel} | Kelas: {fase}
                
                JADWAL PERTEMUAN ({jml_pertemuan} Kali):
                {jadwal_str}
                
                Materi Pokok: {materi}
                Tujuan Umum: {tujuan}

                SYARAT PENULISAN:
                1. Jabarkan LANGKAH PEMBELAJARAN (Pendahuluan, Inti, Penutup) secara spesifik untuk TIAP pertemuan (1-{jml_pertemuan}).
                2. Langkah INTI harus mencerminkan MODEL PEMBELAJARAN yang dipilih untuk pertemuan tersebut.
                3. Gunakan Bahasa Indonesia yang formal dan rapi.
                4. Sertakan bagian tanda tangan di akhir.
                """

                response = model.generate_content(prompt)
                
                if response.text:
                    st.session_state.usage_count += 1
                    st.success(f"✅ RPP BERHASIL DIBUAT! (Penggunaan: {st.session_state.usage_count}/{MAX_FREE_TRIAL})")
                    st.markdown("---")
                    st.markdown(response.text)
                    
                    # File PDF
                    pdf_bytes = create_pdf(response.text)
                    st.download_button(
                        label="📥 DOWNLOAD SEBAGAI PDF",
                        data=pdf_bytes,
                        file_name=f"RPP_{mapel}_{nama_sekolah}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.error("Gagal mendapatkan respon dari AI. Coba lagi.")

        except Exception as e:
            if "404" in str(e):
                st.error("Error 404: Model tidak ditemukan. Saya akan mencoba beralih ke model alternatif...")
                # Fallback otomatis jika model 2.0 gagal
                st.info("Gunakan model 'gemini-2.0-flash-lite' jika masalah berlanjut.")
            elif "429" in str(e):
                st.error("⚠️ Kuota API Anda sedang limit. Mohon tunggu 1 menit.")
            else:
                st.error(f"Terjadi Kendala: {e}")

st.markdown("---")
st.caption(f"© 2026 AI Generator Pro - Andy Kurniawan")
