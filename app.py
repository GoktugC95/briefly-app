import streamlit as st
import PyPDF2 as pdf
import requests
import json
import time

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Briefly | AI Asistan", page_icon="⚡", layout="wide")

# --- CSS TASARIM ---
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .success-box { padding: 1rem; background-color: #d4edda; color: #155724; border-radius: 8px; }
    .warning-box { padding: 1rem; background-color: #fff3cd; color: #856404; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- OTURUM YÖNETİMİ (HAFIZA) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_plan' not in st.session_state:
    st.session_state['user_plan'] = 'free' 
if 'username' not in st.session_state:
    st.session_state['username'] = ''  # Kullanıcı adını burada saklayacağız

# --- FONKSİYONLAR ---

def get_pdf_info(uploaded_file):
    """PDF metnini ve sayfa sayısını alır."""
    text = ""
    reader = pdf.PdfReader(uploaded_file)
    num_pages = len(reader.pages)
    for page in range(num_pages):
        page_text = reader.pages[page].extract_text()
        if page_text:
            text += page_text
    return text, num_pages

def find_flash_model(api_key):
    """Flash modelini otomatik bulur."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            models = response.json().get('models', [])
            for m in models:
                if 'flash' in m['name'] and 'generateContent' in m['supportedGenerationMethods']:
                    return m['name']
            return "models/gemini-1.5-flash" 
    except:
        return "models/gemini-1.5-flash"

def generate_content(api_key, model_name, prompt, text_content):
    """Gemini API İsteği."""
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    full_prompt = f"{prompt}\n\n---\nMetin:\n{text_content}"
    data = {"contents": [{"parts": [{"text": full_prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Hata ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Hata: {str(e)}"

# --- YAN MENÜ ---
with st.sidebar:
    st.title("⚡ Briefly")
    
    api_key = st.text_input("Google API Anahtarı:", type="password")
    
    st.markdown("---")
    
    # GİRİŞ EKRANI
    if not st.session_state['logged_in']:
        st.subheader("👤 Üye Girişi")
        # Buradaki değişken ismini değiştirdik
        user_input = st.text_input("Kullanıcı Adı") 
        pass_input = st.text_input("Şifre", type="password")
        
        if st.button("Giriş Yap"):
            if user_input == "demo" and pass_input == "123":
                st.session_state['logged_in'] = True
                st.session_state['user_plan'] = 'free'
                st.session_state['username'] = user_input # İSMİ HAFIZAYA KAYDETTİK!
                st.rerun()
            else:
                st.error("Hatalı giriş! (Demo: demo / 123)")
    else:
        # GİRİŞ YAPILMIŞ
        current_user = st.session_state['username'] # Hafızadan okuyoruz
        plan_color = "green" if st.session_state['user_plan'] == 'premium' else "orange"
        
        st.markdown(f"Hoşgeldin, **{current_user}**")
        st.markdown(f"Paket: <span style='color:{plan_color}; font-weight:bold'>{st.session_state['user_plan'].upper()}</span>", unsafe_allow_html=True)
        
        if st.session_state['user_plan'] == 'free':
            st.info("⚠️ Ücretsiz planda maks. 3 sayfa.")
            if st.button("💎 Premium'a Yükselt (Simüle)"):
                st.session_state['user_plan'] = 'premium'
                st.success("Premium aktif edildi!")
                time.sleep(1)
                st.rerun()
        
        if st.button("Çıkış Yap"):
            st.session_state['logged_in'] = False
            st.rerun()

# --- ANA EKRAN ---

if not st.session_state['logged_in']:
    st.header("🚀 Akademik Okumalarınızı 10x Hızlandırın")
    st.info("👈 Test etmek için sol menüden giriş yapın. (Kullanıcı: demo / Şifre: 123)")

else:
    st.subheader("📄 Doküman Yükle & Analiz Et")
    uploaded_file = st.file_uploader("PDF Dosyası", type=["pdf"])
    
    action_type = st.selectbox("İşlem Seçin:", ("Özet Çıkar", "Akademik Çeviri", "Sınav Sorusu Oluştur"))
    
    if action_type == "Akademik Çeviri":
        language = st.selectbox("Hedef Dil:", ("Türkçe", "İngilizce", "Fransızca"))
    elif action_type == "Sınav Sorusu Oluştur":
        quiz_count = st.slider("Soru Sayısı:", 1, 20, 5)

    if uploaded_file and api_key:
        text_content, num_pages = get_pdf_info(uploaded_file)
        st.write(f"📄 Sayfa Sayısı: **{num_pages}**")
        
        # KOTA KONTROLÜ
        can_proceed = True
        if st.session_state['user_plan'] == 'free':
            if num_pages > 3:
                st.error(f"⛔ **Kota Aşıldı!** ({num_pages}/3 Sayfa)")
                st.markdown("""<div class="warning-box">Uzun dosyalar için <b>Premium</b> pakete geçmelisiniz.</div>""", unsafe_allow_html=True)
                can_proceed = False
            else:
                st.success("✅ Ücretsiz kota uygun.")
        
        if can_proceed:
            if st.button("Analizi Başlat"):
                model_name = find_flash_model(api_key)
                st.caption(f"Motor: {model_name}")
                
                with st.spinner("Briefly çalışıyor..."):
                    if action_type == "Özet Çıkar":
                        p = "Bu metni akademik dille, maddeler halinde Türkçe özetle."
                    elif action_type == "Akademik Çeviri":
                        p = f"Bu metni {language} diline akademik çevir."
                    else:
                        p = f"Bu metinden {quiz_count} adet test sorusu ve cevap anahtarı hazırla."
                    
                    result = generate_content(api_key, model_name, p, text_content)
                    st.markdown("### 🚀 Sonuçlar:")
                    st.write(result)
                    st.download_button("İndir", result, file_name="sonuc.txt")

    elif not api_key:
        st.warning("⚠️ Lütfen sol menüden API anahtarınızı girin.")