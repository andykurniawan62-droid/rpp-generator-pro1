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
    .main-title {
        color: #ffffff; text-align: center; padding: 30px;
        background: #1e1e1e; border-radius: 15px; border: 1px solid #3b82f6; margin-bottom: 25px;
    }
    [data-testid="stForm"] { background-color: #111111; padding: 30px; border-radius: 15px; border: 1px solid #444444; }
    label, .stMarkdown p { color: #ffffff !important; font-weight: bold; }
    .preview-box { background-color: #ffffff; color: #000000; padding: 30px; border-radius: 10px; border: 1px solid #ccc; }
    table { border-collapse: collapse; width: 100%; color: black !important; }
    th, td { border: 1px solid black !important; padding: 8px; text-align: left; }
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
# 3. FUNGSI GENERATE (ULTRA STABIL - V1)
# ==============================
def generate_rpp_direct(data):
    # KITA PAKSA PAKAI JALUR v1 (STABLE) DAN MODEL gemini-1.0-pro-001
    # Ini adalah model yang paling kompatibel dengan semua jenis API Key
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.0-pro:generateContent?key={GEMINI_API_KEY}"
    
    pertemuan_str = "\n".join([f"P{i+1}: {p['model']}, Waktu {p['waktu']}" for i, p in enumerate(data['pertemuan'])])
    
    prompt_text = f"Buat RPP HTML. Sekolah: {data['sekolah']}, Mapel: {data['mapel']}, Fase: {data['fase']}, Materi: {data['materi']}, Tujuan: {data['tujuan']}. {pertemuan_str}. Tanda tangan: AHMAD JUNAIDI & ANDY KURNIAWAN."

    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=40)
        res_json = response.json()
        
        if 'candidates' in res_json:
            teks = res_json['candidates'][0]['content']['parts'][0]['text']
            return teks.replace("```html", "").replace("```", "").strip()
        else:
            # Jika gagal lagi, kita coba satu model cadangan terakhir
            error_msg = res_json.get('error', {}).get('message', 'Model Tidak Support')
            return f"Error: {error_msg}"
            
    except Exception as e:
        return f"Koneksi Gagal: {str(e)}"

# ==============================
# 4. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Versi Terakhir (Anti-404)</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Sekolah", "SDN ...")
        mapel = st.text_input("Mapel", "PJOK")
    with c2:
        fase = st.text_input("Fase", "B / IV")
        jml = st.number_input("Pertemuan", 1, 3, 1)
    
    materi = st.text_area("Materi")
    tujuan = st.text_area("Tujuan")
    
    pertemuan_data = []
    for i in range(int(jml)):
        col1, col2 = st.columns(2)
        with col1: m = st.selectbox(f"Model P{i+1}", ["PBL", "Discovery"], key=f"m{i}")
        with col2: w = st.text_input(f"Waktu P{i+1}", "2x35m", key=f"w{i}")
        pertemuan_data.append({"model": m, "waktu": w})
    
    submit = st.form_submit_button("🚀 GENERATE")

if submit:
    with st.spinner("Menyusun RPP..."):
        data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
        hasil = generate_rpp_direct(data_input)
        
        if "Error:" in hasil:
            st.error(f"Sistem Google Menolak: {hasil}")
            st.markdown("### 🛠 Solusi Wajib:")
            st.markdown("1. Buka [Google AI Studio](https://aistudio.google.com/).")
            st.markdown("2. Klik tombol **'Create API key'** -> Pilih **'Create API key in NEW project'**.")
            st.markdown("3. Jangan gunakan key yang lama, pakai yang benar-benar baru dari Project baru.")
        else:
            st.success("✅ BERHASIL!")
            st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
            st.markdown(hasil, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 RPP Generator Pro</p>", unsafe_allow_html=True)
