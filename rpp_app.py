import streamlit as st
import google.generativeai as genai
from io import BytesIO
from datetime import datetime
import PIL.Image

# PDF
from xhtml2pdf import pisa

# WORD
from docx import Document
from docx.shared import Pt
from bs4 import BeautifulSoup

# ==============================
# 1. KONFIGURASI HALAMAN
# ==============================
st.set_page_config(
    page_title="RPP Generator Pro - Andy Kurniawan",
    layout="wide"
)

# ==============================
# 2. SECRETS & KONFIGURASI API
# ==============================
# Jika menjalankan lokal, pastikan isi secrets.toml atau ganti string kosong di bawah
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "12345")

if not GEMINI_API_KEY:
    st.error("❌ API KEY tidak ditemukan. Pastikan sudah diatur di .streamlit/secrets.toml")
    st.stop()

# ==============================
# 3. LOGIN SEDERHANA
# ==============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Akses Guru")
    pwd = st.text_input("Masukkan Kode Akses", type="password")
    if st.button("Masuk"):
        if pwd == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Kode akses salah")
    st.stop()

# ==============================
# 4. FUNGSI EKSPOR (PDF & WORD)
# ==============================
def create_pdf(html_content):
    result = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode("utf-8")), dest=result)
    return result.getvalue()

def create_word(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)

    for el in soup.find_all(["h3", "p", "table"]):
        if el.name == "h3":
            doc.add_heading(el.get_text(strip=True), level=2)
        elif el.name == "p":
            doc.add_paragraph(el.get_text(strip=True))
        elif el.name == "table":
            rows = el.find_all("tr")
            if not rows: continue
            max_cols = max(len(r.find_all(["td", "th"])) for r in rows)
            table = doc.add_table(rows=len(rows), cols=max_cols)
            table.style = "Table Grid"
            for i, row in enumerate(rows):
                cells = row.find_all(["td", "th"])
                for j in range(max_cols):
                    text = cells[j].get_text(strip=True) if j < len(cells) else ""
                    table.cell(i, j).text = text
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# ==============================
# 5. FUNGSI GENERATE RPP (AI)
# ==============================
def generate_rpp(data, uploaded_file=None):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    detail_pertemuan = ""
    for i, ptm in enumerate(data["pertemuan"]):
        detail_pertemuan += f"Pertemuan {i+1} ({ptm['tanggal']}): Model {ptm['model']} - Durasi {ptm['waktu']}.\n"

    prompt = f"""
Buatlah RPP Kurikulum Merdeka dalam format HTML MURNI tanpa markdown (tanpa tanda ```).

IDENTITAS:
Sekolah: {data['sekolah']} | Mapel: {data['mapel']} | Kelas: {data['fase']}
Materi: {data['materi']}
Tujuan: {data['tujuan']}

DETAIL PERTEMUAN:
{detail_pertemuan}

STRUKTUR HTML WAJIB:
1. Header Identitas (tabel tanpa border).
2. Per Pertemuan wajib ada Tabel Kegiatan: LANGKAH | RINCIAN KEGIATAN | WAKTU.
3. Gunakan sintaks model pembelajaran yang dipilih (contoh: PBL harus ada Orientasi Masalah).
4. Sertakan tabel Asesmen (Diagnostik, Formatif, Sumatif) dan Rubrik Nilai.
5. Gunakan pendekatan 3M (Memahami, Mengaplikasi, Merefleksi).
6. Tanda Tangan di akhir: Kepala Sekolah (AHMAD JUNAIDI, S.Pd) dan Guru (ANDY KURNIAWAN, S.Pd.SD).
"""

    response = model.generate_content([prompt])
    return response.text.replace("```html", "").replace("```", "").strip()

# ==============================
# 6. ANTARMUKA PENGGUNA (UI)
# ==============================
st.title("📄 RPP GENERATOR PRO - ANDY KURNIAWAN")
st.caption("Edisi 2026 • Kurikulum Merdeka • Mendukung 15 Model Pembelajaran")

MODELS_LIST = [
    "Discovery Learning", "Inquiry Learning", "Problem Based Learning (PBL)",
    "Project Based Learning (PjBL)", "Contextual Teaching (CTL)",
    "Cooperative Learning (Jigsaw)", "Cooperative Learning (STAD)",
    "Demonstrasi & Eksperimen", "Direct Instruction", "Role Playing",
    "Numbered Head Together (NHT)", "Mind Mapping", "Talking Stick",
    "Game Based Learning (PJOK)", "Inside Outside Circle"
]

with st.sidebar:
    st.header("Konfigurasi")
    ref_file = st.file_uploader("Upload Materi/Gambar (Opsional)", type=["jpg","png","pdf"])

with st.form("main_form"):
    col_a, col_b = st.columns(2)
    with col_a:
        sekolah = st.text_input("Nama Sekolah", "SD Negeri 1 Merdeka")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with col_b:
        fase = st.text_input("Fase / Kelas / Sem", "B / IV / 1")
        jml = st.number_input("Jumlah Pertemuan", 1, 15, 1)

    st.divider()
    
    pertemuan_data = []
    for i in range(int(jml)):
        st.write(f"**Pertemuan {i+1}**")
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            m_ptm = st.selectbox(f"Model Ptm {i+1}", MODELS_LIST, key=f"m_{i}")
        with c2:
            w_ptm = st.text_input(f"Waktu Ptm {i+1}", "2 x 35 Menit", key=f"w_{i}")
        with c3:
            t_ptm = st.date_input(f"Tanggal Ptm {i+1}", key=f"t_{i}")
        
        pertemuan_data.append({
            "model": m_ptm, 
            "waktu": w_ptm, 
            "tanggal": t_ptm.strftime("%d/%m/%Y")
        })

    materi = st.text_area("Ringkasan Materi")
    tujuan = st.text_area("Tujuan Pembelajaran")
    
    submit = st.form_submit_button("🚀 Generate RPP Sekarang")

# ==============================
# 7. PROSES & OUTPUT
# ==============================
if submit:
    if not materi or not tujuan:
        st.warning("⚠️ Mohon lengkapi Materi dan Tujuan.")
    else:
        with st.spinner("Menyusun RPP..."):
            data_rpp = {
                "sekolah": sekolah, "mapel": mapel, "fase": fase,
                "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data
            }
            
            html_res = generate_rpp(data_rpp, ref_file)
            
            st.success("✅ RPP Selesai Dibuat!")
            st.html(html_res) # Preview

            # File Generation
            full_html = f"<html><style>body{{font-family:'Times New Roman';}} table{{width:100%; border-collapse:collapse;}} td{{border:1px solid black; padding:5px;}}</style><body>{html_res}</body></html>"
            
            pdf_file = create_pdf(full_html)
            word_file = create_word(html_res)

            c_dl1, c_dl2 = st.columns(2)
            with c_dl1:
                st.download_button("📥 Download PDF", pdf_file, "RPP.pdf", "application/pdf")
            with c_dl2:
                st.download_button("📄 Download Word", word_file, "RPP.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.caption("© 2026 RPP Generator Pro | Andy Kurniawan, S.Pd.SD")