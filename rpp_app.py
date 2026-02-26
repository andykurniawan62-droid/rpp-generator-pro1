import streamlit as st
import requests
import json

# ==============================
# 1. KONFIGURASI HALAMAN & CSS
# ==============================
st.set_page_config(page_title="RPP Generator Pro - Andy Kurniawan", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    /* UI Aplikasi */
    .stApp { background-color: #000000; color: #ffffff; }
    .main-title {
        color: #ffffff; text-align: center; padding: 20px;
        background: #1e1e1e; border-radius: 15px; border: 1px solid #3b82f6; margin-bottom: 25px;
    }
    [data-testid="stForm"] { background-color: #111111; padding: 30px; border-radius: 15px; border: 1px solid #444444; }
    
    /* PREVIEW RPP (FORMAT KERTAS RESMI) */
    .preview-box { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 60px 80px; 
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 1.5;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        margin-top: 20px;
    }
    .preview-box h1 { text-align: center; font-size: 16pt; text-transform: uppercase; text-decoration: underline; margin-bottom: 30px; }
    .preview-box h2 { font-size: 13pt; text-transform: uppercase; border-bottom: 2px solid #000; margin-top: 25px; margin-bottom: 10px; }
    .preview-box h3 { font-size: 12pt; margin-top: 15px; margin-bottom: 5px; }
    
    /* Style Tabel RPP */
    .preview-box table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
    .preview-box table.border, .preview-box table.border th, .preview-box table.border td { 
        border: 1px solid black !important; 
    }
    .preview-box th, .preview-box td { padding: 8px; text-align: left; vertical-align: top; color: black !important; }
    
    /* Style Tabel Tanpa Border (Untuk Identitas & Tanda Tangan) */
    .preview-box table.no-border, .preview-box table.no-border td { border: none !important; }
    
    .signature-space { height: 80px; }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. SISTEM LOGIN & API KEY
# ==============================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "12345")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'><h1>🔐 Akses Guru RPP Pro</h1><p>Andy Kurniawan, S.Pd.SD</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        pwd = st.text_input("Password Aplikasi", type="password")
        if st.button("Masuk"):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Password salah")
    st.stop()

# ==============================
# 3. MESIN AI (AUTO-SCAN MODEL)
# ==============================
def generate_rpp_ai(data):
    # Tahap 1: Scan model yang aktif di akun User
    available_models = []
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        list_res = requests.get(list_url).json()
        if 'models' in list_res:
            available_models = [m['name'] for m in list_res['models'] if 'generateContent' in m['supportedGenerationMethods']]
    except: pass
    
    if not available_models:
        available_models = ["models/gemini-1.5-flash", "models/gemini-1.0-pro"]

    # Tahap 2: Buat Prompt yang Sangat Detail agar Hasil Rapi
    pertemuan_details = "\n".join([f"- Pertemuan {i+1}: Model {p['model']}, Waktu {p['waktu']}" for i, p in enumerate(data['pertemuan'])])
    
    prompt = f"""
    Buatlah RPP Kurikulum Merdeka dalam format HTML murni. 
    Gunakan data berikut (Jangan gunakan placeholder/kurung siku):
    - Sekolah: {data['sekolah']}
    - Mata Pelajaran: {data['mapel']}
    - Fase/Kelas: {data['fase']}
    - Materi Utama: {data['materi']}
    - Tujuan Pembelajaran: {data['tujuan']}
    - Detail Pertemuan: {pertemuan_details}

    STRUKTUR HTML WAJIB:
    1. Judul: <h1>RENCANA PELAKSANAAN PEMBELAJARAN</h1>
    2. Identitas: Gunakan <table class="no-border"> (Isi: Satuan Pendidikan, Mapel, Kelas, Semester, Materi, Alokasi Waktu).
    3. Komponen Inti: (Tujuan, Pemahaman Bermakna, Pertanyaan Pemantik).
    4. Langkah Pembelajaran: Gunakan <table class="border"> dengan kolom: No, Tahap, Kegiatan Pembelajaran, Waktu.
    5. Asesmen & Lampiran: Jelaskan secara ringkas.
    6. Tanda Tangan: Gunakan <table class="no-border"> dengan 2 kolom:
       - Kolom 1: Mengetahui, Kepala {data['sekolah']}, [Spasi Tanda Tangan], AHMAD JUNAIDI, S.Pd.
       - Kolom 2: [Nama Kota], [Tanggal], Guru Kelas, [Spasi Tanda Tangan], ANDY KURNIAWAN, S.Pd.SD.
    
    PENTING: Gunakan class CSS yang sudah disediakan ('border' untuk tabel bergaris, 'no-border' untuk identitas).
    """

    # Tahap 3: Eksekusi Pencarian Model
    for model_path in available_models:
        api_url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={GEMINI_API_KEY}"
        try:
            res = requests.post(api_url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=60)
            res_json = res.json()
            if 'candidates' in res_json:
                raw_html = res_json['candidates'][0]['content']['parts'][0]['text']
                return raw_html.replace("```html", "").replace("```", "").strip()
        except: continue
    
    return "<p style='color:red;'>Gagal menghubungi server Google. Cek API Key Anda.</p>"

# ==============================
# 4. INTERFACE PENGGUNA (UI)
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Format Kurikulum Merdeka - Standar Times New Roman</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    col1, col2 = st.columns(2)
    with col1:
        sekolah = st.text_input("Nama Sekolah Lengkap", "SDN ...")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with col2:
        fase = st.text_input("Fase / Kelas", "B / IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 3, 1)
    
    materi = st.text_area("Materi Utama", placeholder="Contoh: Praktik Musyawarah dan Kesepakatan Bersama")
    tujuan = st.text_area("Tujuan Pembelajaran", placeholder="Contoh: Murid dapat mempraktikkan musyawarah...")
    
    pertemuan_data = []
    for i in range(int(jml)):
        st.write(f"---")
        c1, c2 = st.columns(2)
        with c1: mod = st.selectbox(f"Model Pembelajaran P{i+1}", ["Problem Based Learning", "Project Based Learning", "Discovery Learning"], key=f"mod{i}")
        with c2: wakt = st.text_input(f"Alokasi Waktu P{i+1}", "2 x 35 Menit", key=f"wakt{i}")
        pertemuan_data.append({"model": mod, "waktu": wakt})
    
    submit = st.form_submit_button("🚀 GENERATE RPP SEKARANG")

if submit:
    if not GEMINI_API_KEY:
        st.error("API Key belum terpasang di Secrets!")
    else:
        with st.spinner("Sedang menyusun dokumen sesuai standar Kemdikbud..."):
            data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
            hasil_rpp = generate_rpp_ai(data_input)
            
            st.success("✅ RPP BERHASIL DISUSUN")
            st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
            st.markdown(hasil_rpp, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.warning("🖨️ CARA CETAK: Klik kanan pada hasil putih di atas -> Pilih 'Print' -> Save as PDF.")

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 RPP Generator Pro | Andy Kurniawan, S.Pd.SD</p>", unsafe_allow_html=True)
