import streamlit as st
import google.generativeai as genai

# ==============================
# 1. KONFIGURASI HALAMAN & CSS
# ==============================
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝", layout="wide")

st.markdown("""
    <style>
    /* Tema Gelap untuk Aplikasi */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Area Kertas Putih untuk Hasil RPP */
    .rpp-paper { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 40px 60px; 
        font-family: 'Times New Roman', Times, serif;
        font-size: 11pt;
        line-height: 1.4;
        border-radius: 5px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .rpp-paper h1 { text-align: center; text-decoration: underline; font-size: 16pt; color: #000; text-transform: uppercase; margin-bottom: 20px; }
    .rpp-paper table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
    .rpp-paper th, .rpp-paper td { border: 1px solid black; padding: 6px 10px; text-align: left; color: #000; vertical-align: top; }
    
    /* CSS KHUSUS TANDA TANGAN & IDENTITAS (TANPA GARIS) */
    .rpp-paper .no-border, .rpp-paper .no-border td { border: none !important; padding: 2px 0; }
    .name-line { font-weight: bold; text-decoration: underline; margin-bottom: 0px; padding-bottom: 0px; }
    .nip-line { margin-top: -5px; padding-top: 0px; font-size: 10pt; }

    /* Mencegah Tabel Terpotong saat Print */
    @media print {
        .stButton, .stForm, .stMarkdown:not(.rpp-paper), header, footer, .main-header, [data-testid="stHeader"] {
            display: none !important;
        }
        .stApp { background-color: white !important; }
        .rpp-paper { box-shadow: none; border: none; padding: 0; margin: 0; width: 100%; }
        table { page-break-inside: auto; }
        tr { page-break-inside: avoid; page-break-after: auto; }
        @page { size: auto; margin: 1.5cm; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. SISTEM KEAMANAN & API
# ==============================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    st.error("⚠️ API Key tidak ditemukan di Secrets!")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

MAX_FREE_TRIAL = 5

# ==============================
# 3. INTERFACE (HEADER)
# ==============================
st.markdown(f"""
    <div class="main-header" style="background-color:#007BFF;padding:20px;border-radius:10px;text-align:center;margin-bottom:20px;">
        <h1 style="color:white;margin:0;">AI RPP GENERATOR PRO</h1>
        <p style="color:white;font-weight:bold;margin:5px;">Karya: ANDY KURNIAWAN (WA: 081338370402)</p>
    </div>
""", unsafe_allow_html=True)

if st.session_state.usage_count >= MAX_FREE_TRIAL:
    st.error("🚫 BATAS PENGGUNAAN GRATIS TERCAPAI")
    st.info("Hubungi Pak Andy Kurniawan: 081338370402 untuk aktivasi Versi Full.")
    st.stop()

# ==============================
# 4. FORM INPUT
# ==============================
with st.form("main_form"):
    st.subheader("🏢 Data Administrasi Sekolah")
    c1, c2 = st.columns(2)
    with c1:
        nama_sekolah = st.text_input("Nama Sekolah", placeholder="SD Negeri ...")
        nama_kepsek = st.text_input("Nama Kepala Sekolah")
        nip_kepsek = st.text_input("NIP Kepala Sekolah")
    with c2:
        nama_guru = st.text_input("Nama Guru")
        nip_guru = st.text_input("NIP Guru")
        mapel = st.selectbox("Mata Pelajaran", ["Pendidikan Agama", "Pendidikan Pancasila", "Bahasa Indonesia", "Matematika", "IPAS", "Seni Musik", "Seni Rupa", "Seni Teater", "Seni Tari", "PJOK", "Bahasa Inggris", "Muatan Lokal"])

    st.subheader("🌟 Dimensi Profil Pelajar Pancasila")
    cp1, cp2 = st.columns(2)
    with cp1:
        p1 = st.checkbox("Keimanan dan Ketakwaan Kepada Tuhan Yang Maha Esa")
        p2 = st.checkbox("Kewargaan (Berkebinekaan Global)")
        p3 = st.checkbox("Penalaran Kritis")
        p4 = st.checkbox("Kreativitas")
    with cp2:
        p5 = st.checkbox("Kolaborasi (Gotong Royong)")
        p6 = st.checkbox("Kemandirian")
        p7 = st.checkbox("Kesehatan")
        p8 = st.checkbox("Komunikasi")

    profil_list = [k for k, v in {
        "Beriman & Bertakwa YME": p1, "Berkebinekaan Global": p2, 
        "Bernalar Kritis": p3, "Kreatif": p4, "Gotong Royong": p5, 
        "Mandiri": p6, "Kesehatan": p7, "Komunikasi": p8
    }.items() if v]

    st.subheader("📖 Rincian Pembelajaran")
    fase = st.text_input("Fase/Kelas/Semester", value="Fase B / Kelas 4 / Ganjil")
    jml_pertemuan = st.number_input("Jumlah Pertemuan", 1, 15, 1)

    # DAFTAR 15 MODEL PEMBELAJARAN
    list_model = [
        "PBL (Problem Based Learning)", "PjBL (Project Based Learning)", 
        "Discovery Learning", "Inquiry Learning", "Contextual Learning", 
        "STAD", "Demonstrasi", "Mind Mapping", "Role Playing", 
        "Think Pair Share", "Problem Solving", "Blended Learning", 
        "Flipped Classroom", "Project Citizen", "Ceramah Plus"
    ]

    data_pertemuan = []
    for i in range(int(jml_pertemuan)):
        with st.expander(f"📍 Konfigurasi Pertemuan Ke-{i+1}", expanded=(i==0)):
            ca, cb, cc = st.columns([2,1,1])
            with ca: m = st.selectbox(f"Model P{i+1}", list_model, key=f"m_{i}")
            with cb: w = st.text_input(f"Waktu P{i+1}", "2x35 Menit", key=f"w_{i}")
            with cc: t = st.text_input(f"Tanggal P{i+1}", placeholder="DD-MM-YYYY", key=f"t_{i}")
            data_pertemuan.append({"no": i+1, "model": m, "waktu": w, "tgl": t})

    tujuan_umum = st.text_area("Tujuan Pembelajaran")
    materi_pokok = st.text_area("Detail Materi Pokok (CP/ATP)")
    
    btn_generate = st.form_submit_button("🚀 GENERATE RPP SEKARANG")

# ==============================
# 5. LOGIKA GENERATE (FALLBACK)
# ==============================
if btn_generate:
    if not nama_sekolah or not materi_pokok:
        st.warning("⚠️ Nama Sekolah dan Materi tidak boleh kosong!")
    else:
        model_options = ['gemini-2.0-flash-001', 'gemini-1.5-flash-latest']
        success = False
        jadwal_detail = "\n".join([f"- P{p['no']}: Model {p['model']}, Waktu {p['waktu']}, Tgl {p['tgl']}" for p in data_pertemuan])
        profil_str = ", ".join(profil_list) if profil_list else "Umum"
        
        prompt = f"""
        Buatlah RPP Kurikulum Merdeka dalam format HTML murni.
        Sekolah: {nama_sekolah} | Guru: {nama_guru} | Kepsek: {nama_kepsek}
        Mapel: {mapel} | Fase: {fase} | Materi: {materi_pokok}
        Dimensi Profil Pelajar Pancasila: {profil_str}
        Jadwal Pertemuan: {jadwal_detail}
        
        SYARAT HTML:
        1. Judul: <h1>RENCANA PELAKSANAAN PEMBELAJARAN</h1>
        2. Identitas: Gunakan <table class="no-border">
        3. Langkah: Gunakan <table class="border"> (No, Tahap, Kegiatan, Waktu). Langkah inti harus sesuai dengan model pembelajaran per pertemuan.
        4. Tanda Tangan: Gunakan tabel 2 kolom.
           Gunakan class="name-line" untuk Nama dan class="nip-line" untuk NIP agar sangat rapat (tanpa celah).
        
        Hanya tag HTML, jangan berikan markdown ```html.
        """

        for model_name in model_options:
            try:
                with st.spinner(f"Menyusun dengan Jalur {model_name}..."):
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if response.text:
                        st.session_state.usage_count += 1
                        st.session_state.hasil_rpp = response.text.replace("```html", "").replace("```", "").strip()
                        success = True
                        break
            except: continue
        
        if not success:
            st.error("⚠️ Semua jalur AI sedang sibuk. Tunggu 1 menit.")

# ==============================
# 6. DISPLAY HASIL & PRINT
# ==============================
if "hasil_rpp" in st.session_state:
    st.success(f"✅ RPP Selesai Disusun! (Sisa Kuota: {MAX_FREE_TRIAL - st.session_state.usage_count})")
    st.markdown("""<button onclick="window.print()" style="width:100%; padding:15px; background-color:#28a745; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px;">📥 DOWNLOAD / CETAK SEBAGAI PDF</button>""", unsafe_allow_html=True)
    st.markdown(f'<div class="rpp-paper">{st.session_state.hasil_rpp}</div>', unsafe_allow_html=True)

st.markdown(f"<br><p style='text-align: center; color: #555;'>© 2026 AI Generator Pro - Andy Kurniawan</p>", unsafe_allow_html=True)
