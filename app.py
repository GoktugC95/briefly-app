import streamlit as st
import PyPDF2 as pdf
import requests
import time

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="Briefly | Ultimate AI", page_icon="⚡", layout="wide")

# --- 2. SABİT AYARLAR (LİNKLERİ SONRA DOLDURACAKSIN) ---
SHOPIER_100 = "https://shopier.com/URUN_LINKI_100"
SHOPIER_200 = "https://shopier.com/URUN_LINKI_200"
SHOPIER_300 = "https://shopier.com/URUN_LINKI_300"

# Aktivasyon Kodları
CODE_100 = "BRIEFLY100"
CODE_200 = "BRIEFLY200"
CODE_300 = "BRIEFLY300"

# --- 3. CSS: CANLI ARKA PLAN VE DİNAMİK ŞEKİLLER ---
st.markdown("""
    <style>
    /* 1. Hareketli Gradient Arka Plan */
    .stApp {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* 2. İçerik Kutuları (Glassmorphism - Buzlu Cam Etkisi) */
    .block-container, .stSidebar, .login-box {
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* 3. Butonlar */
    .stButton>button {
        background-image: linear-gradient(to right, #1FA2FF 0%, #12D8FA  51%, #1FA2FF  100%);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: bold;
        transition: 0.5s;
        background-size: 200% auto;
    }
    .stButton>button:hover {
        background-position: right center; 
    }

    /* 4. Paket İsimleri Renklendirme */
    .plan-student { color: #17a2b8; font-weight: bold; }
    .plan-pro { color: #6610f2; font-weight: bold; }
    .plan-elite { color: #d63384; font-weight: bold; text-shadow: 0px 0px 5px #d63384; }
    
    </style>
    """, unsafe_allow_html=True)

# --- 4. HAFIZA VE VERİTABANI ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_plan' not in st.session_state:
    st.session_state['user_plan'] = 'free' # Seçenekler: free, student, pro, elite
if 'username' not in st.session_state:
    st.session_state['username'] = ''

# Basit Veritabanı (Kullanıcı Adı : {Şifre, Email})
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "demo": {"pass": "123", "email": "demo@briefly.com"},
        "goktug": {"pass": "admin", "email": "boss@briefly.com"} # SENİN HESABIN
    }

# --- 5. API KONTROL ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.warning("⚠️ API Anahtarı bulunamadı.")
    st.stop()

# --- 6. FONKSİYONLAR ---
def get_pdf_text(uploaded_file):
    text = ""
    reader = pdf.PdfReader(uploaded_file)
    num_pages = len(reader.pages)
    for page in range(num_pages):
        text += reader.pages[page].extract_text() or ""
    return text, num_pages

def generate_content(key, prompt, text_content):
    model_name = "models/gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": f"{prompt}\n\n---\nMetin:\n{text_content}"}]}]}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return "Hata oluştu."
    except Exception as e: return str(e)

# ================= ARAYÜZ =================

