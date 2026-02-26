import streamlit as st
import google.generativeai as genai
from io import BytesIO
from docx import Document
from docx.shared import Pt
from bs4 import BeautifulSoup

# ==============================
# 1. KONFIGURASI HALAMAN
# ==============================
st.set_page_config(page_title="RPP Generator Pro - Andy Kurniawan", page_icon="📄", layout="wide")

# CSS Custom
st.markdown("""
    <style>
    .stApp { background-color: #f0f7ff; }
    .main-title { color: #1e3a8a; text-align: center; padding: 20px; background: white; border-radius: 15px; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    [data-testid="stForm"] { background-color: #ffffff; padding: 30px; border-radius: 15px; border: 2px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. SECRETS & API
# ==============================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "12345")

if not GEMINI_API_KEY:
    st.error("❌ API KEY belum diisi di menu Secrets Streamlit!")
    st.stop()

# ==============================
# 3. LOGIN
# ==============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'><h1>🔐 Akses Guru RPP Pro</h1></div>", unsafe_allow_html=True)
    pwd = st.text_input("Masukkan Kode Akses", type="password")
    if st.button("Masuk"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Kode akses salah")
    st.stop()

# ==============================
# 4. FUNGSI EKSPOR WORD
# ==============================
def create_word(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    for el in soup.find_all(["h1", "h2", "h3", "p", "table"]):
        if el.name in ["h1", "h2", "h3"]:
            doc.add_heading(el.get_text(), level=2)
        elif el.name == "p":
            doc.add_paragraph(el.get_text())
        elif el.name == "table":
            rows = el.find_all("tr")
            if not rows: continue
            table = doc.add_table(rows=len(rows), cols=0)
            table.style = "Table Grid"
            
            # Hitung kolom maksimum
            max_cols = 0
            for r in rows:
                cols = r.find_all(["td", "th"])
                max_cols = max(max_cols, len(cols))
            
            for _ in range(max_cols): table.add_column(Pt(100))

            for i, row in enumerate(rows):
                cells = row.find_all(["td", "th"])
                for j, cell in enumerate(cells):
                    table.cell(i, j).text = cell.get_text(strip=True)
                    
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==============================
# 5. GENERATE RPP
# ==============================
def generate_rpp(data):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    pertemuan_str = "\n".join([f"P{i+1}: {p['model']} ({p['tanggal']})" for i, p in enumerate(data['pertemuan'])])
    
    prompt = f"""
    Buatlah RPP Kurikulum Merdeka Lengkap dalam format HTML.
    Sekolah: {data['sekolah']}, Mapel: {data['mapel']}, Fase: {data['fase']}.
    Materi: {data['materi']}, Tujuan: {data['tujuan']}.
    Detail Pertemuan: {pertemuan_str}.
    Wajib ada: Tabel Kegiatan (Langkah, Deskripsi, Waktu), Asesmen, dan Tanda Tangan.
    """
    response = model.generate_content(prompt)
    return response.text.replace("```html", "").replace("```", "").strip()

# ==============================
# 6. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>Andalan Guru - Andy Kurniawan, S.Pd.SD</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Nama Sekolah", "SDN")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with c2:
        fase = st.text_input("Fase/Kelas", "B/IV")
        jml = st.number_input("Jumlah Pertemuan", 1, 15, 1)
    
    materi = st.text_area("Ringkasan Materi")
    tujuan = st.text_area("Tujuan Pembelajaran")
    
    pertemuan_data = []
    for i in range(int(jml)):
        col1, col2 = st.columns(2)
        with col1:
            m = st.selectbox(f"Model P{i+1}", ["PBL", "PjBL", "Discovery", "Inquiry", "DLL"], key=f"m{i}")
        with col2:
            t = st.date_input(f"Tanggal P{i+1}", key=f"t{i}")
        pertemuan_data.append({"model": m, "tanggal": t.strftime("%d/%m/%Y")})
    
    submit = st.form_submit_button("🚀 BUAT RPP SEKARANG")

if submit:
    with st.spinner("Sedang memproses..."):
        data = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
        hasil_html = generate_rpp(data)
        
        st.success("✅ Berhasil!")
        st.html(hasil_html)
        
        file_docx = create_word(hasil_html)
        st.download_button("📥 Download File Word (.docx)", file_docx, "RPP_Andy_Kurniawan.docx")
