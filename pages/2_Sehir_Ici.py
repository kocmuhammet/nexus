import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import st_folium
import math
from sklearn.cluster import KMeans

# --- SAYFA YAPILANDIRMASI VE CSS ---
st.set_page_config(page_title="Modül 2 | Şehir İçi Kargo", layout="wide")
st.markdown("""
    <style>
    /* Otomatik oluşan sol menüyü ve açma/kapama butonunu tamamen gizler */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .main {background-color: #0E1117;}
    h1, h2, h3 {color: #E0E6ED !important;}
    .stMetric {background-color: #1E2329; padding: 15px; border-radius: 10px; border-left: 5px solid #00C896;}
    </style>
""", unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
@st.cache_data(show_spinner=False)
def sehir_koordinati_al(sehir_adi):
    url = f"https://nominatim.openstreetmap.org/search?q={sehir_adi},Türkiye&format=json&limit=1"
    try:
        res = requests.get(url, headers={'User-Agent': 'Nexus_KDS_Academik'}).json()
        if res: return float(res[0]['lat']), float(res[0]['lon'])
    except: pass
    return None, None

def tsp_sirala(koordinatlar):
    if len(koordinatlar) <= 1: return koordinatlar
    ziyaret_edilmeyenler = koordinatlar.copy()
    guncel = ziyaret_edilmeyenler.pop(0)
    sirali = [guncel]
    while ziyaret_edilmeyenler:
        en_yakin = min(ziyaret_edilmeyenler, key=lambda x: math.dist(guncel, x))
        sirali.append(en_yakin)
        guncel = en_yakin
        ziyaret_edilmeyenler.remove(en_yakin)
    return sirali

# --- SİSTEM HAFIZASI ---
if "modul2_hesapla" not in st.session_state:
    st.session_state.modul2_hesapla = False

# --- ANA SAYFAYA DÖNÜŞ BUTONU ---
col_nav, _ = st.columns([1, 5])
with col_nav:
    if st.button("⬅️ Ana Sayfaya Dön", use_container_width=True):
        st.switch_page("app.py")
# --- ARAYÜZ VE GİRDİ PANELİ ---
st.title("📦 Modül 2: Şehir İçi Akıllı Kargo Dağıtımı")
st.markdown("Makine Öğrenmesi (K-Means) kullanılarak Bölge Optimizasyonu ve Karar Destek Sistemi algoritması çalıştırılır.")

with st.expander("⚙️ Operasyon ve K-Means Girdi Paneli", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        merkez_ilce = st.text_input("Dağıtım Merkezi (İlçe, İl)", value="Menteşe, Muğla")
        kargo_sayisi = st.slider("Dağıtılacak Kargo Sayısı (N)", 10, 100, 40)
    with col2:
        kurye_sayisi = st.slider("Görevli Kurye Sayısı (K-Means k değeri)", 2, 8, 3)
        st.info("💡 **Sentetik Veri:** Gerçek harita merkez alınarak Gaussian dağılımı ile rastgele kargo lokasyonları üretilir.")

if st.button("🚀 K-Means Kurye Optimizasyonunu Başlat", use_container_width=True):
    st.session_state.modul2_hesapla = True

# --- ALGORİTMA VE ÇIKTILAR ---
if st.session_state.modul2_hesapla:
    merkez_lat, merkez_lon = sehir_koordinati_al(merkez_ilce)
    
    if merkez_lat:
        with st.spinner("Makine Öğrenmesi ile Kümeleme Yapılıyor..."):
            np.random.seed(42)
            lat_sapma = np.random.normal(0, 0.015, kargo_sayisi)
            lon_sapma = np.random.normal(0, 0.015, kargo_sayisi)
            kargo_lat = merkez_lat + lat_sapma
            kargo_lon = merkez_lon + lon_sapma
            koordinatlar = np.column_stack((kargo_lat, kargo_lon))
            
            kmeans = KMeans(n_clusters=kurye_sayisi, random_state=42, n_init=10)
            kumeler = kmeans.fit_predict(koordinatlar)
            
            arac_kararlari = []
            sirali_kume_rotalari = []
            
            for k in range(kurye_sayisi):
                kume_noktalari = koordinatlar[kumeler == k].tolist()
                sirali_rota = tsp_sirala(kume_noktalari)
                sirali_kume_rotalari.append(sirali_rota)
                
                if len(kume_noktalari) > 1:
                    varyans = np.var(kume_noktalari, axis=0).sum()
                    if varyans < 0.0001: arac = "⚡ Elektrikli Kargo Bisikleti (Dar Bölge)"
                    elif varyans < 0.0003: arac = "🛵 Moto-Kurye (Orta Mesafe)"
                    else: arac = "🚐 Elektrikli Minivan (Geniş Bölge)"
                else:
                    arac = "🛵 Moto-Kurye (Tekil Teslimat)"
                
                arac_kararlari.append(arac)

            st.success("K-Means Kümeleme ve Rota Optimizasyonu Başarıyla Tamamlandı!")
            
            sol, sag = st.columns([2, 1])
            with sol:
                m = folium.Map(location=[merkez_lat, merkez_lon], zoom_start=13, tiles="CartoDB dark_matter")
                folium.Marker([merkez_lat, merkez_lon], tooltip="Ana Depo", icon=folium.Icon(color="black", icon="home")).add_to(m)
                
                renkler = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige']
                for k in range(kurye_sayisi):
                    renk = renkler[k % len(renkler)]
                    rota = sirali_kume_rotalari[k]
                    folium.PolyLine(rota, color=renk, weight=2.5, opacity=0.7).add_to(m)
                    for lat, lon in rota:
                        folium.CircleMarker(location=[lat, lon], radius=5, color=renk, fill=True, fill_color=renk, fill_opacity=0.9).add_to(m)
                
                # Yanıp sönmeyi engelleyen kilit
                st_folium(m, width=700, height=500, returned_objects=[])

            with sag:
                st.markdown("### 📊 Bölgesel KDS Analizi")
                df_kurye = pd.DataFrame({
                    "Kurye / Bölge": [f"Bölge {i+1}" for i in range(kurye_sayisi)],
                    "Kargo Adedi": [sum(kumeler == i) for i in range(kurye_sayisi)],
                    "Atanan Araç": arac_kararlari
                })
                st.dataframe(df_kurye, use_container_width=True)
                st.warning("**Algoritmik Karar Şeffaflığı:** Sistem, kuryelerin iş yükünü dengelemekten ziyade coğrafi yakınlığı (Öklid) baz alarak kümeler oluşturur. Dağınık kümelere Minivan, dar sokaklara Bisiklet atanmıştır.")
    else:
        st.error("Girdiğiniz merkez ilçe bulunamadı.")