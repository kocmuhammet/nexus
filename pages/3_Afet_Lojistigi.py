import streamlit as st
import pandas as pd
import numpy as np
import requests
import pydeck as pdk
import math

# --- SAYFA YAPILANDIRMASI VE CSS ---
st.set_page_config(page_title="Modül 3 | Afet KDS", layout="wide")
st.markdown("""
    <style>
    /* Otomatik oluşan sol menüyü ve açma/kapama butonunu tamamen gizler */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .main {background-color: #0b0f19;}
    h1, h2, h3 {color: #ffffff !important;}
    .stMetric {background-color: #1a2235; padding: 15px; border-radius: 8px; border-left: 5px solid #ff4b4b;}
    </style>
""", unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
@st.cache_data(show_spinner=False)
def koordinat_al(sehir_adi):
    url = f"https://nominatim.openstreetmap.org/search?q={sehir_adi},Türkiye&format=json&limit=1"
    try:
        res = requests.get(url, headers={'User-Agent': 'Nexus_KDS_Academik'}).json()
        if res: return float(res[0]['lon']), float(res[0]['lat']) 
    except: pass
    return None, None

def haversine_mesafe(lon1, lat1, lon2, lat2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# --- SİSTEM HAFIZASI ---
if "modul3_hesapla" not in st.session_state:
    st.session_state.modul3_hesapla = False


# --- ANA SAYFAYA DÖNÜŞ BUTONU ---
col_nav, _ = st.columns([1, 5])
with col_nav:
    if st.button("⬅️ Ana Sayfaya Dön", use_container_width=True):
        st.switch_page("app.py")

# --- ARAYÜZ VE GİRDİ PANELİ ---
st.title("🚨 Modül 3: AFAD Kriz Yönetimi ve Afet Lojistiği KDS")
st.markdown("Dinamik AHP Algoritması ve 3D Pydeck (Arc) haritalama ile Çoklu Hedef Kriz Simülasyonu.")

with st.expander("⚙️ Kriz Senaryosu ve AHP Girdi Paneli", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        merkez = st.text_input("Çıkış (Lojistik Üs)", value="Ankara")
        hedefler_str = st.text_area("Afet Bölgeleri (Virgülle ayırın)", value="Hatay, Kahramanmaraş, Adıyaman")
        yol_durumu = st.radio("Bölgesel Ulaşım Durumu", ["🟢 Yollar Açık (Standart)", "🟠 Kısmi Göçük ve Enkaz", "🔴 Karayolu Ulaşımı Koptu"])
    with col2:
        st.markdown("**Kriz Anı Manuel AHP Müdahalesi (1-9)**")
        w_hiz = st.slider("Hız ve Aciliyet", 1, 9, 8)
        w_kapasite = st.slider("Taşıma Kapasitesi", 1, 9, 6)
        w_maliyet = st.slider("Operasyon Maliyeti", 1, 9, 2)

if st.button("🚁 Kriz Yönetim Sistemini Başlat", use_container_width=True):
    st.session_state.modul3_hesapla = True

# --- ALGORİTMA VE ÇIKTILAR ---
if st.session_state.modul3_hesapla:
    hedef_listesi = [x.strip() for x in hedefler_str.split(",") if x.strip()]
    merkez_lon, merkez_lat = koordinat_al(merkez)
    
    if merkez_lon:
        with st.spinner("Uydu Verileri Alınıyor ve Dinamik AHP Hesaplanıyor..."):
            gecerli_hedefler = []
            for h in hedef_listesi:
                lon, lat = koordinat_al(h)
                if lon and lat: gecerli_hedefler.append({"isim": h, "lon": lon, "lat": lat})
            
            arc_data = []
            toplam_mesafe = 0
            for hedef in gecerli_hedefler:
                mesafe = haversine_mesafe(merkez_lon, merkez_lat, hedef['lon'], hedef['lat'])
                toplam_mesafe += mesafe
                arc_data.append({
                    "source": [merkez_lon, merkez_lat], "target": [hedef['lon'], hedef['lat']],
                    "name": f"{merkez} ➔ {hedef['isim']} ({int(mesafe)} km)"
                })
            
            araclar = ["Standart Lojistik Tırı", "4x4 Taktik Arama Kurtarma", "CH-47 Kargo Helikopteri"]
            karar_matrisi = np.array([[80, 1, 500], [50, 4, 1500], [15, 8, 8000]], dtype=float)
            
            if "Göçük" in yol_durumu:
                karar_matrisi[0, 0] = 999 
                w_hiz = min(9, w_hiz + 1)
                w_maliyet = max(1, w_maliyet - 1)
            elif "Koptu" in yol_durumu:
                karar_matrisi[0, 0] = 9999 
                karar_matrisi[1, 0] *= 2.5 
                w_hiz = 9 
                w_maliyet = 1 
                
            toplam_w = w_hiz + w_kapasite + w_maliyet
            agirliklar = np.array([w_hiz/toplam_w, w_kapasite/toplam_w, w_maliyet/toplam_w])
            
            norm_matris = karar_matrisi / np.sqrt((karar_matrisi**2).sum(axis=0))
            weighted_matris = norm_matris * agirliklar
            
            ideal = weighted_matris.min(axis=0)
            neg_ideal = weighted_matris.max(axis=0)
            
            d_pos = np.sqrt(((weighted_matris - ideal)**2).sum(axis=1))
            d_neg = np.sqrt(((weighted_matris - neg_ideal)**2).sum(axis=1))
            topsis_skor = np.where((d_pos + d_neg) == 0, 0, d_neg / (d_pos + d_neg))
            
            df_sonuc = pd.DataFrame({"Müdahale Aracı": araclar, "KDS Uygunluk": np.round(topsis_skor, 3)}).sort_values(by="KDS Uygunluk", ascending=False).reset_index(drop=True)
            secilen_arac = df_sonuc.iloc[0]["Müdahale Aracı"]

            st.success("Analiz Tamamlandı. Kriz Müdahale Planı Hazır.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Operasyon Yarıçapı", f"{int(toplam_mesafe)} km", f"{len(gecerli_hedefler)} Bölge")
            c2.metric("Önerilen Ana Filo", secilen_arac, yol_durumu.split(" ")[1], delta_color="inverse")
            c3.metric("Sistem Güncellemesi", "Dinamik AHP Aktif", "Ağırlıklar Yapılandırıldı")

            sol, sag = st.columns([2, 1])
            with sol:
                view_state = pdk.ViewState(latitude=merkez_lat, longitude=merkez_lon, zoom=5.5, pitch=45, bearing=15)
                nokta_data = [{"lon": merkez_lon, "lat": merkez_lat, "isim": merkez, "renk": [0, 255, 100, 200]}]
                for h in gecerli_hedefler:
                    nokta_data.append({"lon": h["lon"], "lat": h["lat"], "isim": h["isim"], "renk": [255, 50, 50, 200]})
                
                scatter = pdk.Layer("ScatterplotLayer", data=pd.DataFrame(nokta_data), get_position="[lon, lat]", get_color="renk", get_radius=12000, pickable=True)
                arc_layer = pdk.Layer("ArcLayer", data=pd.DataFrame(arc_data), get_source_position="source", get_target_position="target", get_source_color="[0, 255, 100, 160]", get_target_color="[255, 50, 50, 160]", get_width=4, pickable=True)
                
                r = pdk.Deck(layers=[scatter, arc_layer], initial_view_state=view_state, tooltip={"text": "{name}\n{isim}"}, map_style="mapbox://styles/mapbox/dark-v10")
                st.pydeck_chart(r)

            with sag:
                st.markdown("### 🧮 KDS Analiz Raporu")
                st.dataframe(df_sonuc.style.background_gradient(cmap="Reds"), use_container_width=True)
                st.warning(f"**Algoritmik Zeka:** Sahadaki duruma ({yol_durumu}) göre KDS otonom bir tepki vermiştir. AHP ağırlıkları dinamik olarak güncellenmiş ve en uygun seçenek olan **{secilen_arac}** seçilmiştir.")
    else:
        st.error("Merkez koordinatı bulunamadı.")