import streamlit as st
import requests
import json
from bs4 import BeautifulSoup

# ==============================
# 1. KONFIGURASI HALAMAN
# ==============================
st.set_page_config(page_title="RPP Generator Pro - Andy Kurniawan", page_icon="📄", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    .main-title {
        color: #ffffff; text-align: center; padding: 30px;
        background: #1e1e1e; border-radius: 15px; border: 1px solid #3b82f6; margin-bottom: 25px;
    }
    [data-testid="stForm"] { background-color: #111111; padding: 30px; border-radius: 15px; border: 1px solid #444444; }
    label, .stMarkdown p { color: #ffffff !important; font-weight: bold; }
    .preview-box { background-color: #ffffff; color: #000000; padding: 40 paradox; border-radius: 10px; margin-top: 20px; border: 1px solid #ccc; overflow-x: auto; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid black; padding: 8px; text-align: left; }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. SECRETS & LOGIN
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
            else:
                st.error("❌ Password salah")
    st.stop()

# ==============================
# 3. FUNGSI GENERATE (AUTO-TRY MODELS)
# ==============================
def generate_rpp_direct(data):
    # Mencoba model yang paling mungkin aktif
    models_to_try = ["gemini-1.5-flash", "gemini-pro"]
    
    pertemuan_str = "\n".join([f"P{i+1}: Model {p['model']}, Waktu {p['waktu']}" for i, p in enumerate(data['pertemuan'])])
    
    prompt_text = f"""
    Buatlah RPP Kurikulum Merdeka dalam format HTML (gunakan tabel dengan border="1").
    Sekolah: {data['sekolah']}, Mapel: {data['mapel']}, Fase: {data['fase']}.
    Materi: {data['materi']}. Tujuan: {data['tujuan']}.
    Rincian: {pertemuan_str}.
    Wajib ada: Tabel Kegiatan Pembelajaran, Asesmen, dan Tanda Tangan: Kepala Sekolah (AHMAD JUNAIDI, S.Pd) & Guru (ANDY KURNIAWAN, S.Pd.SD).
    """

    last_error = ""
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            res_json = response.json()
            
            if 'candidates' in res_json:
                hasil_ai = res_json['candidates'][0]['content']['parts'][0]['text']
                # Bersihkan tag code markdown jika ada
                hasil_clean = hasil_ai.replace("```html", "").replace("```", "").strip()
                return hasil_clean
            else:
                last_error = res_json.get('error', {}).get('message', 'Unknown Error')
        except Exception as e:
            last_error = str(e)
            
    return f"<div style='color:red; background:white; padding:15px;'><b>Gagal:</b> {last_error}</div>"

# ==============================
# 4. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Versi Teruji - Andy Kurniawan</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Nama Sekolah", "SDN ...")
        mapel = st.text_input("Mapel", "PJOK")
    with c2:
        fase = st.text_input("Fase / Kelas", "B / IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 5, 1)
    
    materi = st.text_area("Materi Utama")
    tujuan = st.text_area("Tujuan Pembelajaran")
    
    pertemuan_data = []
    for i in range(int(jml)):
        st.markdown(f"**Pertemuan {i+1}**")
        col1, col2 = st.columns(2)
        with col1: m = st.selectbox(f"Model P{i+1}", ["PBL", "PjBL", "Discovery", "Ceramah"], key=f"m{i}")
        with col2: w = st.text_input(f"Waktu P{i+1}", "2x35m", key=f"w{i}")
        pertemuan_data.append({"model": m, "waktu": w})
    
    submit = st.form_submit_button("🚀 GENERATE RPP")

if submit:
    if not GEMINI_API_KEY:
        st.error("API Key belum diisi di Secrets!")
    else:
        with st.spinner("Sedang menyusun RPP..."):
            data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
            hasil = generate_rpp_direct(data_input)
            
            if "Gagal:" in hasil:
                st.markdown(hasil, unsafe_allow_html=True)
            else:
                st.success("✅ RPP BERHASIL DISUSUN!")
                st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
                st.markdown(hasil, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                st.info("Tips: Klik kanan pada halaman lalu pilih 'Print' dan simpan sebagai PDF.")

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 RPP Generator Pro | Andy Kurniawan, S.Pd.SD</p>", unsafe_allow_html=True)
