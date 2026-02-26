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
    .preview-box { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 50px; 
        border-radius: 5px; 
        margin-top: 20px; 
        font-family: 'Arial', sans-serif;
    }
    .preview-box table { border-collapse: collapse; width: 100%; color: #000000 !important; }
    .preview-box th, .preview-box td { border: 1px solid #000 !important; padding: 8px; }
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
# 3. FUNGSI GENERATE (TRIPLE SHOT)
# ==============================
def generate_rpp_triple_shot(data):
    # DAFTAR NAMA TEKNIS TERBARU (Sangat Spesifik)
    model_variants = [
        "gemini-1.5-flash-latest",   # Varian 1
        "gemini-1.5-flash-002",      # Varian 2 (Versi Stabil Terbaru)
        "gemini-1.5-flash"           # Varian Standar
    ]
    
    pertemuan_str = "\n".join([f"P{i+1}: {p['model']}, {p['waktu']}" for i, p in enumerate(data['pertemuan'])])
    prompt_text = f"Buat RPP HTML Rapi. Sekolah: {data['sekolah']}, Mapel: {data['mapel']}, Fase: {data['fase']}, Materi: {data['materi']}, Tujuan: {data['tujuan']}. {pertemuan_str}. Tanda tangan: AHMAD JUNAIDI & ANDY KURNIAWAN."

    last_error = ""
    for model_id in model_variants:
        # Kita coba jalur v1 (Stable) bukan v1beta agar lebih kuat
        url = f"https://generativelanguage.googleapis.com/v1/models/{model_id}:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
        
        try:
            response = requests.post(url, json=payload, timeout=45)
            res_json = response.json()
            
            if 'candidates' in res_json:
                teks = res_json['candidates'][0]['content']['parts'][0]['text']
                return teks.replace("```html", "").replace("```", "").strip()
            else:
                last_error = f"{model_id}: {res_json.get('error', {}).get('message', 'N/A')}"
                continue # Gagal? Coba varian model berikutnya
        except:
            continue

    return f"<div style='color:red; background:white; padding:15px;'><b>SEMUA MODEL DITOLAK:</b> {last_error}</div>"

# ==============================
# 4. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Mode: Triple-Shot Model Accuracy</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Nama Sekolah", "SDN ...")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with c2:
        fase = st.text_input("Fase / Kelas", "B / IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 3, 1)
    
    materi = st.text_area("Materi Utama")
    tujuan = st.text_area("Tujuan Pembelajaran")
    
    pertemuan_data = []
    for i in range(int(jml)):
        col1, col2 = st.columns(2)
        with col1: m = st.selectbox(f"Model P{i+1}", ["PBL", "PjBL", "Discovery"], key=f"m{i}")
        with col2: w = st.text_input(f"Waktu P{i+1}", "2x35m", key=f"w{i}")
        pertemuan_data.append({"model": m, "waktu": w})
    
    submit = st.form_submit_button("🚀 GENERATE RPP")

if submit:
    with st.spinner("Mencoba 3 varian model Google AI..."):
        data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
        hasil = generate_rpp_triple_shot(data_input)
        
        if "SEMUA MODEL DITOLAK" in hasil:
            st.markdown(hasil, unsafe_allow_html=True)
            st.warning("PERINGATAN: Jika error 404 berlanjut, berarti API KEY Anda belum divalidasi oleh Google. Mohon buat API KEY baru di Google AI Studio sekarang.")
        else:
            st.success("✅ RPP BERHASIL DISUSUN!")
            st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
            st.markdown(hasil, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 RPP Generator Pro | Andy Kurniawan, S.Pd.SD</p>", unsafe_allow_html=True)
