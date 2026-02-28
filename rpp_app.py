import streamlit as st
import google.generativeai as genai

# ==============================
# 1. KONFIGURASI HALAMAN & CSS
# ==============================
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .rpp-paper { 
        background-color: #ffffff !important; color: #000000 !important; 
        padding: 40px 60px; font-family: 'Times New Roman', Times, serif;
        font-size: 11pt; line-height: 1.5; border-radius: 5px;
    }
    .rpp-paper h1 { text-align: center; text-decoration: underline; font-size: 16pt; color: #000; text-transform: uppercase; }
    .rpp-paper table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
    .rpp-paper th, .rpp-paper td { border: 1px solid black; padding: 6px 10px; color: #000; vertical-align: top; }
    .rpp-paper .no-border, .rpp-paper .no-border td { border: none !important; padding: 2px 0; }
    .name-line { font-weight: bold; text-decoration: underline; margin-bottom: 0px; }
    .nip-line { margin-top: -5px; font-size: 10pt; }

    @media print {
        header, footer, .stSidebar, .stButton, .stForm, .main-header, [data-testid="stHeader"] { display: none !important; }
        .stApp { background-color: white !important; }
        .rpp-paper { box-shadow: none; border: none; padding: 0; margin: 0; width: 100%; }
        table { page-break-inside: auto; }
        tr { page-break-inside: avoid; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. SISTEM API & SIDEBAR
# ==============================
with st.sidebar:
    st.header("🔑 Pengaturan API")
    user_api_key = st.text_input("Ganti/Input API Key Cadangan", type="password", help="Masukkan API Key jika jalur utama limit.")
    
    st.divider()
    st.info("Aplikasi ini menggunakan sistem estafet: Jika Gemini 2.0 limit, otomatis pindah ke 2.5 lalu 1.5.")

# Gunakan API Key dari Sidebar jika ada, jika tidak gunakan dari Secrets
FINAL_API_KEY = user_api_key if user_api_key else st.secrets.get("GEMINI_API_KEY", "")

if not FINAL_API_KEY:
    st.error("⚠️ API Key tidak ditemukan! Masukkan di Sidebar atau Secrets.")
    st.stop()

genai.configure(api_key=FINAL_API_KEY)

# ==============================
# 3. INTERFACE HEADER
# ==============================
st.markdown(f"""
    <div class="main-header" style="background-color:#007BFF;padding:20px;border-radius:10px;text-align:center;margin-bottom:20px;">
        <h1 style="color:white;margin:0;">AI RPP GENERATOR PRO</h1>
        <p style="color:white;font-weight:bold;margin:5px;">Karya: ANDY KURNIAWAN (WA: 081338370402)</p>
    </div>
""", unsafe_allow_html=True)

# ==============================
# 4. FORM INPUT (SAMA SEPERTI SEBELUMNYA)
# ==============================
with st.form("main_form"):
    st.subheader("🏢 Data Administrasi")
    c1, c2 = st.columns(2)
    with c1:
        nama_sekolah = st.text_input("Nama Sekolah")
        nama_kepsek = st.text_input("Nama Kepala Sekolah")
        nip_kepsek = st.text_input("NIP Kepala Sekolah")
    with c2:
        nama_guru = st.text_input("Nama Guru")
        nip_guru = st.text_input("NIP Guru")
        mapel = st.selectbox("Mata Pelajaran", ["Pendidikan Agama", "Pendidikan Pancasila", "Bahasa Indonesia", "Matematika", "IPAS", "Seni Musik", "Seni Rupa", "PJOK", "Bahasa Inggris"])

    st.subheader("🌟 Profil Pelajar Pancasila & Media")
    p1 = st.checkbox("Keimanan & Ketakwaan Tuhan YME")
    p2 = st.checkbox("Penalaran Kritis & Kreativitas")
    media_ajar = st.text_input("Media (LCD, Alat Peraga, dll)")
    sumber_ajar = st.text_input("Sumber (Buku, Internet, dll)")

    st.subheader("📅 Rincian Pertemuan")
    fase = st.text_input("Fase/Kelas", "Fase B / Kelas 4")
    jml_pertemuan = st.number_input("Jumlah Pertemuan", 1, 15, 1)

    list_model = ["PBL", "PjBL", "Discovery Learning", "Inquiry", "Contextual", "STAD", "Demonstrasi", "Mind Mapping", "Role Playing", "TPS", "Problem Solving", "Blended", "Flipped", "Project Citizen", "Ceramah Plus"]
    
    data_pertemuan = []
    for i in range(int(jml_pertemuan)):
        ca, cb = st.columns(2)
        with ca: m = st.selectbox(f"Model P{i+1}", list_model, key=f"m_{i}")
        with cb: t = st.text_input(f"Tanggal P{i+1}", "2026-01-01", key=f"t_{i}")
        data_pertemuan.append({"no": i+1, "model": m, "tgl": t})

    materi_pokok = st.text_area("Materi Pokok / CP")
    btn_generate = st.form_submit_button("🚀 GENERATE RPP SEKARANG")

# ==============================
# 5. LOGIKA GENERATE (ESTAFET MODEL)
# ==============================
if btn_generate:
    model_options = ['gemini-2.0-flash-001', 'gemini-2.5-flash', 'gemini-1.5-flash']
    jadwal_detail = "\n".join([f"- P{p['no']}: {p['model']} ({p['tgl']})" for p in data_pertemuan])
    
    prompt = f"""
    Buat RPP Kurikulum Merdeka HOLISTIK dalam HTML.
    Sekolah: {nama_sekolah} | Guru: {nama_guru} | Kepsek: {nama_kepsek}
    Materi: {materi_pokok} | Media: {media_ajar} | Sumber: {sumber_ajar}
    Jadwal: {jadwal_detail}
    
    SYARAT:
    1. Ada Pertanyaan Pemantik & Apersepsi Bermakna.
    2. Langkah Inti sesuai Model Pembelajaran.
    3. Ada Refleksi Murid (Berkesadaran).
    4. Tanda tangan rapat (class 'name-line' dan 'nip-line').
    """

    success = False
    for model_name in model_options:
        try:
            with st.spinner(f"Mencoba Jalur {model_name}..."):
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                if response.text:
                    st.session_state.hasil_rpp = response.text.replace("```html", "").replace("```", "").strip()
                    success = True
                    st.success(f"✅ Berhasil menggunakan jalur {model_name}")
                    break
        except Exception as e:
            if "429" in str(e):
                st.warning(f"Jalur {model_name} penuh, pindah ke jalur berikutnya...")
                continue
            else:
                st.error(f"Error pada {model_name}: {e}")
                continue

    if not success:
        st.error("⚠️ Semua jalur API limit. Gunakan API Key cadangan di Sidebar!")

# ==============================
# 6. DISPLAY
# ==============================
if "hasil_rpp" in st.session_state:
    st.markdown('<button onclick="window.print()" style="width:100%; padding:15px; background-color:#28a745; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold;">📥 DOWNLOAD / CETAK PDF</button>', unsafe_allow_html=True)
    st.markdown(f'<div class="rpp-paper">{st.session_state.hasil_rpp}</div>', unsafe_allow_html=True)
