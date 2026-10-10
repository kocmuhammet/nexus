import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import st_folium
import math

# --- SAYFA YAPILANDIRMASI VE CSS ---
st.set_page_config(page_title="Modül 1 | Çoklu Rota", layout="wide")

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

# --- ORTAK API VE ALGORİTMA FONKSİYONLARI ---
@st.cache_data(show_spinner=False)
def sehir_koordinati_al(sehir_adi):
    url = f"https://nominatim.openstreetmap.org/search?q={sehir_adi},Türkiye&format=json&limit=1"
    try:
        res = requests.get(url, headers={'User-Agent': 'Nexus_KDS_Academik'}).json()
        if res: return float(res[0]['lat']), float(res[0]['lon'])
    except: pass
    return None, None

def haversine_mesafe(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

@st.cache_data(show_spinner=False)
def coklu_gercek_rota_hesapla(sirali_koordinatlar):
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in sirali_koordinatlar])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
    try:
        res = requests.get(url).json()
        if res.get('code') == 'Ok':
            return res['routes'][0]['geometry'], res['routes'][0]['distance']/1000, res['routes'][0]['duration']/3600
    except: pass
    return None, 0, 0

# --- SİSTEM HAFIZASI (SESSION STATE) ---
if "modul1_hesapla" not in st.session_state:
    st.session_state.modul1_hesapla = False

# --- ANA SAYFAYA DÖNÜŞ BUTONU ---
col_nav, _ = st.columns([1, 5])
with col_nav:
    if st.button("⬅️ Ana Sayfaya Dön", use_container_width=True):
        st.switch_page("app.py")
# --- ARAYÜZ ---
st.title("🚛 Modül 1: Çoklu Rota (TSP) ve Filo Optimizasyonu")
st.markdown("Gerçek dünya karayolu verileri kullanılarak Çok Kriterli Karar Verme (AHP/TOPSIS) ve Rota Optimizasyonu (TSP) işlemleri yapılır.")

with st.expander("⚙️ Rota ve AHP Girdi Paneli", expanded=True):
    col_girdi1, col_girdi2 = st.columns(2)
    with col_girdi1:
        baslangic = st.text_input("Çıkış Noktası (Merkez)", value="Muğla")
        hedefler_str = st.text_area("Uğranacak Duraklar (Virgülle Ayırın)", value="Balıkesir, İzmir, Bursa, İstanbul")
        yuk_tonaji = st.number_input("Toplam Taşınacak Yük (Ton)", min_value=1.0, max_value=25.0, value=18.0)
    with col_girdi2:
        st.markdown("**Stratejik AHP Öncelikleri (1-9)**")
        w_maliyet = st.slider("Finansal Maliyet", 1, 9, 7)
        w_sure = st.slider("Teslimat Hızı", 1, 9, 4)
        w_cevre = st.slider("Çevresel Etki (Karbon İzi)", 1, 9, 6)
        
hedef_listesi = [x.strip() for x in hedefler_str.split(",") if x.strip()]

# Buton hafızayı tetikler
if st.button("🚀 KDS Optimizasyonunu Başlat", use_container_width=True):
    st.session_state.modul1_hesapla = True

