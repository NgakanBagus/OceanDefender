import streamlit as st
import pandas as pd
from datetime import datetime
import os
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk

DATA_FILE = "laporan_pencemaran.csv"
WATER_QUALITY_FILE = "water_pollution_disease.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if "Foto" not in df.columns:
            df["Foto"] = ""
        return df
    else:
        return pd.DataFrame(columns=["Tanggal", "Lokasi", "Deskripsi", "Foto"])
    
def load_water_data():
    if os.path.exists(WATER_QUALITY_FILE):
        return pd.read_csv(WATER_QUALITY_FILE)
    else:
        return pd.DataFrame()

def save_report(lokasi, deskripsi, foto):
    df = load_data()
    filename = ""

    if foto:
        file_extension = os.path.splitext(foto.name)[-1]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{lokasi.replace(' ', '_')}{file_extension}"
        file_path = os.path.join("uploads", filename)
        with open(file_path, "wb") as f:
            f.write(foto.getbuffer())

    new_row = {
        "Tanggal": datetime.now().strftime("%Y-%m-%d"),
        "Lokasi": lokasi,
        "Deskripsi": deskripsi,
        "Foto": filename  
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

with st.sidebar:
    menu = option_menu(
        menu_title="OceanDefender",
        options=["Home", "Tentang", "Visualisasi Data", "Artikel Edukatif", "Peta"]
    )

if menu == "Home":
    st.title("📝 Laporan Pencemaran Laut")
    st.markdown("Laporkan pencemaran laut yang kamu temui untuk membantu menjaga kebersihan laut Indonesia.")

    with st.form("form_laporan"):
        lokasi = st.text_input("Nama Lokasi")
        deskripsi = st.text_area("Deskripsi Pencemaran")
        foto = st.file_uploader("Unggah Foto (Opsional)", type=["jpg", "jpeg", "png"])
        submit = st.form_submit_button("Kirim Laporan")

        if submit:
            if lokasi.strip() and deskripsi.strip():
                save_report(lokasi, deskripsi, foto)
                st.success("✅ Laporan berhasil dikirim!")
            else:
                st.error("⚠️ Harap lengkapi semua kolom!")


    st.subheader("📋 Daftar Laporan Masuk")
    data = load_data()
    if not data.empty:
        for i, row in data[::-1].iterrows():
            st.markdown(f"### 📍 {row['Lokasi']} ({row['Tanggal']})")
            st.write(row["Deskripsi"])
            if row["Foto"]:
                st.image(f"uploads/{row['Foto']}", width=400)
            st.markdown("---")
    else:
        st.info("Belum ada laporan yang tersedia.") 


elif menu == "Tentang":
    st.title("Tentang OceanDefender")
    
    st.markdown("""
        <style>
        .about-box {
            background-color: #e0f7fa;
            padding: 20px;
            border-radius: 15px;
            border-left: 5px solid #00bcd4;
        }
        </style>
        <div class='about-box'>
            <h3 style="color:#012c4f">🌐 Apa itu <strong>OceanDefender</strong>?</h3>
            <p style="color:#012c4f;">
                <strong>OceanDefender</strong> adalah aplikasi web interaktif yang bertujuan untuk <em>menjaga kelestarian ekosistem laut</em> Indonesia melalui pelaporan pencemaran dan penyajian data kualitas air berbasis visualisasi data
            </p>
        </div>
        <br/>

        ### 🎯 Misi Kami
        - **Meningkatkan kesadaran publik** terhadap pencemaran laut
        - **Mempermudah masyarakat** untuk melaporkan pencemaran secara langsung
        - **Menyediakan informasi** berbasis data dan visualisasi kualitas air laut

        ---

        ### 🛠 Teknologi yang Digunakan
        - **Frontend**: Streamlit
        - **Backend**: Python
        - **Penyimpanan Data**: Lokal (CSV)

        ---

        ### 👥 Dibuat untuk
        - Masyarakat Sekitar
        - Pemerintah Daerah
        - Pelajar dan peneliti bidang kelautan 
        """, unsafe_allow_html=True)


elif menu == "Visualisasi Data":
    st.title("📊 Visualisasi Data Kualitas Air dan Kesehatan di Indonesia")

    water_df = load_water_data()

    if not water_df.empty:
        indo_df = water_df[water_df["Country"].str.lower() == "indonesia"].copy()

        if not indo_df.empty:
            wilayah = st.selectbox("📍 Pilih Wilayah di Indonesia", sorted(indo_df["Region"].unique()))
            df_filtered = indo_df[indo_df["Region"] == wilayah]

            st.markdown(f"### 🌍 Data untuk Wilayah: **{wilayah}**")

            st.subheader("🧪 Level Kontaminan (ppm)")
            fig1, ax1 = plt.subplots()
            sns.barplot(data=df_filtered, x="Year", y="Contaminant Level (ppm)", ax=ax1, palette="Blues_d")
            ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
            st.pyplot(fig1)
            st.markdown("💡 **Insight**: Level kontaminan cenderung meningkat/turun seiring waktu dapat menunjukkan perubahan kualitas sumber air. Tahun-tahun dengan lonjakan signifikan perlu ditelusuri penyebabnya")
            st.subheader("⚗️ Level pH Air")
            st.line_chart(df_filtered.set_index("Year")["pH Level"])
            st.markdown("💡 **Insight**: pH air normal berkisar antara 6.5 - 8.5. Penyimpangan dari rentang ini dapat berbahaya bagi makhluk hidup air dan menunjukkan adanya pencemaran kimia")

            st.subheader("🌫️ Tingkat Kekeruhan (NTU)")
            st.line_chart(df_filtered.set_index("Year")["Turbidity (NTU)"])
            st.markdown("💡 **Insight**: Tingkat kekeruhan yang tinggi menunjukkan partikel tersuspensi dalam air yang bisa berasal dari limbah, tanah longsor, atau aktivitas manusia seperti tambang")

            st.subheader("🌬️ Oksigen Terlarut (mg/L)")
            st.line_chart(df_filtered.set_index("Year")["Dissolved Oxygen (mg/L)"])
            st.markdown("💡 **Insight**: Kadar oksigen terlarut di bawah 5 mg/L dapat menyebabkan stres bagi kehidupan akuatik. Penurunan tajam bisa mengindikasikan eutrofikasi atau pencemaran organik")

            st.subheader("🧪 Kadar Nitrat (mg/L)")
            st.line_chart(df_filtered.set_index("Year")["Nitrate Level (mg/L)"])
            st.markdown("💡 **Insight**: Nitrat tinggi dapat berasal dari pupuk pertanian dan limbah domestik. Jika kadarnya tinggi, dapat menyebabkan masalah kesehatan seperti 'blue baby syndrome'")

            st.subheader("🧍‍♂️📈 Jumlah Kasus Penyakit per 100.000 Penduduk")
            penyakit_df = df_filtered.set_index("Year")[[
                "Diarrheal Cases per 100,000 people",
                "Cholera Cases per 100,000 people",
                "Typhoid Cases per 100,000 people"
            ]]
            latest_year = penyakit_df.index.max()
            latest_data = penyakit_df.loc[latest_year].sort_values(by="Diarrheal Cases per 100,000 people")

            fig2, ax2 = plt.subplots()
            latest_data.plot(kind="barh", ax=ax2, color="salmon")
            ax2.set_title(f"Jumlah Kasus Penyakit di Tahun {latest_year}")
            ax2.set_xlabel("Kasus per 100.000 penduduk")
            st.pyplot(fig2)
            st.markdown(f"💡 **Insight**: Data tahun **{latest_year}** menunjukkan penyakit terbanyak adalah **{latest_data.idxmax()}**. Hal ini dapat dikaitkan dengan kualitas air buruk dan sanitasi yang kurang memadai di wilayah tersebut")

            # Akses sanitasi
            st.subheader("🚰 Akses Sanitasi dan Air Bersih (% Populasi)")
            st.line_chart(df_filtered.set_index("Year")[[
                "Access to Clean Water (% of Population)",
                "Sanitation Coverage (% of Population)"
            ]])
            st.markdown("💡 **Insight**: Meningkatnya akses terhadap air bersih dan sanitasi yang layak berkorelasi dengan penurunan kasus penyakit berbasis air. Program peningkatan infrastruktur sangat krusial")

        else:
            st.warning("❌ Tidak ditemukan data untuk Indonesia pada dataset ini")
    else:
        st.warning("Dataset kualitas air belum tersedia")

elif menu == "Artikel Edukatif":
    st.title("📚 Artikel Edukatif")
    st.markdown("""
Berikut adalah beberapa artikel ilmiah dan berita terkini mengenai kondisi laut Indonesia:

- 🐠 [Mengapa Laut Kita Harus Bersih?](https://sains.kompas.com/read/2019/09/24/180000623/5-alasan-mengapa-kita-wajib-menjaga-lautan?page=all)
- 🛢️ [Dampak Pencemaran Minyak di Laut](https://portacademy.id/jenis-jenis-minyak-dan-dampaknya-terhadap-lingkungan-laut/)
- ♻️ [Solusi Penanganan Sampah Laut](https://kumparan.com/nuki-pratama/upaya-mengatasi-sampah-di-laut-20xwQnvF54N)
- 🧪 [Ekosistem Laut dan Perubahan Iklim](https://www.eea.europa.eu/publications/how-climate-change-impacts)

_(Daftar artikel ini dapat diperbarui sesuai kebutuhan)_
    """)

elif menu == "Peta":
    st.title("🗺️ Peta Interaktif Kualitas Air dan Lingkungan - Indonesia")

    water_df = load_water_data()

    if not water_df.empty:
        indo_df = water_df[water_df["Country"].str.lower() == "indonesia"]

        if not indo_df.empty:
            st.markdown("Peta ini menunjukkan distribusi wilayah berdasarkan data kualitas air dan lingkungan di Indonesia.")

            region_coords = {
                "Central": {"lat": -7.5, "lon": 110.0},
                "West": {"lat": -0.5, "lon": 101.5},
                "East": {"lat": -3.0, "lon": 129.0}
            }

            indo_df = indo_df.copy()
            indo_df["lat"] = indo_df["Region"].map(lambda x: region_coords.get(x, {}).get("lat"))
            indo_df["lon"] = indo_df["Region"].map(lambda x: region_coords.get(x, {}).get("lon"))

            latest_df = indo_df.sort_values("Year", ascending=False).drop_duplicates("Region")

            st.pydeck_chart(pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v9",
                initial_view_state=pdk.ViewState(
                    latitude=-2.5,
                    longitude=120.0,
                    zoom=4,
                    pitch=20,
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=latest_df,
                        get_position='[lon, lat]',
                        get_fill_color='[200, 30, 0, 160]',
                        get_radius=50000,
                        pickable=True,
                        auto_highlight=True,
                    )
                ],
                tooltip={
                    "html": "<b>{Region} Indonesia</b><br/>"
                            "Tahun: {Year}<br/>"
                            "Kontaminan: {Contaminant Level (ppm)} ppm<br/>"
                            "pH: {pH Level}<br/>"
                            "Kekeruhan: {Turbidity (NTU)} NTU<br/>"
                            "DO: {Dissolved Oxygen (mg/L)} mg/L<br/>"
                            "Akses Air Bersih: {Access to Clean Water (% of Population)}%",
                    "style": {
                        "backgroundColor": "steelblue",
                        "color": "white"
                    }
                }
            ))

        else:
            st.warning("❌ Tidak ditemukan data wilayah Indonesia")
    else:
        st.warning("Dataset belum tersedia")




