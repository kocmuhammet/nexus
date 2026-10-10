import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from streamlit_folium import st_folium
import math
import plotly.graph_objects as go

# --- SAYFA YAPILANDIRMASI VE CSS ---
st.set_page_config(page_title="Modül 4 | Soğuk Zincir KDS", layout="wide")
st.markdown("""
    <style>
    /* Otomatik oluşan sol menüyü ve açma/kapama butonunu tamamen gizler */
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .main {background-color: #0E1117;}
    h1, h2, h3 {color: #E0E6ED !important;}
    .stMetric {background-color: #1E2329; padding: 15px; border-radius: 10px; border-left: 5px solid #3498db;}
    </style>
""", unsafe_allow_html=True)

# --- YARDIMCI FONKSİYONLAR ---
@st.cache_data(show_spinner=False)
def koordinat_al(sehir_adi):
    url = f"https://nominatim.openstreetmap.org/search?q={sehir_adi},Türkiye&format=json&limit=1"
    try:
        res = requests.get(url, headers={'User-Agent': 'Nexus_KDS_Academik'}).json()
        if res: return float(res[0]['lat']), float(res[0]['lon'])
    except: pass
    return None, None

def haversine_mesafe(lat1, lon1, lat2, lon2):
    R = 6371
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# --- SİSTEM HAFIZASI ---
if "modul4_hesapla" not in st.session_state:
    st.session_state.modul4_hesapla = False


# --- ANA SAYFAYA DÖNÜŞ BUTONU ---
col_nav, _ = st.columns([1, 5])
with col_nav:
    if st.button("⬅️ Ana Sayfaya Dön", use_container_width=True):
        st.switch_page("app.py")

# --- ARAYÜZ VE GİRDİ PANELİ ---
st.title("❄️ Modül 4: Tıbbi Ürün ve Soğuk Zincir (VRPTW) KDS")
st.markdown("Sıcaklık toleransı ve zaman kısıtlı tıbbi sevkiyat rotalama optimizasyonu.")

