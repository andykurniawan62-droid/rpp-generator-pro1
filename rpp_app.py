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
    .preview-box { background-color: #ffffff; color: #000000; padding: 30px; border-radius: 10px; margin-top: 20px; border: 1px solid #ccc; }
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
# 3. FUNGSI GENERATE (FIXED MODEL 1.5 FLASH)
# ==============================
def generate_rpp_direct(data):
    # Menggunakan model paling update di jalur v1beta
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    pertemuan_str = "\n".join([f"Pertemuan {i+1}: Model {p['model']}, Waktu {p['waktu']}" for i, p in enumerate(data['pertemuan'])])
    
    prompt_text = f"""
    Buatlah RPP Kurikulum Merdeka. 
    Sekolah: {data['sekolah']}, Mapel: {data['mapel']}, Fase/Kelas: {data['fase']}.
    Materi: {data['materi']}. Tujuan: {data['tujuan']}.
    Rincian: {pertemuan_str}.
    
    FORMAT WAJIB: Gunakan HTML. Buat tabel untuk kegiatan pembelajaran. 
    Wajib ada tanda tangan: Kepala Sekolah (AHMAD JUNAIDI, S.Pd) & Guru (ANDY KURNIAWAN, S.Pd.SD).
    Berikan hasil langsung kodenya saja tanpa penjelasan pembuka.
    """

    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=40)
        res_json = response.json()
        
        if 'candidates' in res_json:
            teks = res_json['candidates'][0]['content']['parts'][0]['text']
            # Membersihkan tag markdown agar HTML terbaca oleh Streamlit
            clean_html = teks.replace("```html", "").replace("```", "").strip()
            return clean_html
        else:
            error_msg = res_json.get('error', {}).get('message', 'Model Tidak Mendukung')
            return f"<div style='color:red; background:white; padding:10px;'><b>Sistem AI Berkata:</b> {error_msg}</div>"
            
    except Exception as e:
        return f"<div style='color:red; background:white; padding:10px;'><b>Masalah Koneksi:</b> {str(e)}</div>"

# ==============================
# 4. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Versi 1.5 Flash - Stabil</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Nama Sekolah", "SDN ...")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with c2:
        fase = st.text_input("Fase / Kelas", "B / IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 5, 1)
    
    materi = st.text_area("Materi Utama")
    tujuan = st.text_area("Tujuan Pembelajaran")
    
    pertemuan_data = []
    for i in range(int(jml)):
        st.markdown(f"**Pertemuan {i+1}**")
        col1, col2 = st.columns(2)
        with col1: m = st.selectbox(f"Model P{i+1}", ["PBL", "PjBL", "Discovery"], key=f"m{i}")
        with col2: w = st.text_input(f"Waktu P{i+1}", "2x35m", key=f"w{i}")
        pertemuan_data.append({"model": m, "waktu": w})
    
    submit = st.form_submit_button("🚀 SUSUN RPP SEKARANG")

if submit:
    with st.spinner("AI sedang menulis RPP Anda..."):
        data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
        hasil_rpp = generate_rpp_direct(data_input)
        
        if "Sistem AI Berkata" in hasil_rpp:
            st.markdown(hasil_rpp, unsafe_allow_html=True)
            st.warning("Tips: Pastikan API Key di Secrets sudah menggunakan Key terbaru yang dibuat di AI Studio.")
        else:
            st.success("✅ RPP BERHASIL DISUSUN!")
            st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
            st.markdown(hasil_rpp, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.info("💡 Salin hasil di atas ke Microsoft Word untuk dicetak.")

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 RPP Generator Pro | Andy Kurniawan, S.Pd.SD</p>", unsafe_allow_html=True)