# --- YAN MENÜ ---
with st.sidebar:
    st.title("⚡ Briefly")
    
    if st.session_state['logged_in']:
        user = st.session_state['username']
        plan = st.session_state['user_plan']
        
        st.write(f"Hoşgeldin, **{user.capitalize()}**")
        
        # PLAN GÖSTERGESİ
        if plan == 'free':
            st.markdown("Paket: **ÜCRETSİZ** (3 Sayfa)")
        elif plan == 'student':
            st.markdown("Paket: <span class='plan-student'>STUDENT (100 TL)</span>", unsafe_allow_html=True)
        elif plan == 'pro':
            st.markdown("Paket: <span class='plan-pro'>ACADEMIC PRO (200 TL)</span>", unsafe_allow_html=True)
        elif plan == 'elite':
            st.markdown("Paket: <span class='plan-elite'>ELITE RESEARCHER (300 TL)</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # PAKET YÜKSELTME MENÜSÜ (Sadece Elite değilse göster)
        if plan != 'elite':
            st.subheader("🚀 Paketinizi Yükseltin")
            
            with st.expander("🎓 Student Pack (100 TL)"):
                st.write("• 50 Sayfa Limiti\n• Özet & Çeviri")
                st.link_button("Satın Al", SHOPIER_100)
            
            with st.expander("🧠 Academic Pro (200 TL)"):
                st.write("• 200 Sayfa Limiti\n• Sınav Modu Aktif")
                st.link_button("Satın Al", SHOPIER_200)
            
            with st.expander("💎 Elite Researcher (300 TL)"):
                st.write("• SINIRSIZ Erişim\n• Her Şey Dahil")
                st.link_button("Satın Al", SHOPIER_300)
            
            st.markdown("---")
            
            # AKTİVASYON
            code = st.text_input("Aktivasyon Kodu Girin")
            if st.button("Kodu Onayla"):
                if code == CODE_100:
                    st.session_state['user_plan'] = 'student'
                    st.success("Student Paket Aktif!")
                    st.rerun()
                elif code == CODE_200:
                    st.session_state['user_plan'] = 'pro'
                    st.success("Pro Paket Aktif!")
                    st.rerun()
                elif code == CODE_300:
                    st.session_state['user_plan'] = 'elite'
                    st.balloons()
                    st.success("Elite Paket Aktif!")
                    st.rerun()
                else:
                    st.error("Geçersiz Kod")

        if st.button("Çıkış Yap"):
            st.session_state['logged_in'] = False
            st.rerun()
            
    else:
        st.info("Giriş yapın veya kayıt olun.")

# --- ANA EKRAN ---

if not st.session_state['logged_in']:
    # LOGIN / REGISTER
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.title("Briefly'ye Katılın")
        st.markdown("Akademik hayatınızı yapay zeka ile kolaylaştırın.")
        
        tab1, tab2 = st.tabs(["Giriş Yap", "Kayıt Ol (E-Posta)"])
        
        with tab1:
            l_user = st.text_input("Kullanıcı Adı")
            l_pass = st.text_input("Şifre", type="password")
            if st.button("Giriş"):
                db = st.session_state['users_db']
                if l_user in db and db[l_user]["pass"] == l_pass:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = l_user
                    # PATRON KONTROLÜ
                    if l_user == "goktug":
                        st.session_state['user_plan'] = 'elite'
                    st.rerun()
                else:
                    st.error("Hatalı bilgiler.")
        
        with tab2:
            r_user = st.text_input("Kullanıcı Adı Belirle")
            r_email = st.text_input("E-Posta Adresiniz")
            r_pass = st.text_input("Şifre Belirle", type="password")
            
            if st.button("Kayıt Ol"):
                if r_user and r_email and r_pass:
                    st.session_state['users_db'][r_user] = {"pass": r_pass, "email": r_email}
                    st.success("Kayıt Başarılı! Giriş sekmesine geçiniz.")
                else:
                    st.warning("Tüm alanları doldurun.")

else:
    # APP ARAYÜZÜ
    st.subheader("📄 Yapay Zeka Analiz Merkezi")
    uploaded_file = st.file_uploader("PDF Yükle", type=["pdf"])
    
    col1, col2 = st.columns(2)
    with col1:
        action = st.selectbox("İşlem", ["Özet Çıkar", "Akademik Çeviri", "Sınav Sorusu"])
    with col2:
        lang = st.selectbox("Dil", ["Türkçe", "İngilizce", "Fransızca"]) if action == "Akademik Çeviri" else None
        q_cnt = st.slider("Soru Sayısı", 5, 50, 10) if action == "Sınav Sorusu" else None

    if uploaded_file:
        text, pages = get_pdf_text(uploaded_file)
        plan = st.session_state['user_plan']
        
        # --- KOTA MANTIĞI (EN ÖNEMLİ KISIM) ---
        LIMITS = {'free': 3, 'student': 50, 'pro': 200, 'elite': 99999}
        limit = LIMITS[plan]
        
        st.info(f"Dosya: {pages} Sayfa | Sizin Limitiniz: {limit} Sayfa")
        
        if pages > limit:
            st.error(f"⛔ Limit Aşıldı! ({pages}/{limit})")
            st.markdown(f"**{plan.upper()}** paketiniz bu dosya için yetersiz. Lütfen paketinizi yükseltin.")
        else:
            if st.button("Analizi Başlat 🚀"):
                with st.spinner("Briefly çalışıyor..."):
                    # Prompt Hazırlığı
                    if action == "Özet Çıkar": p = "Bu metni akademik, detaylı Türkçe özetle."
                    elif action == "Akademik Çeviri": p = f"Bu metni {lang} diline akademik çevir."
                    else: p = f"Bu metinden {q_cnt} adet zorlayıcı test sorusu ve cevap anahtarı oluştur."
                    
                    res = generate_content(api_key, p, text)
                    st.markdown("### Sonuçlar")
                    st.write(res)
                    st.download_button("İndir", res)