# Hafıza tetiklenmişse işlemleri yap ve ekranda tut
if st.session_state.modul1_hesapla:
    lat_bas, lon_bas = sehir_koordinati_al(baslangic)
    
    if lat_bas:
        with st.spinner('Yapay Zeka Rota (TSP) Optimizasyonu Yapıyor ve Veriler Çekiliyor...'):
            ziyaret_edilecekler = []
            for h in hedef_listesi:
                lat, lon = sehir_koordinati_al(h)
                if lat and lon:
                    ziyaret_edilecekler.append({"isim": h, "lat": lat, "lon": lon})
            
            guncel_lat, guncel_lon = lat_bas, lon_bas
            sirali_rota_isimleri = [baslangic]
            sirali_koordinatlar = [(lat_bas, lon_bas)]
            
            while ziyaret_edilecekler:
                en_yakin = None
                min_mesafe = float('inf')
                
                for durak in ziyaret_edilecekler:
                    mesafe = haversine_mesafe(guncel_lat, guncel_lon, durak['lat'], durak['lon'])
                    if mesafe < min_mesafe:
                        min_mesafe = mesafe
                        en_yakin = durak
                        
                sirali_rota_isimleri.append(en_yakin['isim'])
                sirali_koordinatlar.append((en_yakin['lat'], en_yakin['lon']))
                guncel_lat, guncel_lon = en_yakin['lat'], en_yakin['lon']
                ziyaret_edilecekler.remove(en_yakin)
            
            rota_geo, gercek_mesafe, gercek_sure = coklu_gercek_rota_hesapla(sirali_koordinatlar)
            
            if rota_geo:
                toplam_w = w_maliyet + w_sure + w_cevre
                agirliklar = np.array([w_maliyet/toplam_w, w_sure/toplam_w, w_cevre/toplam_w])
                
                araclar = ["Dizel Ağır Yük Tırı", "Elektrikli Lojistik Kamyonu", "Hibrit Panelvan"]
                karar_matrisi = np.array([
                    [12.0, 1.0, 150.0],  
                    [5.0,  1.4, 0.0],    
                    [8.0,  0.9, 60.0]    
                ])
                
                if yuk_tonaji > 15:
                    karar_matrisi[1, 1] *= 1.5 
                    karar_matrisi[2, 0] *= 4.0 
                    
                norm_matris = karar_matrisi / np.sqrt((karar_matrisi**2).sum(axis=0))
                weighted_matris = norm_matris * agirliklar
                
                ideal = weighted_matris.min(axis=0) 
                neg_ideal = weighted_matris.max(axis=0)
                
                d_pozitif = np.sqrt(((weighted_matris - ideal)**2).sum(axis=1))
                d_negatif = np.sqrt(((weighted_matris - neg_ideal)**2).sum(axis=1))
                topsis_skoru = np.where((d_pozitif + d_negatif) == 0, 0, d_negatif / (d_pozitif + d_negatif))
                
                df_skor = pd.DataFrame({"Araç": araclar, "Uygunluk": topsis_skoru}).sort_values(by="Uygunluk", ascending=False).reset_index(drop=True)
                secilen_arac = df_skor.iloc[0]["Araç"]
                
                st.success(f"**TSP Rota Optimizasyonu Tamamlandı:** {' ➔ '.join(sirali_rota_isimleri)}")
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Toplam Karayolu", f"{int(gercek_mesafe)} km", f"{len(sirali_rota_isimleri)-1} Durak")
                c2.metric("AHP/TOPSIS Seçimi", secilen_arac)
                c3.metric("Tahmini Maliyet", f"{int(gercek_mesafe * karar_matrisi[araclar.index(secilen_arac)][0])} ₺")
                c4.metric("Karbon İzi", f"{int((gercek_mesafe * yuk_tonaji * karar_matrisi[araclar.index(secilen_arac)][2])/1000)} kg")
                
                sol, sag = st.columns([2, 1])
                with sol:
                    m = folium.Map(location=[(lat_bas+sirali_koordinatlar[-1][0])/2, (lon_bas+sirali_koordinatlar[-1][1])/2], zoom_start=6, tiles="CartoDB dark_matter")
                    
                    for idx, (lat, lon) in enumerate(sirali_koordinatlar):
                        renk = "green" if idx == 0 else ("red" if idx == len(sirali_koordinatlar)-1 else "orange")
                        folium.Marker(
                            [lat, lon], 
                            tooltip=f"{idx}. Durak: {sirali_rota_isimleri[idx]}",
                            icon=folium.Icon(color=renk, icon="info-sign")
                        ).add_to(m)
                        
                    folium.GeoJson(rota_geo, style_function=lambda x: {'color': '#00C896', 'weight': 4}).add_to(m)
                    
                    # Haritanın Streamlit'i yenilemesini engelleyen kilit nokta
                    st_folium(m, width=700, height=450, returned_objects=[])
                    
                with sag:
                    st.markdown("#### Karar Matrisi")
                    st.dataframe(df_skor, use_container_width=True)
                    st.info(f"Sistem, rotayı en kısa mesafeye göre sıraya dizmiş (TSP) ve bu mesafe üzerinden {yuk_tonaji} tonluk yük kısıtını değerlendirerek en optimum araç tipini belirlemiştir.")
            else:
                st.error("Karayolu rotası çizilemedi.")
    else:
        st.error("Başlangıç noktası bulunamadı.")