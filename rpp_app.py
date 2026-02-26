import streamlit as st
import google.generativeai as genai
from io import BytesIO
from docx import Document
from docx.shared import Pt
from bs4 import BeautifulSoup

# ==============================
# 1. KONFIGURASI HALAMAN & TEMA HITAM
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
    label, .stMarkdown p, .stSelectbox label { color: #ffffff !important; font-weight: bold; }
    .meeting-card { background-color: #1e3a8a; padding: 10px 15px; border-radius: 8px; margin-top: 20px; color: white; font-weight: bold; }
    input, textarea, [data-baseweb="select"] { background-color: #222222 !important; color: white !important; }
    .preview-box { background-color: #ffffff; color: #000000; padding: 40px; border-radius: 10px; margin-top: 20px; border: 1px solid #ccc; }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. SECRETS & API
# ==============================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "12345")

# ==============================
# 3. LOGIN SYSTEM
# ==============================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<div class='main-title'><h1>🔐 Akses Guru RPP Pro</h1><p>Gunakan password untuk masuk</p></div>", unsafe_allow_html=True)
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
# 4. FUNGSI EKSPOR WORD
# ==============================
def create_word(html_content):
    try:
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
                max_cols = 0
                for r in rows:
                    max_cols = max(max_cols, len(r.find_all(["td", "th"])))
                table = doc.add_table(rows=len(rows), cols=max_cols)
                table.style = "Table Grid"
                for i, row in enumerate(rows):
                    cells = row.find_all(["td", "th"])
                    for j, cell in enumerate(cells):
                        if j < max_cols:
                            table.cell(i, j).text = cell.get_text(strip=True)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except:
        return None

# ==============================
# 5. FUNGSI GENERATE RPP (V1 STABLE FIX)
# ==============================
def generate_rpp(data):
    if not GEMINI_API_KEY:
        return "<p style='color:red;'>Error: API KEY tidak ditemukan!</p>"
    
    try:
        # Konfigurasi API Dasar
        genai.configure(api_key=GEMINI_API_KEY)
        
        # FIX: Gunakan inisialisasi model yang memaksa penggunaan jalur stabil
        # Jika 'gemini-1.5-flash' gagal, kita langsung lompat ke daftar model cadangan
        model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        model = None
        for name in model_names:
            try:
                model = genai.GenerativeModel(model_name=name)
                # Tes panggil singkat untuk memastikan model tersedia
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                break
            except:
                continue

        if not model:
            return "<p style='color:red;'>Semua model AI sedang sibuk atau tidak tersedia di wilayah Anda.</p>"
        
        pertemuan_str = "\n".join([f"P{i+1}: Model {p['model']}, Waktu {p['waktu']}, Tgl {p['tanggal']}" for i, p in enumerate(data['pertemuan'])])
        
        prompt = f"""
        Buatlah RPP Kurikulum Merdeka Profesional dalam format HTML (tabel dengan border="1").
        IDENTITAS: Sekolah: {data['sekolah']}, Mapel: {data['mapel']}, Fase: {data['fase']}.
        KONTEN: Materi: {data['materi']}, Tujuan: {data['tujuan']}.
        RINCIAN: {pertemuan_str}
        SYARAT WAJIB:
        1. Identitas lengkap di awal.
        2. Tabel kegiatan (Langkah, Deskripsi, Waktu) per pertemuan.
        3. Bagian Asesmen dan Media Pembelajaran.
        4. Tanda Tangan: Kepala Sekolah (AHMAD JUNAIDI, S.Pd) dan Guru (ANDY KURNIAWAN, S.Pd.SD).
        """
        
        response = model.generate_content(prompt)
        return response.text.replace("```html", "").replace("```", "").strip()

    except Exception as e:
        return f"""
        <div style='color:red; background:white; padding:15px; border:2px solid red; border-radius:10px;'>
        <b>SERVER AI MENOLAK (Error 404):</b><br>
        <i>Detail: {str(e)}</i><br><br>
        <b>SOLUSI TERAKHIR:</b><br>
        1. Buka <a href='https://aistudio.google.com/'>Google AI Studio</a>.<br>
        2. Klik tombol "Get API Key" dan buat <b>API Key Baru</b> di Project baru.<br>
        3. Kadang satu akun Google bisa terkena pembatasan, cobalah gunakan <b>Akun Gmail Lain</b> untuk membuat Key baru.<br>
        4. Simpan di Secrets Streamlit dan pilih <b>REBOOT APP</b>.
        </div>
        """

# ==============================
# 6. DAFTAR MODEL PEMBELAJARAN
# ==============================
MODELS_LIST = [
    "Problem Based Learning (PBL)", "Project Based Learning (PjBL)", 
    "Discovery Learning", "Inquiry Learning", "Contextual Teaching (CTL)",
    "Cooperative Learning (Jigsaw)", "Cooperative Learning (STAD)",
    "Demonstrasi & Eksperimen", "Direct Instruction (Ceramah)", 
    "Role Playing (Bermain Peran)", "Numbered Head Together (NHT)", 
    "Mind Mapping", "Talking Stick", "Game Based Learning (PJOK/Umum)", 
    "Inside Outside Circle", "Example Non-Example", "Think Pair Share (TPS)",
    "Problem Solving (PAI/Agama)", "Kisah Keteladanan (Agama)", "Praktik Lapangan (Olahraga)"
]

# ==============================
# 7. UI UTAMA
# ==============================
st.markdown("<div class='main-title'><h1>📄 RPP GENERATOR PRO</h1><p>By Andy Kurniawan, S.Pd.SD</p></div>", unsafe_allow_html=True)

with st.form("rpp_form"):
    st.subheader("📋 Identitas RPP")
    c1, c2 = st.columns(2)
    with c1:
        sekolah = st.text_input("Nama Sekolah", "SDN ...")
        mapel = st.text_input("Mata Pelajaran", "PJOK")
    with c2:
        fase = st.text_input("Fase / Kelas", "B / IV")
        jml = st.number_input("Jumlah Pertemuan (Maks 15)", 1, 15, 1)
    
    st.divider()
    materi = st.text_area("Materi Utama")
    tujuan = st.text_area("Tujuan Pembelajaran (TP)")
    
    pertemuan_data = []
    for i in range(int(jml)):
        st.markdown(f"<div class='meeting-card'>Pertemuan Ke-{i+1}</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            m = st.selectbox(f"Model P{i+1}", MODELS_LIST, key=f"m{i}")
        with col2:
            w = st.text_input(f"Waktu P{i+1}", "2 x 35 Menit", key=f"w{i}")
        with col3:
            t = st.date_input(f"Tanggal P{i+1}", key=f"t{i}")
        pertemuan_data.append({"model": m, "waktu": w, "tanggal": t.strftime("%d/%m/%Y")})
    
    submit = st.form_submit_button("🚀 GENERATE RPP")

if submit:
    if not materi or not tujuan:
        st.error("Isi Materi dan Tujuan terlebih dahulu!")
    else:
        with st.spinner("AI sedang memproses RPP Anda..."):
            data_input = {"sekolah": sekolah, "mapel": mapel, "fase": fase, "materi": materi, "tujuan": tujuan, "pertemuan": pertemuan_data}
            hasil_html = generate_rpp(data_input)
            
            if "SERVER AI MENOLAK" in hasil_html:
                st.markdown(hasil_html, unsafe_allow_html=True)
            else:
                st.success("✅ RPP Berhasil Dibuat!")
                st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
                st.html(hasil_html)
                st.markdown("</div>", unsafe_allow_html=True)
                
                file_docx = create_word(hasil_html)
                if file_docx:
                    st.download_button("📥 Download Word", file_docx, f"RPP_{mapel}.docx")

st.markdown("<br><p style='text-align: center; color: #555;'>© 2026 RPP Generator Pro | Andy Kurniawan, S.Pd.SD</p>", unsafe_allow_html=True)