with st.expander("⚙️ Sevkiyat ve Termal Tolerans Girdi Paneli", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        merkez = st.text_input("Merkez Kan/Aşı Bankası", value="İzmir Şehir Hastanesi")
        hedefler_str = st.text_area("Teslimat Yapılacak Hastaneler", value="Ege Üniversitesi Hastanesi, Dokuz Eylül Üniversitesi Hastanesi, Tepecik Eğitim ve Araştırma Hastanesi")
    with col2:
        urun_tipi = st.selectbox("Taşınacak Tıbbi Ürün", ["💉 mRNA Aşısı (-20°C)", "🩸 Kan Torbaları (+4°C)", "🫀 Organ Nakli (+2°C)"])
        trafik_faktoru = st.slider("Trafik Yoğunluğu (Isı kaybını hızlandırır)", 1.0, 3.0, 1.5, 0.1)
        
if st.button("🧬 Termal Rota ve Araç Optimizasyonunu Başlat", use_container_width=True):
    st.session_state.modul4_hesapla = True

# --- ALGORİTMA VE ÇIKTILAR ---
if st.session_state.modul4_hesapla:
    hedef_listesi = [x.strip() for x in hedefler_str.split(",") if x.strip()]
    
    if "Aşısı" in urun_tipi: baslangic_isi, kritik_limit, isi_artis_hizi = -20.0, -15.0, 0.05
    elif "Kan" in urun_tipi: baslangic_isi, kritik_limit, isi_artis_hizi = 4.0, 10.0, 0.08
    else: baslangic_isi, kritik_limit, isi_artis_hizi = 2.0, 5.0, 0.15 
        
    lat_bas, lon_bas = koordinat_al(merkez)
    
    if lat_bas:
        with st.spinner("Termal riskler hesaplanıyor ve rotalar oluşturuluyor..."):
            ziyaret_edilecekler = []
            for h in hedef_listesi:
                lat, lon = koordinat_al(h)
                if lat and lon: ziyaret_edilecekler.append({"isim": h, "lat": lat, "lon": lon})
            
            guncel_lat, guncel_lon = lat_bas, lon_bas
            sirali_rota = [{"isim": merkez, "lat": lat_bas, "lon": lon_bas, "mesafe": 0, "isi": baslangic_isi}]
            
            toplam_mesafe = 0
            mevcut_isi = baslangic_isi
            risk_var_mi = False
            
            while ziyaret_edilecekler:
                en_yakin = min(ziyaret_edilecekler, key=lambda x: haversine_mesafe(guncel_lat, guncel_lon, x['lat'], x['lon']))
                min_mesafe = haversine_mesafe(guncel_lat, guncel_lon, en_yakin['lat'], en_yakin['lon'])
                
                toplam_mesafe += min_mesafe
                mevcut_isi += (min_mesafe * isi_artis_hizi * trafik_faktoru)
                if mevcut_isi > kritik_limit: risk_var_mi = True
                
                sirali_rota.append({"isim": en_yakin['isim'], "lat": en_yakin['lat'], "lon": en_yakin['lon'], "mesafe": min_mesafe, "isi": mevcut_isi})
                guncel_lat, guncel_lon = en_yakin['lat'], en_yakin['lon']
                ziyaret_edilecekler.remove(en_yakin)

            w_iklim, w_hiz, w_maliyet = (9, 8, 2) if risk_var_mi else (6, 5, 7)
            araclar = ["Standart Frigofirik Kamyonet", "VIP Soğutuculu Ambulans", "Medikal Drone Kargo"]
            karar_matrisi = np.array([[6, 5, 200], [9, 8, 800], [4, 10, 1500]], dtype=float)
            karar_matrisi[:, 2] = 1 / karar_matrisi[:, 2] # Maliyeti ters çevir (TOPSIS)
            
            toplam_w = w_iklim + w_hiz + w_maliyet
            agirliklar = np.array([w_iklim/toplam_w, w_hiz/toplam_w, w_maliyet/toplam_w])
            norm_matris = karar_matrisi / np.sqrt((karar_matrisi**2).sum(axis=0))
            weighted_matris = norm_matris * agirliklar
            
            ideal, neg_ideal = weighted_matris.max(axis=0), weighted_matris.min(axis=0)
            d_pos = np.sqrt(((weighted_matris - ideal)**2).sum(axis=1))
            d_neg = np.sqrt(((weighted_matris - neg_ideal)**2).sum(axis=1))
            topsis_skor = np.where((d_pos + d_neg) == 0, 0, d_neg / (d_pos + d_neg))
            secilen_arac = araclar[np.argmax(topsis_skor)]

            st.success("Termal Rota ve Araç Optimizasyonu Tamamlandı.")
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Tahmini Mesafe", f"{int(toplam_mesafe)} km", f"{len(sirali_rota)-1} Hastane")
            if risk_var_mi: c2.metric("Soğuk Zincir Durumu", "⚠️ KRİTİK RİSK", "Sıcaklık Eşiği Aşıldı", delta_color="inverse")
            else: c2.metric("Soğuk Zincir Durumu", "✅ GÜVENLİ", "Eşik Altında", delta_color="normal")
            c3.metric("KDS Önerilen Araç", secilen_arac, "AHP Optimizasyonu")

            sol, sag = st.columns([1, 1])
            with sol:
                st.markdown("### 🗺️ Teslimat Rotası")
                m = folium.Map(location=[lat_bas, lon_bas], zoom_start=11, tiles="CartoDB dark_matter")
                rota_koordinatlari = []
                for idx, durak in enumerate(sirali_rota):
                    rota_koordinatlari.append([durak['lat'], durak['lon']])
                    renk = "blue" if idx == 0 else ("red" if durak['isi'] > kritik_limit else "green")
                    folium.Marker([durak['lat'], durak['lon']], tooltip=f"{durak['isim']} ({durak['isi']:.1f}°C)", icon=folium.Icon(color=renk, icon="plus" if idx > 0 else "home")).add_to(m)
                folium.PolyLine(rota_koordinatlari, color="cyan", weight=3, opacity=0.8, dash_array="10").add_to(m)
                
                # Yanıp sönmeyi engelleyen kilit
                st_folium(m, width=500, height=400, returned_objects=[])

            with sag:
                st.markdown("### 📈 Termal Bozulma Grafiği")
                isimler = [d['isim'].split(" ")[0] for d in sirali_rota]
                isilar = [d['isi'] for d in sirali_rota]
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=isimler, y=isilar, mode='lines+markers', name='Ürün Sıcaklığı', line=dict(color='cyan', width=3), marker=dict(size=10)))
                fig.add_hline(y=kritik_limit, line_dash="dash", line_color="red", annotation_text=f"Bozulma Eşiği ({kritik_limit}°C)", annotation_position="bottom right")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), xaxis_title="Rota Durakları", yaxis_title="Sıcaklık (°C)", margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                st.info(f"**Algoritmik Karar:** Termal risk tespit {'edildiği için VIP araç' if risk_var_mi else 'edilmediği için Kamyonet'} seçilmiştir.")
    else:
        st.error("Merkez koordinatı bulunamadı.")