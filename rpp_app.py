import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- KONFIGURASI API KEY DARI SECRETS ---
# Pastikan Anda sudah memasukkan GEMINI_API_KEY di dashboard Streamlit (Settings > Secrets)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("⚠️ API Key tidak ditemukan! Masukkan API Key di 'Settings > Secrets' pada Dashboard Streamlit.")
    st.stop()

# --- LOGIKA PEMBATASAN PENGGUNA (SESSION BASED) ---
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

MAX_FREE_TRIAL = 5

# --- FUNGSI GENERATE PDF ---
class RPP_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'RENCANA PELAKSANAAN PEMBELAJARAN (RPP)', 0, 1, 'C')
        self.ln(5)

def create_pdf(text):
    pdf = RPP_PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    # Membersihkan karakter non-latin1 agar PDF tidak error/crash
    clean_text = text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    return pdf.output(dest='S')

# --- TAMPILAN APLIKASI ---
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝", layout="centered")

# Header Identitas Pembuat
st.markdown(f"""
    <div style="background-color:#007BFF;padding:20px;border-radius:10px;text-align:center;margin-bottom:20px;">
        <h1 style="color:white;margin:0;">AI RPP GENERATOR PRO</h1>
        <p style="color:white;font-weight:bold;margin:5px;">Karya: ANDY KURNIAWAN (WA: 081338370402)</p>
    </div>
""", unsafe_allow_html=True)

