# ==============================
# 5. LOGIKA GENERATE (DENGAN URUTAN MODEL SESUAI PERMINTAAN)
# ==============================
if btn_generate:
    if not nama_sekolah or not materi_pokok:
        st.warning("⚠️ Mohon lengkapi Data Sekolah dan Materi!")
    else:
        # URUTAN SESUAI PERMINTAAN PAK ANDY:
        # 1. 2.0-flash-001 (Utama)
        # 2. 2.5-flash (Cadangan 1)
        # 3. 1.5-flash (Cadangan 2)
        model_options = [
            'gemini-2.0-flash-001', 
            'gemini-2.5-flash', 
            'gemini-1.5-flash'
        ]
        
        # ... (proses penyiapan profil_str dan jadwal_detail tetap sama) ...

        success = False
        for current_model_name in model_options:
            try:
                with st.spinner(f"Menyusun RPP dengan {current_model_name}..."):
                    model = genai.GenerativeModel(current_model_name)
                    response = model.generate_content(prompt)
                    
                    if response.text:
                        # Jika berhasil, simpan hasil dan berhenti mencoba model lain
                        st.session_state.usage_count += 1
                        st.session_state.hasil_rpp = response.text.replace("```html", "").replace("```", "").strip()
                        success = True
                        break 
            except Exception as e:
                # Jika terkena Limit (Error 429), tampilkan peringatan dan lanjut ke model berikutnya
                if "429" in str(e):
                    st.info(f"💡 Jalur {current_model_name} sedang limit, otomatis pindah ke jalur berikutnya...")
                    continue 
                else:
                    st.error(f"Gagal di jalur {current_model_name}: {e}")
                    # Jika errornya bukan karena limit (misal: sinyal), kita coba model berikutnya juga
                    continue

        if not success:
            st.error("⚠️ Semua jalur (2.0, 2.5, dan 1.5) sedang sibuk. Mohon tunggu beberapa saat.")
