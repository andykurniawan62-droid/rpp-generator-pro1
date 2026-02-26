import streamlit as st
import requests
import json
from io import BytesIO
from docx import Document
from docx.shared import Pt
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
    .meeting-card { background-color: #1e3a8a; padding: 10px 15px; border-radius: 8px; margin-top: 20px; color: white; }
    .preview-box { background-color: #ffffff; color: #000000; padding: 40px; border-radius: 10px; margin-top: 20px; }
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
    st.markdown("<div class='main-title'><h1>🔐 Akses Guru RPP Pro</h1></div>", unsafe_allow_html=True)
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
# 3. FUNGSI EKSPOR WORD
# ==============================
def create_word(html_content):
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        doc = Document()
        for el in soup.find_all(["h1", "h2", "h3", "p", "table"]):
            if el.name in ["h1", "h2", "h3"]:
                doc.add_heading(el.get_text(), level=2)
            elif el.name == "p":
                doc.add_paragraph(el.get_text())
            elif el.name == "table":
                rows = el.find_all("tr")
                if not rows: continue
                table = doc.add_table(rows=len(rows), cols=len(rows[0].find_all(["td", "th"])))
                table.style = "Table Grid"
                for i, row in enumerate(rows):
                    for j, cell in enumerate(row.find_all(["td", "th"])):
                        table.cell(i, j).text = cell.get_text(strip=True)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except: return None

# ==============================
# 4. FUNGSI BYPASS API (DIRECT CALL)
# ==============================
def generate_rpp_direct(data):
    # Menggunakan endpoint v1 STABLE (Bukan Beta)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    pertemuan_str = "\n".join([f"P{i+1}: Model {p['model']}, Waktu {p['waktu']}, Tgl {p['tanggal']}" for i, p in enumerate(data['pertemuan'])])
    
    prompt_text = f"""
    Buatlah RPP Kurikulum Merdeka dalam format HTML (tabel border="1").
    Sekolah: {data['sekolah']}, Mapel: {data['mapel']}, Fase: {data['fase']}.
    Materi: {data['materi']}, Tujuan: {data['tujuan']}.
    Rincian: {pertemuan_str}
    Wajib: Tabel Kegiatan, Asesmen, dan Tanda Tangan: Kepala Sekolah (AHMAD JUNAIDI, S.Pd) & Guru (ANDY KURNIAWAN, S.Pd.SD).
    """

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        res_json = response.json()
        
        # Ambil teks dari struktur JSON Google
        if 'candidates' in res_json:
            hasil_ai = res_json['candidates'][0]['content']['parts'][0]['text']
            # Bersihkan markdown
            if "```html" in hasil_ai:
                hasil_ai = hasil_ai.split("```html")[1].split("```")[0]
            elif "```" in hasil_ai:
                hasil_ai = hasil_ai.split("```")[1].split("```")[0]
            return hasil_ai.strip()
        else:
            return f"<div style='color:red;'><b>API Google Error:</b> {res_json.get('error', {}).get('message', 'Unknown Error')}</div>"
            
    except Exception as e:
        return f"<div style='color:red;'><b>Gagal Koneksi:</b> {str(e)}</div>"

# ==============================
# 5. UI UTAMA
# ==============================
MODELS_LIST = ["PBL", "PjBL", "Discovery Learning", "Inquiry", "STAD", "Jigsaw", "Demonstrasi", "Ceramah"]

st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Versi Bypass Jalur Stabil</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Nama Sekolah", "SDN ...")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with c2:
        fase = st.text_input("Fase / Kelas", "B / IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 10, 1)
    
    materi = st.text_area("Materi Utama")
    tujuan = st.text_area("Tujuan Pembelajaran")
    
    pertemuan_data = []
    for i in range(int(jml)):
        st.markdown(f"<div class='meeting-card'>Pertemuan {i+1}</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: m = st.selectbox(f"Model P{i+1}", MODELS_LIST, key=f"m{i}")
        with col2: w = st.text_input(f"Waktu P{i+1}", "2x35 Menit", key=f"w{i}")
        with col3: t = st.date_input(f"Tgl P{i+1}", key=f"t{i}")
        pertemuan_data.append({"model": m, "waktu": w, "tanggal": t.strftime("%d/%m/%Y")})
    
    submit = st.form_submit_button("🚀 GENERATE RPP")

if submit:
    with st.spinner("Menembus blokir Google AI..."):
        data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
        hasil = generate_rpp_direct(data_input)
        
        if "API Google Error" in hasil or "Gagal Koneksi" in hasil:
            st.markdown(hasil, unsafe_allow_html=True)
        else:
            st.success("✅ AKHIRNYA BERHASIL!")
            st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
            st.html(hasil)
            st.markdown("</div>", unsafe_allow_html=True)
            
            file_docx = create_word(hasil)
            st.download_button("📥 Download Word", file_docx, f"RPP_{mapel}.docx")