# Cek Pembatasan Kuota Gratis
if st.session_state.usage_count >= MAX_FREE_TRIAL:
    st.error("🚫 BATAS PENGGUNAAN GRATIS TERCAPAI")
    st.markdown(f"""
    <div style="background-color:#fff3cd; padding:15px; border-left: 5px solid #ffa000; border-radius: 5px;">
        <h3 style="color:#856404; margin-top:0;">Daftar Harga Versi Full:</h3>
        <ul style="color:#856404;">
            <li><b>Versi Full (50x Generate):</b> Rp 200.000</li>
            <li><b>Versi Full + Pemeliharaan:</b> Rp 600.000</li>
        </ul>
        <p style="color:#856404; font-weight:bold;">Hubungi Andy Kurniawan: 081338370402 untuk Aktivasi</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# --- FORM INPUT PENGGUNA ---
with st.form("main_form"):
    st.subheader("🏢 Data Administrasi Sekolah")
    col1, col2 = st.columns(2)
    with col1:
        nama_sekolah = st.text_input("Nama Sekolah", placeholder="SD Negeri ...")
        nama_kepsek = st.text_input("Nama Kepala Sekolah")
        nip_kepsek = st.text_input("NIP Kepala Sekolah")
    with col2:
        nama_guru = st.text_input("Nama Guru")
        nip_guru = st.text_input("NIP Guru")
        mapel = st.selectbox("Mata Pelajaran", [
            "Pendidikan Agama", "Pendidikan Pancasila", "Bahasa Indonesia", 
            "Matematika", "IPAS", "Seni Musik", "Seni Rupa", "Seni Teater", 
            "Seni Tari", "PJOK", "Bahasa Inggris", "Muatan Lokal"
        ])

    st.subheader("📖 Detail Pembelajaran")
    fase = st.text_input("Fase/Kelas/Semester", value="Fase B / Kelas 4 / Ganjil")
    jml_pertemuan = st.number_input("Jumlah Pertemuan (Maksimal 15)", min_value=1, max_value=15, value=1)
    
    # Form Dinamis Tiap Pertemuan
    st.info("Atur detail Model, Waktu, dan Tanggal untuk tiap pertemuan:")
    data_pertemuan = []
    list_model = [
        "PBL (Problem Based Learning)", "PjBL (Project Based Learning)", 
        "Discovery Learning", "Inquiry Learning", "Contextual Learning", 
        "STAD", "Demonstrasi", "Mind Mapping", "Role Playing", 
        "Think Pair Share", "Problem Solving", "Blended Learning", 
        "Flipped Classroom", "Project Citizen", "Ceramah Plus"
    ]

    for i in range(int(jml_pertemuan)):
        with st.expander(f"📍 Konfigurasi Pertemuan Ke-{i+1}", expanded=(i==0)):
            c1, c2, c3 = st.columns([2,1,1])
            with c1:
                m = st.selectbox(f"Model P{i+1}", list_model, key=f"m_{i}")
            with c2:
                w = st.text_input(f"Waktu P{i+1}", value="2x35 Menit", key=f"w_{i}")
            with c3:
                t = st.text_input(f"Tanggal P{i+1}", placeholder="DD-MM-YYYY", key=f"t_{i}")
            data_pertemuan.append({"no": i+1, "model": m, "waktu": w, "tgl": t})

    tujuan_umum = st.text_area("Tujuan Pembelajaran Umum")
    materi_pokok = st.text_area("Detail Materi Pokok (KD/CP)")

    btn_generate = st.form_submit_button("🚀 GENERATE RPP SEKARANG")

# --- PROSES GENERATE OLEH AI ---
if btn_generate:
    if not nama_sekolah or not materi_pokok:
        st.warning("Mohon lengkapi Nama Sekolah dan Detail Materi!")
    else:
        # Daftar model Fallback (Mencoba 2.0 Flash, jika limit coba 2.0 Flash Lite)
        model_options = ['gemini-2.0-flash-001', 'gemini-2.0-flash-lite-001']
        success = False

        for model_name in model_options:
            try:
                with st.spinner(f"Sedang menyusun RPP menggunakan {model_name}..."):
                    current_model = genai.GenerativeModel(model_name)
                    
                    # Menyusun rincian jadwal untuk prompt
                    jadwal_detail = ""
                    for p in data_pertemuan:
                        jadwal_detail += f"- Pertemuan {p['no']}: Model {p['model']}, Alokasi Waktu {p['waktu']}, Tanggal {p['tgl']}\n"

                    prompt = f"""
                    Buatlah Rencana Pelaksanaan Pembelajaran (RPP) profesional dengan data:
                    Nama Sekolah: {nama_sekolah}
                    Kepala Sekolah: {nama_kepsek} (NIP: {nip_kepsek})
                    Guru: {nama_guru} (NIP: {nip_guru})
                    Mapel: {mapel} | Kelas: {fase}
                    
                    RINCIAN PERTEMUAN ({jml_pertemuan} kali):
                    {jadwal_detail}
                    
                    Tujuan Umum: {tujuan_umum}
                    Materi Pokok: {materi_pokok}

                    SYARAT PENULISAN:
                    1. Jabarkan Tujuan Khusus dan Langkah Pembelajaran (Pendahuluan, Inti, Penutup) secara spesifik untuk TIAP pertemuan.
                    2. Langkah INTI harus sesuai dengan Model Pembelajaran yang dipilih pada pertemuan tersebut.
                    3. Berikan bagian Instrumen Penilaian di akhir.
                    4. Gunakan format yang rapi dan bahasa Indonesia formal.
                    """

                    response = current_model.generate_content(prompt)
                    
                    if response.text:
                        st.session_state.usage_count += 1
                        st.success(f"✅ RPP Berhasil Dibuat! (Sisa Kuota Gratis: {MAX_FREE_TRIAL - st.session_state.usage_count})")
                        st.markdown("---")
                        st.markdown(response.text)
                        
                        # Tombol Download PDF
                        pdf_bytes = create_pdf(response.text)
                        st.download_button(
                            label="📥 DOWNLOAD SEBAGAI PDF",
                            data=pdf_bytes,
                            file_name=f"RPP_{mapel}_{nama_sekolah}.pdf",
                            mime="application/pdf"
                        )
                        success = True
                        break # Keluar dari loop jika berhasil
            
            except Exception as e:
                if "429" in str(e):
                    st.warning(f"Jalur {model_name} sedang penuh. Mencoba jalur cadangan...")
                    continue
                else:
                    st.error(f"Terjadi kesalahan teknis: {e}")
                    break

        if not success:
            st.error("⚠️ Semua jalur kuota AI Google sedang limit.")
            st.info("Saran: Tunggu sekitar 1 menit agar kuota reset, lalu klik kembali tombol Generate.")

# Footer Akhir
st.markdown("---")
st.caption(f"© 2026 AI Generator Pro - Andy Kurniawan | Sisa Sesi: {MAX_FREE_TRIAL - st.session_state.usage_count}")
