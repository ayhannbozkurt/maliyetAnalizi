import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Sayfa yapılandırması
st.set_page_config(
    page_title="Kişisel Nakit Bütçe Yönetimi",
    page_icon="💰",
    layout="wide"
)

# Başlık
st.title("Kişisel Nakit Bütçe Yönetimi")

# Tarih aralığı
start_date = datetime(2024, 11, 1)
end_date = datetime(2025, 12, 31)
date_range = pd.date_range(start=start_date, end=end_date, freq='M')

# Sidebar - Sabit Ekonomik Varsayımlar
with st.sidebar:
    st.header("Ekonomik Varsayımlar")
    
    st.markdown("""
    ### Sabit Değerler
    - **Yıllık Enflasyon Oranı:** %45.0
    - **TCMB Faiz Oranı:** %42.5
    - **Yıllık Kira Artış Oranı:** %25.0
    """)
    
    # Sabit değerleri değişkenlere atama
    enflasyon = 45.0
    faiz_orani = 42.5
    kira_artis = 25.0

# Ana içerik
tab1, tab2, tab3 = st.tabs(["Nakit Girişleri", "Nakit Çıkışları", "Yatırımlar"])

with tab1:
    st.header("Nakit Girişleri")
    
    # Gelir kategorileri
    gelir_kategorileri = {
        "Aile Desteği": st.number_input("Aylık Aile Desteği (TL)", min_value=0.0, value=5000.0, step=100.0),
        "Burs": st.number_input("Aylık Burs (TL)", min_value=0.0, value=2000.0, step=100.0),
        "Part-time İş": st.number_input("Part-time İş Geliri (TL)", min_value=0.0, value=0.0, step=100.0),
        "Diğer Gelirler": st.number_input("Diğer Gelirler (TL)", min_value=0.0, value=0.0, step=100.0)
    }
    
    # Gelir artış oranları
    st.subheader("Gelir Artış Oranları")
    gelir_artis = {}
    for kategori in gelir_kategorileri.keys():
        gelir_artis[kategori] = st.slider(
            f"{kategori} - Yıllık Artış Oranı (%)",
            min_value=0.0,
            max_value=100.0,
            value=enflasyon,
            step=0.1
        )

with tab2:
    st.header("Nakit Çıkışları")
    
    # Gider kategorileri
    gider_kategorileri = {
        "Yurt/Kira": st.number_input("Aylık Yurt/Kira (TL)", min_value=0.0, value=3500.0, step=100.0),
        "Yemek": st.number_input("Aylık Yemek (TL)", min_value=0.0, value=2500.0, step=100.0),
        "Ulaşım": st.number_input("Aylık Ulaşım (TL)", min_value=0.0, value=500.0, step=100.0),
        "Eğlence": st.number_input("Aylık Eğlence (TL)", min_value=0.0, value=1000.0, step=100.0),
        "Eğitim": st.number_input("Aylık Eğitim (TL)", min_value=0.0, value=500.0, step=100.0),
        "Diğer": st.number_input("Diğer Giderler (TL)", min_value=0.0, value=500.0, step=100.0)
    }
    
    # Gider artış oranları
    st.subheader("Gider Artış Oranları")
    gider_artis = {}
    for kategori in gider_kategorileri.keys():
        if kategori == "Yurt/Kira":
            default_artis = kira_artis
        else:
            default_artis = enflasyon
            
        gider_artis[kategori] = st.slider(
            f"{kategori} - Yıllık Artış Oranı (%)",
            min_value=0.0,
            max_value=100.0,
            value=default_artis,
            step=0.1
        )

