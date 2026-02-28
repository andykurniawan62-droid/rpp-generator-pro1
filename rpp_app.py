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
        padding: 50px 70px; 
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 1.6;
        border-radius: 5px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .rpp-paper h1 { text-align: center; text-decoration: underline; font-size: 16pt; color: #000; }
    .rpp-paper table { width: 100%; border-collapse: collapse; margin: 15px 0; }
    .rpp-paper th, .rpp-paper td { border: 1px solid black; padding: 8px; text-align: left; color: #000; }
    .no-border, .no-border td { border: none !important; }

    /* Tombol Sembunyi Saat Cetak */
    @media print {
        .stButton, .stForm, .stMarkdown:not(.rpp-paper), header, footer, .main-header {
            display: none !important;
        }
        .stApp { background-color: white !important; }
        .rpp-paper { box-shadow: none; border: none; padding: 0; margin: 0; width: 100%; }
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
        mapel = st.selectbox("Mata Pelajaran", ["Pendidikan Agama", "Pendidikan Pancasila", "Bahasa Indonesia", "Matematika", "IPAS", "Seni Musik", "PJOK", "Bahasa Inggris"])

    fase = st.text_input("Fase/Kelas/Semester", value="Fase B / Kelas 4 / Ganjil")
    jml_pertemuan = st.number_input("Jumlah Pertemuan", 1, 15, 1)

    data_pertemuan = []
    for i in range(int(jml_pertemuan)):
        with st.expander(f"📍 Konfigurasi Pertemuan Ke-{i+1}"):
            ca, cb, cc = st.columns([2,1,1])
            with ca: m = st.selectbox(f"Model P{i+1}", ["PBL", "PjBL", "Discovery", "Inquiry", "STAD"], key=f"m_{i}")
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
        # DAFTAR MODEL YANG AKAN DICOBA SECARA BERURUTAN
        model_options = [
            'gemini-2.0-flash-001', 
            'gemini-2.5-flash', 
            'gemini-1.5-flash-latest'
        ]
        
        success = False
        jadwal_detail = "\n".join([f"- P{p['no']}: {p['model']}, {p['waktu']}, Tgl: {p['tgl']}" for p in data_pertemuan])
        
        prompt = f"""
        Buatlah Rencana Pelaksanaan Pembelajaran (RPP) Kurikulum Merdeka dalam format HTML.
        Gunakan data:
        Sekolah: {nama_sekolah} | Kepsek: {nama_kepsek} ({nip_kepsek}) | Guru: {nama_guru} ({nip_guru})
        Mapel: {mapel} | Fase: {fase} | Materi: {materi_pokok} | Tujuan: {tujuan_umum}
        Jadwal: {jadwal_detail}
        
        STRUKTUR HTML:
        1. Judul: <h1>RENCANA PELAKSANAAN PEMBELAJARAN</h1>
        2. Identitas: Gunakan <table class="no-border">
        3. Langkah: Gunakan <table class="border"> dengan kolom No, Tahap, Kegiatan (Pendahuluan, Inti, Penutup), Waktu.
        4. Tanda Tangan: Di akhir gunakan <table class="no-border"> untuk Kepsek dan Guru.
        
        PENTING: Hanya berikan tag HTML, jangan berikan kata-kata pembuka atau markdown ```html.
        """

        for model_name in model_options:
            try:
                with st.spinner(f"Menghubungi Jalur {model_name}..."):
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        st.session_state.usage_count += 1
                        st.session_state.hasil_rpp = response.text
                        success = True
                        break
            except Exception:
                continue
        
        if not success:
            st.error("⚠️ Semua jalur AI sedang sibuk. Tunggu 1 menit dan coba lagi.")

# ==============================
# 6. DISPLAY HASIL & PRINT
# ==============================
if "hasil_rpp" in st.session_state:
    st.success(f"✅ RPP Berhasil Disusun! (Sisa Kuota: {MAX_FREE_TRIAL - st.session_state.usage_count})")
    
    st.markdown("""
        <button onclick="window.print()" style="width:100%; padding:15px; background-color:#28a745; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px;">
            📥 DOWNLOAD / CETAK SEBAGAI PDF
        </button>
        <p style='color:gray; font-size:12px; text-align:center;'>Tips: Setelah jendela muncul, pilih 'Save as PDF' pada bagian Destination/Printer.</p>
    """, unsafe_allow_html=True)
    
    # Area Kertas RPP
    st.markdown(f'<div class="rpp-paper">{st.session_state.hasil_rpp}</div>', unsafe_allow_html=True)

st.markdown(f"<br><p style='text-align: center; color: #555;'>© 2026 AI Generator Pro - Andy Kurniawan</p>", unsafe_allow_html=True)
