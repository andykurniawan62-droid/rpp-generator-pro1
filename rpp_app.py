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
        color: #ffffff; text-align: center; padding: 20px;
        background: #1e1e1e; border-radius: 15px; border: 1px solid #3b82f6; margin-bottom: 25px;
    }
    [data-testid="stForm"] { background-color: #111111; padding: 30px; border-radius: 15px; border: 1px solid #444444; }
    label, .stMarkdown p { color: #ffffff !important; font-weight: bold; }
    .preview-box { background-color: #ffffff !important; color: #000000 !important; padding: 40px; border-radius: 5px; margin-top: 20px; }
    .preview-box table { border-collapse: collapse; width: 100%; color: #000 !important; border: 1px solid black; }
    .preview-box th, .preview-box td { border: 1px solid black !important; padding: 8px; }
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
# 3. FUNGSI GENERATE (AUTO-DETECTOR)
# ==============================
def generate_rpp_final(data):
    # LANGKAH 1: Tanya Google, "Model apa yang sebenarnya ada di akun saya?"
    try:
        list_models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
        list_res = requests.get(list_models_url)
        list_json = list_res.json()
        
        available_models = []
        if 'models' in list_json:
            for m in list_json['models']:
                # Cari model yang bisa buat konten (bukan model lama)
                if 'generateContent' in m['supportedGenerationMethods']:
                    available_models.append(m['name'])
        
        if not available_models:
            # Jika daftar kosong, paksa pakai versi 8b yang sering ada di free tier 2026
            available_models = ["models/gemini-1.5-flash-8b", "models/gemini-1.5-flash", "models/gemini-1.0-pro"]
            
    except:
        available_models = ["models/gemini-1.5-flash"]

    pertemuan_str = "\n".join([f"P{i+1}: {p['model']}, {p['waktu']}" for i, p in enumerate(data['pertemuan'])])
    prompt_text = f"Buat RPP HTML Rapi. Sekolah: {data['sekolah']}, Mapel: {data['mapel']}, Fase: {data['fase']}, Materi: {data['materi']}, Tujuan: {data['tujuan']}. {pertemuan_str}. Tanda tangan: AHMAD JUNAIDI & ANDY KURNIAWAN."

    last_error = ""
    # LANGKAH 2: Coba satu per satu model yang Google berikan tadi
    for model_name in available_models:
        # Gunakan v1beta untuk kompatibilitas daftar model
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            res_json = response.json()
            
            if 'candidates' in res_json:
                teks = res_json['candidates'][0]['content']['parts'][0]['text']
                return teks.replace("```html", "").replace("```", "").strip()
            else:
                last_error = res_json.get('error', {}).get('message', 'N/A')
                continue
        except:
            continue

    return f"<div style='background:white;color:red;padding:20px;'><b>SISTEM GOOGLE MASIH MENOLAK</b><br>Daftar Model yang ditemukan: {available_models}<br>Error Terakhir: {last_error}</div>"

# ==============================
# 4. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Mode: Auto-Detect System</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Nama Sekolah", "SDN ...")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with c2:
        fase = st.text_input("Fase", "B / IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 3, 1)
    
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
    with st.spinner("Mendeteksi model yang aktif di akun Anda..."):
        data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
        hasil = generate_rpp_final(data_input)
        
        if "SISTEM GOOGLE MASIH MENOLAK" in hasil:
            st.markdown(hasil, unsafe_allow_html=True)
        else:
            st.success("✅ RPP BERHASIL DISUSUN!")
            st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
            st.markdown(hasil, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 | Andy Kurniawan, S.Pd.SD</p>", unsafe_allow_html=True)
