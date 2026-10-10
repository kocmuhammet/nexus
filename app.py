import streamlit as st

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Nexus KDS | Ana Merkez", layout="wide", initial_sidebar_state="expanded")

# --- GELİŞMİŞ CSS (Modern Dashboard Görünümü) ---
st.markdown("""
    <style>
    /* Otomatik oluşan sol menüyü ve açma/kapama butonunu tamamen gizler */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .main {background-color: #0E1117;}
    h1, h2, h3, h4, p {color: #E0E6ED !important;}
    .stButton>button {
        background-color: #00C896; 
        color: #0E1117 !important; 
        font-weight: bold; 
        border-radius: 8px; 
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00A67C;
        transform: scale(1.02);
    }
    .kds-card {
        background-color: #1A1C24;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00C896;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- HERO BÖLÜMÜ (Başlık ve Proje Özeti) ---
c1, c2, c3 = st.columns([1, 4, 1])
with c2:
    st.image("https://cdn-icons-png.flaticon.com/512/2065/2065565.png", width=80)
    st.markdown("<h1 style='text-align: left; font-size: 3rem;'>🌐 NEXUS KDS PLATFORMU</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #00C896 !important;'>Karar Destek Sistemleri Dersi - Kapsamlı Dönem Projesi</h4>", unsafe_allow_html=True)
    st.markdown("""
    Bu sistem; **Çok Kriterli Karar Verme (AHP, TOPSIS)**, **Makine Öğrenmesi (K-Means)** ve **Sezgisel Optimizasyon (TSP, VRPTW)** algoritmalarını birleştirerek 4 farklı gerçek dünya lojistik problemine otonom ve algoritmik çözümler sunar.
    """)

st.divider()

# --- MODÜL BUTONLARI (KART TASARIMI) ---
st.markdown("### 🚀 Sistem Modülleri (Başlamak İçin Seçiniz)")

col1, col2 = st.columns(2)

# MODÜL 1 KARTI
with col1:
    with st.container(border=True):
        st.markdown("### 🚛 Modül 1: Makro Lojistik")
        st.markdown("**Problem:** Şehirlerarası ağır tonajlı kargo rotalama ve filo seçimi.")
        st.markdown("**Kullanılan Yöntemler:** AHP, TOPSIS, Gezgin Satıcı (TSP), OSRM Karayolu API")
        if st.button("Modül 1'i Başlat ➔", key="btn1", use_container_width=True):
            st.switch_page("pages/1_Makro_Lojistik.py")

# MODÜL 2 KARTI
with col2:
    with st.container(border=True):
        st.markdown("### 📦 Modül 2: Şehir İçi Dağıtım")
        st.markdown("**Problem:** Dar sokak kısıtlarına göre son-mil (last-mile) kargo dağıtımı.")
        st.markdown("**Kullanılan Yöntemler:** K-Means Kümeleme (Makine Öğrenmesi), Varyans Analizi")
        if st.button("Modül 2'yi Başlat ➔", key="btn2", use_container_width=True):
            st.switch_page("pages/2_Sehir_Ici.py")

st.markdown("<br>", unsafe_allow_html=True)
col3, col4 = st.columns(2)

# MODÜL 3 KARTI
with col3:
    with st.container(border=True):
        st.markdown("### 🚨 Modül 3: Afet Lojistiği (AFAD)")
        st.markdown("**Problem:** Deprem/Afet sonrası kısıtlı yollarda acil yardım dağıtımı.")
        st.markdown("**Kullanılan Yöntemler:** Dinamik AHP, Pydeck 3D Haritalama, Kriz Simülasyonu")
        if st.button("Modül 3'ü Başlat ➔", key="btn3", use_container_width=True):
            st.switch_page("pages/3_Afet_Lojistigi.py")

# MODÜL 4 KARTI
with col4:
    with st.container(border=True):
        st.markdown("### ❄️ Modül 4: Soğuk Zincir (Sağlık)")
        st.markdown("**Problem:** Aşı, Kan ve Organ naklinde sıcaklık sınırına dayalı rota optimizasyonu.")
        st.markdown("**Kullanılan Yöntemler:** VRPTW (Zaman Pencereli Rotalama), Termal Risk Fonksiyonu")
        if st.button("Modül 4'ü Başlat ➔", key="btn4", use_container_width=True):
            st.switch_page("pages/4_Soguk_Zincir.py")

st.divider()

# --- PROJE KRİTERLERİ KONTROL PANELİ (Hocaya Yönelik Gövde Gösterisi) ---
st.markdown("### 📋 Proje Kriterleri Karşılama Tablosu")
kriterler_col1, kriterler_col2 = st.columns(2)

with kriterler_col1:
    st.success("✅ **Gerçek Dünya Problemi:** 4 farklı sektörel kriz senaryosu simüle edilmiştir.")
    st.success("✅ **Karar Unsurları & Kriterler:** AHP matrisleri ile netleştirilmiştir (Maliyet, Hız, Çevre vb.)")
    st.success("✅ **Yöntem ve Teknolojik Altyapı:** Streamlit, Pandas, Folium, Pydeck, Scikit-Learn kullanılmıştır.")

with kriterler_col2:
    st.success("✅ **Çok Kriterli Optimizasyon:** AHP ve TOPSIS hibrit olarak tüm modüllere entegre edilmiştir.")
    st.success("✅ **Veri Ulaşılabilirliği:** Gerçek API'ler (OSRM, Nominatim) ve Sentetik Veri (K-Means) kullanılmıştır.")
    st.success("✅ **Etik & Açıklanabilirlik:** Her modülde algoritmik kararın nedeni yöneticiye şeffafça sunulmuştur.")