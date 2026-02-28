import streamlit as st
import requests
import json

# ==============================
# 1. KONFIGURASI HALAMAN
# ==============================
st.set_page_config(page_title="RPP Generator Pro - Andy Kurniawan", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .main-title { color: #ffffff; text-align: center; padding: 20px; background: #1e1e1e; border-radius: 15px; border: 1px solid #3b82f6; margin-bottom: 25px; }
    
    #rpp-cetak { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 40px 60px; 
        font-family: 'Times New Roman', Times, serif;
        font-size: 12pt;
        line-height: 1.5;
        border: 1px solid #ccc;
    }
    #rpp-cetak h1 { text-align: center; font-size: 16pt; text-transform: uppercase; text-decoration: underline; color: #000; }
    #rpp-cetak table { width: 100%; border-collapse: collapse; margin-bottom: 15px; color: #000; }
    #rpp-cetak table.border th, #rpp-cetak table.border td { border: 1px solid black !important; padding: 8px; }
    #rpp-cetak table.no-border td { border: none !important; padding: 4px; }

    @media print {
        header, footer, .stSidebar, .stButton, [data-testid="stForm"], .main-title, .stAlert, .download-btn {
            display: none !important;
        }
        .stApp { background-color: white !important; }
        #rpp-cetak { border: none !important; width: 100%; padding: 0; margin: 0; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. LOGIN & AUTH
# ==============================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "12345")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'><h1>🔐 Akses Guru RPP Pro</h1><p>Andy Kurniawan, S.Pd.SD</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        pwd = st.text_input("Password", type="password")
        if st.button("Masuk"):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("❌ Password salah")
    st.stop()

# ==============================
# 3. FUNGSI AI DENGAN MULTI-MODEL (FALLBACK)
# ==============================
def generate_rpp_ai(data):
    # DAFTAR MODEL YANG AKAN DICRY SATU PER SATU
    model_variants = [
        "gemini-3.1-pro-preview", 
        "gemini-3-flash-preview",
        "gemini-2.5-flash",
        "gemini-2.0-flash"
    ]
    
    pertemuan_str = "\n".join([f"Pertemuan {i+1}: Model {p['model']}, Waktu {p['waktu']}" for i, p in enumerate(data['pertemuan'])])
    
    prompt = f"""
    Buat RPP Kurikulum Merdeka Lengkap dalam HTML. 
    Identitas:
    Sekolah: {data['sekolah']}
    Mapel: {data['mapel']}
    Fase/Kelas: {data['fase']}
    Materi: {data['materi']}
    Tujuan: {data['tujuan']}
    {pertemuan_str}

    Format WAJIB:
    - Judul <h1> RENCANA PELAKSANAAN PEMBELAJARAN
    - Tabel Identitas & Tanda tangan pakai <table class="no-border">
    - Tabel Langkah Pembelajaran pakai <table class="border"> (Kolom: No, Tahap, Kegiatan, Waktu)
    - Tanda Tangan: Kiri (Kepala Sekolah AHMAD JUNAIDI, S.Pd), Kanan (Guru ANDY KURNIAWAN, S.Pd.SD)
    - Jangan sertakan teks markdown ```html, berikan tag HTML saja.
    """

    for model_name in model_variants:
        url = f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            response = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=45)
            res_json = response.json()
            
            if 'candidates' in res_json:
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                return content.replace("```html", "").replace("```", "").strip()
            else:
                # Jika gagal, lanjut ke model berikutnya di list
                continue
        except:
            continue
            
    return "<p style='color:red;'>Maaf, semua model AI (3.1, 3.0, 2.5, 2.0) gagal merespon. Silakan periksa API Key atau koneksi Anda.</p>"

# ==============================
# 4. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Smart Fallback AI System (3.1-Pro s/d 2.0-Flash)</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    col1, col2 = st.columns(2)
    with col1:
        sekolah = st.text_input("Nama Sekolah", "SDN ...")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with col2:
        fase = st.text_input("Fase", "B / IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 3, 1)
    
    materi = st.text_area("Materi")
    tujuan = st.text_area("Tujuan Pembelajaran")
    
    pertemuan_data = []
    for i in range(int(jml)):
        c1, c2 = st.columns(2)
        with c1: mod = st.selectbox(f"Model P{i+1}", ["PBL", "PjBL", "Discovery"], key=f"mod{i}")
        with c2: wakt = st.text_input(f"Waktu P{i+1}", "2x35 Menit", key=f"wakt{i}")
        pertemuan_data.append({"model": mod, "waktu": wakt})
    
    submit = st.form_submit_button("🚀 GENERATE RPP")

if submit:
    with st.spinner("AI sedang mencari model yang tersedia dan menyusun RPP..."):
        hasil = generate_rpp_ai({"sekolah":sekolah, "mapel":mapel, "fase":fase, "materi":materi, "tujuan":tujuan, "pertemuan":pertemuan_data})
        st.session_state.hasil_rpp = hasil

if "hasil_rpp" in st.session_state:
    st.markdown('<button onclick="window.print()" class="download-btn" style="width:100%; padding:15px; background-color:#28a745; color:white; border:none; border-radius:10px; cursor:pointer; font-weight:bold; font-size:16px; margin-bottom:20px;">📥 DOWNLOAD / CETAK RPP (PDF)</button>', unsafe_allow_html=True)
    
    st.markdown(f"""
        <div id="rpp-cetak">
            {st.session_state.hasil_rpp}
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 | Andy Kurniawan, S.Pd.SD</p>", unsafe_allow_html=True)
