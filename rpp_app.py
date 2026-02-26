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
    
    /* Style Khusus Preview RPP agar Putih Bersih seperti Kertas */
    .preview-box { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 50px; 
        border-radius: 5px; 
        margin-top: 20px; 
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
    }
    .preview-box h1, .preview-box h2, .preview-box h3, .preview-box h4 { color: #000000 !important; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .preview-box table { border-collapse: collapse; width: 100%; margin-bottom: 20px; color: #000000 !important; }
    .preview-box th, .preview-box td { border: 1px solid #000 !important; padding: 10px; text-align: left; vertical-align: top; }
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
# 3. FUNGSI GENERATE (OPTIMAL PROMPT)
# ==============================
def generate_rpp_final(data):
    # Menggunakan model 1.5-flash di jalur v1beta (paling update 2026)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    pertemuan_str = "\n".join([f"P{i+1}: Model {p['model']}, Waktu {p['waktu']}" for i, p in enumerate(data['pertemuan'])])
    
    prompt_text = f"""
    Buatlah RPP Kurikulum Merdeka Lengkap.
    PENTING: Jangan gunakan teks dalam kurung siku seperti [Nama Sekolah]. Gunakan data asli di bawah ini.
    
    DATA IDENTITAS:
    Satuan Pendidikan: {data['sekolah']}
    Mata Pelajaran: {data['mapel']}
    Fase/Kelas: {data['fase']}
    Materi Utama: {data['materi']}
    Tujuan Pembelajaran: {data['tujuan']}
    Rincian Pertemuan: {pertemuan_str}
    
    STRUKTUR OUTPUT HTML:
    1. Judul Besar: RENCANA PELAKSANAAN PEMBELAJARAN (RPP).
    2. Tabel Identitas (Tanpa border luar jika bisa, tapi isi jelas).
    3. Tujuan Pembelajaran (list).
    4. Langkah Pembelajaran (Pendahuluan, Inti, Penutup) buat dalam TABEL 3 Kolom: No, Kegiatan, Alokasi Waktu.
    5. Asesmen, Refleksi Guru, dan Refleksi Murid.
    6. BAGIAN TANDA TANGAN (Sangat Penting): 
       Buat tabel 2 kolom tanpa border. 
       Kolom Kiri: Mengetahui, Kepala Sekolah ({data['sekolah']}), (kosongkan ruang tanda tangan), AHMAD JUNAIDI, S.Pd.
       Kolom Kanan: (Tempat/Tanggal hari ini), Guru Kelas IV, (kosongkan ruang tanda tangan), ANDY KURNIAWAN, S.Pd.SD.
    
    Gunakan Tag HTML murni. Pastikan tabel kegiatan memiliki atribut border="1".
    """

    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        res_json = response.json()
        if 'candidates' in res_json:
            teks = res_json['candidates'][0]['content']['parts'][0]['text']
            return teks.replace("```html", "").replace("```", "").strip()
        else:
            return f"<p style='color:red;'>Gagal: {res_json.get('error', {}).get('message', 'Cek API Key')}</p>"
    except Exception as e:
        return f"<p style='color:red;'>Error: {str(e)}</p>"

# ==============================
# 4. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Versi Sempurna - Andy Kurniawan</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Nama Sekolah Lengkap", "SDN ...")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with c2:
        fase = st.text_input("Fase / Kelas", "B / IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 3, 1)
    
    materi = st.text_area("Materi Utama")
    tujuan = st.text_area("Tujuan Pembelajaran")
    
    pertemuan_data = []
    for i in range(int(jml)):
        st.markdown(f"**Pertemuan {i+1}**")
        col1, col2 = st.columns(2)
        with col1: m = st.selectbox(f"Model P{i+1}", ["Problem Based Learning", "Project Based Learning", "Discovery Learning"], key=f"m{i}")
        with col2: w = st.text_input(f"Waktu P{i+1}", "2x35 Menit", key=f"w{i}")
        pertemuan_data.append({"model": m, "waktu": w})
    
    submit = st.form_submit_button("🚀 GENERATE RPP SEMPURNA")

if submit:
    with st.spinner("AI sedang merancang RPP profesional untuk Anda..."):
        data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
        hasil = generate_rpp_final(data_input)
        
        st.success("✅ RPP SIAP!")
        st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
        st.markdown(hasil, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.info("💡 TIPS: Tekan Ctrl+P di keyboard Anda untuk mencetak RPP ini langsung ke PDF.")

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 RPP Generator Pro | By Andy Kurniawan, S.Pd.SD</p>", unsafe_allow_html=True)
