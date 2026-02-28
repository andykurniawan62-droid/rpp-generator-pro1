import streamlit as st
import google.generativeai as genai

# ==============================
# 1. KONFIGURASI HALAMAN & CSS
# ==============================
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Area Kertas Putih untuk Hasil RPP */
    .rpp-paper { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 40px 60px; 
        font-family: 'Times New Roman', Times, serif;
        font-size: 11pt;
        line-height: 1.5;
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
MAX_FREE_TRIAL = 3

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
    st.error("🚫 BATAS PENGGUNAAN GRATIS TERCAPAI. Hubungi Pak Andy Kurniawan (081338370402) untuk aktivasi Full.")
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

    st.subheader("🌟 Dimensi Profil Lulusan")
    cp1, cp2 = st.columns(2)
    with cp1:
        p1 = st.checkbox("Keimanan & Ketakwaan Kepada Tuhan YME")
        p2 = st.checkbox("Kewargaan (Berkebinekaan Global)")
        p3 = st.checkbox("Penalaran Kritis")
        p4 = st.checkbox("Kreativitas")
    with cp2:
        p5 = st.checkbox("Kolaborasi (Gotong Royong)")
        p6 = st.checkbox("Kemandirian")
        p7 = st.checkbox("Kesehatan")
        p8 = st.checkbox("Komunikasi")

    st.subheader("📖 Sumber & Media Belajar")
    cm1, cm2 = st.columns(2)
    with cm1:
        media_ajar = st.text_area("Media Pembelajaran", placeholder="Contoh: LCD Proyektor, Video YouTube, Kartu Gambar, Alat Peraga...")
    with cm2:
        sumber_ajar = st.text_area("Sumber Belajar", placeholder="Contoh: Buku Siswa Kelas 4, Lingkungan Sekolah, Internet...")

    st.subheader("📅 Rincian Pertemuan")
    fase = st.text_input("Fase/Kelas/Semester", value="Fase B / Kelas 4 / Ganjil")
    jml_pertemuan = st.number_input("Jumlah Pertemuan", 1, 15, 1)

    list_model = ["PBL (Problem Based Learning)", "PjBL (Project Based Learning)", "Discovery Learning", "Inquiry Learning", "Contextual Learning", "STAD", "Demonstrasi", "Mind Mapping", "Role Playing", "Think Pair Share", "Problem Solving", "Blended Learning", "Flipped Classroom", "Project Citizen", "Ceramah Plus"]

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
# 5. LOGIKA GENERATE (HOLISTIK)
# ==============================
if btn_generate:
    if not nama_sekolah or not materi_pokok:
        st.warning("⚠️ Mohon lengkapi Data Sekolah dan Materi!")
    else:
        profil_str = ", ".join([k for k, v in {"Beriman":p1, "Kewargaan":p2, "Bernalar Kritis":p3, "Kreatif":p4, "Kolaborasi":p5, "Mandiri":p6, "Kesehatan":p7, "Komunikasi":p8}.items() if v])
        jadwal_detail = "\n".join([f"- P{p['no']}: Model {p['model']}, Waktu {p['waktu']}, Tgl {p['tgl']}" for p in data_pertemuan])
        
        prompt = f"""
        Buatlah RPP Kurikulum Merdeka yang HOLISTIK, BERMAKNA, dan MENGGEMBIRAKAN dalam format HTML murni.
        Sekolah: {nama_sekolah} | Guru: {nama_guru} | Kepsek: {nama_kepsek}
        Mapel: {mapel} | Fase: {fase} | Materi: {materi_pokok}
        Dimensi Profil: {profil_str} | Media: {media_ajar} | Sumber: {sumber_ajar}
        Jadwal: {jadwal_detail} | Tujuan: {tujuan_umum}

        WAJIB MUNCULKAN KOMPONEN BERIKUT:
        1. IDENTITAS & KOMPONEN INTI: Tampilkan dalam <table class="no-border"> termasuk Media dan Sumber Belajar.
        2. PERTANYAAN PEMANTIK: Untuk membangun kesadaran murid.
        3. LANGKAH PEMBELAJARAN (Tabel Border):
           - PENDAHULUAN: Apersepsi yang BERMAKNA (kaitan kehidupan nyata).
           - INTI: Sesuai Sintaks Model Pembelajaran yang dipilih, suasana MENGGEMBIRAKAN.
           - PENUTUP: REFLEKSI MURID (untuk kemandirian/pengaturan diri).
        4. ASESMEN: Diagnostik, Formatif, dan Sumatif lengkap dengan Rubrik/Kisi-kisi.
        5. TANDA TANGAN: Kepsek (Kiri), Guru (Kanan). Gunakan class="name-line" dan class="nip-line" agar rapat.

        Hanya berikan tag HTML tanpa markdown atau pembukaan.
        """

        try:
            with st.spinner("Sedang menyusun RPP yang Holistik & Bermakna..."):
                model = genai.GenerativeModel('gemini-2.0-flash-001')
                response = model.generate_content(prompt)
                st.session_state.usage_count += 1
                st.session_state.hasil_rpp = response.text.replace("```html", "").replace("```", "").strip()
        except Exception as e:
            st.error(f"Terjadi kendala teknis: {e}")

# ==============================
# 6. DISPLAY HASIL
# ==============================
if "hasil_rpp" in st.session_state:
    st.success(f"✅ RPP Selesai! (Sisa Kuota: {MAX_FREE_TRIAL - st.session_state.usage_count})")
    st.markdown("""<button onclick="window.print()" style="width:100%; padding:15px; background-color:#28a745; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px;">📥 DOWNLOAD / CETAK SEBAGAI PDF</button>""", unsafe_allow_html=True)
    st.markdown(f'<div class="rpp-paper">{st.session_state.hasil_rpp}</div>', unsafe_allow_html=True)

st.markdown(f"<br><p style='text-align: center; color: #555;'>© 2026 AI Generator Pro - Andy Kurniawan</p>", unsafe_allow_html=True)


