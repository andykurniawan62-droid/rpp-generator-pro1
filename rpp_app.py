import streamlit as st
import google.generativeai as genai

# ==============================
# 1. KONFIGURASI HALAMAN & CSS
# ==============================
st.set_page_config(page_title="AI RPP Generator Pro", page_icon="📝", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* STYLE KERTAS RPP */
    .rpp-paper { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        padding: 40px 60px; 
        font-family: 'Times New Roman', Times, serif;
        font-size: 11pt;
        line-height: 1.4;
        border-radius: 2px;
    }
    
    .rpp-paper h1, .rpp-paper h2 { text-align: center; text-transform: uppercase; color: #000; margin-bottom: 5px; }
    .rpp-paper table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
    .rpp-paper th, .rpp-paper td { border: 1px solid black; padding: 5px 8px; color: #000; vertical-align: top; }
    
    /* CSS KHUSUS TANDA TANGAN RAPAT */
    .rpp-paper .no-border, .rpp-paper .no-border td { border: none !important; padding: 2px 0; }
    .sig-container { margin-top: 30px; }
    .name-line { font-weight: bold; text-decoration: underline; margin-bottom: 0px; padding-bottom: 0px; }
    .nip-line { margin-top: -5px; padding-top: 0px; font-size: 10pt; }

    /* Mencegah Tabel Terpotong di Tengah Halaman saat PDF */
    table { page-break-inside: auto; }
    tr { page-break-inside: avoid; page-break-after: auto; }

    @media print {
        header, footer, .stSidebar, .stButton, .stForm, .main-header, [data-testid="stHeader"] { display: none !important; }
        .stApp { background-color: white !important; }
        .rpp-paper { box-shadow: none; border: none; padding: 0; margin: 0; width: 100%; }
        @page { size: auto; margin: 1.5cm; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# 2. SISTEM API
# ==============================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    st.error("⚠️ API Key tidak ditemukan!")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

# ==============================
# 3. UI INPUT
# ==============================
st.markdown(f"""
    <div class="main-header" style="background-color:#007BFF;padding:15px;border-radius:10px;text-align:center;margin-bottom:15px;">
        <h2 style="color:white;margin:0;">AI RPP GENERATOR PRO</h2>
        <p style="color:white;margin:5px;">Layanan Cepat RPP Kurikulum Merdeka - Andy Kurniawan</p>
    </div>
""", unsafe_allow_html=True)

with st.form("main_form"):
    st.subheader("🏢 Data Administrasi")
    col1, col2 = st.columns(2)
    with col1:
        nama_sekolah = st.text_input("Nama Sekolah", "SD Negeri ...")
        nama_kepsek = st.text_input("Nama Kepala Sekolah")
        nip_kepsek = st.text_input("NIP Kepala Sekolah")
    with col2:
        nama_guru = st.text_input("Nama Guru")
        nip_guru = st.text_input("NIP Guru")
        mapel = st.text_input("Mata Pelajaran")

    st.subheader("🌟 Dimensi Profil Lulusan")
    c_prof1, c_prof2 = st.columns(2)
    with c_prof1:
        p1 = st.checkbox("Beriman, Bertakwa Kepada Tuhan YME")
        p2 = st.checkbox("Kewargaan (Berkebinekaan Global)")
        p3 = st.checkbox("Penalaran Kritis")
        p4 = st.checkbox("Kreativitas")
    with c_prof2:
        p5 = st.checkbox("Gotong Royong (Kolaborasi)")
        p6 = st.checkbox("Kemandirian")
        p7 = st.checkbox("Kesehatan (Jasmani/Rohani)")
        p8 = st.checkbox("Komunikasi (Sosial)")

    profil_list = [v for k, v in {
        "Beriman & Bertakwa YME": p1, "Berkebinekaan Global": p2, 
        "Bernalar Kritis": p3, "Kreatif": p4, "Gotong Royong": p5, 
        "Mandiri": p6, "Kesehatan": p7, "Komunikasi": p8
    }.items() if k]
    
    st.subheader("📖 Rincian Pembelajaran")
    fase = st.text_input("Fase/Kelas", "Fase B / Kelas 4")
    materi = st.text_area("Materi Pokok")
    
    btn_generate = st.form_submit_button("🚀 GENERATE RPP")

# ==============================
# 4. PROSES AI
# ==============================
if btn_generate:
    profil_str = ", ".join([p for p in profil_list])
    
    prompt = f"""
    Buat RPP Kurikulum Merdeka dalam HTML murni (TANPA ```html).
    Data: Sekolah {nama_sekolah}, Guru {nama_guru}, Kepsek {nama_kepsek}, Mapel {mapel}, Materi {materi}.
    Dimensi Profil: {profil_str}.
    
    FORMAT WAJIB:
    1. Pakai Tabel No-Border untuk Identitas (Sekolah, Kelas, Semester, Materi, Alokasi Waktu).
    2. Bagian Langkah Pembelajaran pakai Tabel Border 1px.
    3. Bagian Tanda Tangan WAJIB Mengikuti Struktur Ini:
       <table class="no-border" style="width:100%; margin-top:40px;">
         <tr>
           <td style="width:50%;">Mengetahui,<br>Kepala Sekolah</td>
           <td style="width:50%;">Jombang, ................... 2026<br>Guru Mata Pelajaran</td>
         </tr>
         <tr style="height:70px;"><td></td><td></td></tr>
         <tr>
           <td>
             <div class="name-line">{nama_kepsek}</div>
             <div class="nip-line">NIP. {nip_kepsek}</div>
           </td>
           <td>
             <div class="name-line">{nama_guru}</div>
             <div class="nip-line">NIP. {nip_guru}</div>
           </td>
         </tr>
       </table>
    """

    model = genai.GenerativeModel('gemini-2.0-flash-001')
    with st.spinner("Sedang menyusun..."):
        response = model.generate_content(prompt)
        st.session_state.hasil_rpp = response.text

# ==============================
# 5. TAMPILAN HASIL & TOMBOL CETAK
# ==============================
if "hasil_rpp" in st.session_state:
    st.markdown("""
        <button onclick="window.print()" style="width:100%; padding:12px; background-color:#28a745; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; margin-bottom:10px;">
            📥 DOWNLOAD SEBAGAI PDF (CETAK)
        </button>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="rpp-paper">{st.session_state.hasil_rpp}</div>', unsafe_allow_html=True)

st.caption("© 2026 AI RPP Pro - Andy Kurniawan")
