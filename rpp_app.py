import streamlit as st
import google.generativeai as genai

# --- KONFIGURASI API KEY LANGSUNG ---
GEMINI_API_KEY = "AIzaSyB-nk0E9Laiqg5x6rI7m6tNoqWMLSSDn7Q"

# Konfigurasi model Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- TAMPILAN APLIKASI ---
st.set_page_config(page_title="AI RPP Generator Pro", layout="wide")

st.title("📝 AI RPP Generator Pro")
st.subheader("Buat Rencana Pelaksanaan Pembelajaran dalam Hitungan Detik")

with st.sidebar:
    st.header("Parameter RPP")
    mata_pelajaran = st.text_input("Mata Pelajaran", placeholder="Contoh: Matematika")
    kelas = st.text_input("Kelas/Semester", placeholder="Contoh: X / Ganjil")
    materi_pokok = st.text_area("Materi Pokok", placeholder="Contoh: Persamaan Linear Satu Variabel")
    alokasi_waktu = st.text_input("Alokasi Waktu", placeholder="Contoh: 2 x 45 Menit")

# Tombol Generate
if st.button("Generate RPP Sekarang"):
    if not mata_pelajaran or not materi_pokok:
        st.warning("Mohon isi Mata Pelajaran dan Materi Pokok terlebih dahulu!")
    else:
        try:
            with st.spinner("Sedang menyusun RPP... Mohon tunggu."):
                # Membuat Prompt (Instruksi) untuk AI
                prompt = f"""
                Buatlah Rencana Pelaksanaan Pembelajaran (RPP) yang lengkap dan profesional dengan format berikut:
                1. Identitas (Mata Pelajaran: {mata_pelajaran}, Kelas: {kelas}, Alokasi Waktu: {alokasi_waktu})
                2. Tujuan Pembelajaran
                3. Materi Pembelajaran ({materi_pokok})
                4. Metode Pembelajaran
                5. Langkah-langkah Kegiatan (Pendahuluan, Inti, Penutup)
                6. Penilaian (Asesmen)
                
                Gunakan bahasa Indonesia yang formal dan mudah dipahami.
                """
                
                # Memanggil Gemini
                response = model.generate_content(prompt)
                
                # Menampilkan Hasil
                st.success("✅ RPP Berhasil Dibuat!")
                st.markdown("---")
                st.markdown(response.text)
                
                # Fitur Download (Opsional)
                st.download_button(
                    label="Unduh RPP (Txt)",
                    data=response.text,
                    file_name=f"RPP_{mata_pelajaran}.txt",
                    mime="text/plain"
                )
                
        except Exception as e:
            st.error("Terjadi kesalahan saat menghubungi server Google.")
            st.info(f"Detail Error: {e}")

# Footer
st.markdown("---")
st.caption("Dibuat dengan ❤️ menggunakan Google Gemini AI")