with tab3:
    st.header("Yatırımlar")
    
    # Yatırım kategorileri
    yatirim_kategorileri = {
        "Borsa": {
            "miktar": st.number_input("Aylık Borsa Yatırımı (TL)", min_value=0.0, value=0.0, step=100.0),
            "getiri": st.slider("Yıllık Beklenen Borsa Getirisi (%)", min_value=-50.0, max_value=100.0, value=20.0)
        },
        "Kripto": {
            "miktar": st.number_input("Aylık Kripto Yatırımı (TL)", min_value=0.0, value=0.0, step=100.0),
            "getiri": st.slider("Yıllık Beklenen Kripto Getirisi (%)", min_value=-70.0, max_value=200.0, value=30.0)
        },
        "Diğer": {
            "miktar": st.number_input("Diğer Yatırımlar (TL)", min_value=0.0, value=0.0, step=100.0),
            "getiri": st.slider("Yıllık Beklenen Diğer Yatırım Getirisi (%)", min_value=-50.0, max_value=100.0, value=15.0)
        }
    }

# Hesaplama ve Görselleştirme
if st.button("Bütçe Hesapla"):
    # Aylık nakit akışı hesaplama
    nakit_akisi = pd.DataFrame(index=date_range)
    
    # Gelirleri hesapla
    for kategori in gelir_kategorileri.keys():
        baslangic_gelir = gelir_kategorileri[kategori]
        artis_orani = gelir_artis[kategori]
        
        gelir_serisi = []
        current_gelir = baslangic_gelir
        
        for date in date_range:
            if date.month == 1 and date.year > start_date.year:  # Yıllık artış
                current_gelir *= (1 + artis_orani/100)
            gelir_serisi.append(current_gelir)
            
        nakit_akisi[f"Gelir_{kategori}"] = gelir_serisi
    
    # Giderleri hesapla
    for kategori in gider_kategorileri.keys():
        baslangic_gider = gider_kategorileri[kategori]
        artis_orani = gider_artis[kategori]
        
        gider_serisi = []
        current_gider = baslangic_gider
        
        for date in date_range:
            if date.month == 1 and date.year > start_date.year:  # Yıllık artış
                current_gider *= (1 + artis_orani/100)
            gider_serisi.append(current_gider)
            
        nakit_akisi[f"Gider_{kategori}"] = gider_serisi
    
    # Toplam gelir ve gider hesaplama (yatırımlar hariç)
    gelir_kolonlari = [col for col in nakit_akisi.columns if col.startswith('Gelir_')]
    gider_kolonlari = [col for col in nakit_akisi.columns if col.startswith('Gider_')]
    
    nakit_akisi['Toplam_Gelir'] = nakit_akisi[gelir_kolonlari].sum(axis=1)
    nakit_akisi['Toplam_Gider'] = nakit_akisi[gider_kolonlari].sum(axis=1)
    nakit_akisi['Net_Nakit_Akisi'] = nakit_akisi['Toplam_Gelir'] - nakit_akisi['Toplam_Gider']
    
    # Yatırımları hesapla
    aylik_toplam_yatirim = sum(degerler['miktar'] for degerler in yatirim_kategorileri.values())
    
    for kategori, degerler in yatirim_kategorileri.items():
        baslangic_yatirim = degerler['miktar']
        yillik_getiri = degerler['getiri']
        
        yatirim_serisi = []
        birikimli_yatirim = 0
        aylik_getiri = (1 + yillik_getiri/100) ** (1/12) - 1  # Yıllık getiriyi aylığa çevirme
        
        for date in date_range:
            if len(yatirim_serisi) == 0:
                birikimli_yatirim = baslangic_yatirim
            else:
                # Önceki ayın birikimi + getirisi + yeni yatırım
                birikimli_yatirim = birikimli_yatirim * (1 + aylik_getiri) + baslangic_yatirim
            
            yatirim_serisi.append(birikimli_yatirim)
            
        nakit_akisi[f"Yatirim_{kategori}"] = yatirim_serisi
    
    # Yatırım toplamlarını hesapla
    yatirim_kolonlari = [col for col in nakit_akisi.columns if col.startswith('Yatirim_')]
    nakit_akisi['Toplam_Yatirim_Degeri'] = nakit_akisi[yatirim_kolonlari].sum(axis=1)
    
    # Kümülatif nakit akışını güncelle (yatırım miktarlarını çıkararak)
    nakit_akisi['Net_Nakit_Akisi_Yatirimlar'] = nakit_akisi['Net_Nakit_Akisi'] - aylik_toplam_yatirim
    nakit_akisi['Kumulatif_Nakit'] = nakit_akisi['Net_Nakit_Akisi_Yatirimlar'].cumsum()
    
    # Toplam varlık değeri (Kümülatif nakit + Toplam yatırım değeri)
    nakit_akisi['Toplam_Varlik'] = nakit_akisi['Kumulatif_Nakit'] + nakit_akisi['Toplam_Yatirim_Degeri']
    
    # Görselleştirme
    fig = go.Figure()
    
    # Gelir, Gider ve Net Nakit Akışı çizgileri
    fig.add_trace(go.Scatter(
        x=nakit_akisi.index,
        y=nakit_akisi['Toplam_Gelir'],
        name='Toplam Gelir',
        line=dict(color='green')
    ))
    
    fig.add_trace(go.Scatter(
        x=nakit_akisi.index,
        y=nakit_akisi['Toplam_Gider'],
        name='Toplam Gider',
        line=dict(color='red')
    ))
    
    fig.add_trace(go.Scatter(
        x=nakit_akisi.index,
        y=nakit_akisi['Net_Nakit_Akisi_Yatirimlar'],
        name='Net Nakit Akışı (Yatırımlar Dahil)',
        line=dict(color='blue')
    ))
    
    # Yatırım ve toplam varlık çizgileri
    fig.add_trace(go.Scatter(
        x=nakit_akisi.index,
        y=nakit_akisi['Toplam_Yatirim_Degeri'],
        name='Toplam Yatırım Değeri',
        line=dict(color='purple')
    ))
    
    fig.add_trace(go.Scatter(
        x=nakit_akisi.index,
        y=nakit_akisi['Toplam_Varlik'],
        name='Toplam Varlık',
        line=dict(color='gold')
    ))
    
    fig.update_layout(
        title='Aylık Nakit Akışı ve Yatırım Analizi',
        xaxis_title='Tarih',
        yaxis_title='TL',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Özet tablo
    st.subheader("Aylık Nakit Akışı ve Yatırım Özeti")
    
    ozet_tablo = pd.DataFrame({
        'Tarih': nakit_akisi.index.strftime('%Y-%m'),
        'Toplam Gelir': nakit_akisi['Toplam_Gelir'].round(2),
        'Toplam Gider': nakit_akisi['Toplam_Gider'].round(2),
        'Net Nakit Akışı': nakit_akisi['Net_Nakit_Akisi'].round(2),
        'Aylık Yatırım': aylik_toplam_yatirim,
        'Net Nakit (Yatırımlar Dahil)': nakit_akisi['Net_Nakit_Akisi_Yatirimlar'].round(2),
        'Kümülatif Nakit': nakit_akisi['Kumulatif_Nakit'].round(2),
        'Toplam Yatırım Değeri': nakit_akisi['Toplam_Yatirim_Degeri'].round(2),
        'Toplam Varlık': nakit_akisi['Toplam_Varlik'].round(2)
    })
    
    st.dataframe(
        ozet_tablo.style.format({
            'Toplam Gelir': '{:,.2f} TL',
            'Toplam Gider': '{:,.2f} TL',
            'Net Nakit Akışı': '{:,.2f} TL',
            'Aylık Yatırım': '{:,.2f} TL',
            'Net Nakit (Yatırımlar Dahil)': '{:,.2f} TL',
            'Kümülatif Nakit': '{:,.2f} TL',
            'Toplam Yatırım Değeri': '{:,.2f} TL',
            'Toplam Varlık': '{:,.2f} TL'
        })
    )
    
    # Yatırım detayları
    st.subheader("Yatırım Detayları")
    yatirim_detay = pd.DataFrame({
        'Tarih': nakit_akisi.index.strftime('%Y-%m')
    })
    
    for kategori in yatirim_kategorileri.keys():
        yatirim_detay[f'{kategori} Değeri'] = nakit_akisi[f'Yatirim_{kategori}'].round(2)
    
    st.dataframe(
        yatirim_detay.style.format({
            f'{kategori} Değeri': '{:,.2f} TL' for kategori in yatirim_kategorileri.keys()
        })
    )