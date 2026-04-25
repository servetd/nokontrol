import streamlit as st
import pandas as pd
import difflib
import unicodedata
import io

st.set_page_config(page_title="Öğrenci No Eşleştirici", layout="wide")


# ---------- Yardımcı fonksiyonlar ----------

def normalize_turkish(text):
    if not isinstance(text, str):
        return ''
    text = text.replace('İ', 'i').replace('I', 'ı').lower()
    text = ' '.join(text.split())
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def turkish_to_english(text):
    if not isinstance(text, str):
        return ''
    tr_chars = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u'}
    text = text.lower()
    for tr_char, en_char in tr_chars.items():
        text = text.replace(tr_char, en_char)
    return text


def prepare_name_variations(name):
    if not isinstance(name, str):
        return set()
    name = name.strip()
    variations = {name}
    normalized = ' '.join(name.split())
    variations.add(normalized)
    turkish_normalized = normalize_turkish(normalized)
    variations.add(turkish_normalized)
    english_version = turkish_to_english(turkish_normalized)
    variations.add(english_version)
    return {v for v in variations if v}


def get_col(df, col_list):
    for c in col_list:
        if c in df.columns:
            return c
    return None


def precompute_liste_variations(liste):
    """Excel listesindeki her satır için isim varyasyonlarını önceden hesapla."""
    out = []
    for _, list_row in liste.iterrows():
        ad_soyad = list_row['Ad_soyad']
        soyad_ad = list_row['Soyad_ad']
        out.append(prepare_name_variations(ad_soyad) | prepare_name_variations(soyad_ad))
    return out


def find_matches(ad_soyad, liste, liste_variations, alan_col, sinif_col, sube_col, threshold=0.70):
    """Bir TXT öğrencisi için Excel listesinden eşleşmeleri bul."""
    name_variations = prepare_name_variations(ad_soyad)
    eslesmeler = []
    for s, list_row in liste.iterrows():
        variations = liste_variations[s]
        max_ratio = 0.0
        for var1 in name_variations:
            for var2 in variations:
                ratio = difflib.SequenceMatcher(None, var1, var2).ratio()
                if ratio > max_ratio:
                    max_ratio = ratio
                    if max_ratio >= 1.0:
                        break
            if max_ratio >= 1.0:
                break
        if max_ratio > threshold:
            alan = str(list_row[alan_col]) if alan_col else "?"
            sinif = str(list_row[sinif_col]) if sinif_col else "?"
            sube = str(list_row[sube_col]) if sube_col else "?"
            eslesmeler.append(
                (list_row['Ad_soyad'], list_row["Öğrenci No"], max_ratio, alan, sinif, sube)
            )
    eslesmeler.sort(key=lambda x: x[2], reverse=True)
    return eslesmeler


def reset_only_txt_state():
    """Sadece TXT'ye özel state'i temizle. Excel listesi ve sütun ayarları korunur."""
    for k in ["data", "data_okuma", "idx", "current_eslesmeler", "current_eslesmeler_idx"]:
        st.session_state.pop(k, None)


def reset_all_state():
    """Tüm state'i sıfırla (yeni kurum için)."""
    for k in list(st.session_state.keys()):
        del st.session_state[k]


# ---------- Başlık ----------

st.title("Öğrenci No Eşleştirici ve Kontrol Paneli")

# ---------- State başlangıç değerleri ----------

st.session_state.setdefault("step", 0)            # 0: form, 1: işlem, 2: sonuç
st.session_state.setdefault("data_okuma", [])
st.session_state.setdefault("idx", 0)
# Sütun varsayılanları (kullanıcı değiştirirse güncellenir, yeni TXT'de korunur)
st.session_state.setdefault("no_ilk_input", 2)
st.session_state.setdefault("no_son_input", 7)
st.session_state.setdefault("ad_ilk_input", 13)
st.session_state.setdefault("ad_son_input", 32)
st.session_state.setdefault("son_sutun_input", 215)


# ---------- ADIM 0: SÜTUN FORMU ----------

if st.session_state.step == 0:
    has_cached_liste = "liste" in st.session_state and "liste_variations" in st.session_state

    if has_cached_liste:
        st.success(
            f"Aynı kurumun Excel listesi bellekte ({len(st.session_state.liste)} öğrenci). "
            "Yalnızca yeni TXT dosyasını yüklemeniz yeterli."
        )
        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button("Excel listesini değiştir", use_container_width=True):
                for k in ["liste", "liste_variations", "alan_col", "sinif_col", "sube_col"]:
                    st.session_state.pop(k, None)
                st.rerun()

    excel_file = None
    if not has_cached_liste:
        excel_file = st.file_uploader("Excel dosyasını seçiniz (.xlsx)", type=["xlsx"])
    txt_file = st.file_uploader("TXT dosyasını seçiniz", type=["txt"])

    with st.form("col_form"):
        st.markdown("### Kolon Konumlarını Giriniz")
        no_ilk = st.number_input(
            "Öğrenci No Başlangıç Sütunu", min_value=1, step=1, key="no_ilk_input",
        ) - 1
        no_son = st.number_input(
            "Öğrenci No Bitiş Sütunu", min_value=1, step=1, key="no_son_input",
        ) - 1
        ad_ilk = st.number_input(
            "Ad Başlangıç Sütunu", min_value=1, step=1, key="ad_ilk_input",
        ) - 1
        ad_son = st.number_input(
            "Ad Bitiş Sütunu", min_value=1, step=1, key="ad_son_input",
        ) - 1
        son_sutun = st.number_input(
            "Son Sütun Numarası", min_value=1, step=1, key="son_sutun_input",
        ) - 1
        submit_cols = st.form_submit_button("Başla")

    if submit_cols:
        if not has_cached_liste and not excel_file:
            st.warning("Excel dosyası yüklenmeli!")
            st.stop()
        if not txt_file:
            st.warning("TXT dosyası yüklenmeli!")
            st.stop()

        # Sütun ayarlarını kaydet
        st.session_state.no_ilk = no_ilk
        st.session_state.no_son = no_son
        st.session_state.ad_ilk = ad_ilk
        st.session_state.ad_son = ad_son
        st.session_state.son_sutun = son_sutun
        st.session_state.no_len = no_son - no_ilk

        # Excel listesi (yalnızca gerekirse oku)
        if not has_cached_liste:
            try:
                liste = pd.read_excel(excel_file)
            except Exception as e:
                st.error(f"Excel okuma hatası: {e}")
                st.stop()
            liste['Ad_soyad'] = liste.apply(
                lambda row: f"{row['Adı']} {row['Soyadı']}", axis=1
            )
            liste['Soyad_ad'] = liste.apply(
                lambda row: f"{row['Soyadı']} {row['Adı']}", axis=1
            )
            st.session_state.liste = liste
            st.session_state.liste_variations = precompute_liste_variations(liste)
            st.session_state.alan_col = get_col(
                liste, ["Alan", "ALAN", "alan", "Alanı", "ALANI", "Dal", "DAL", "dal"]
            )
            st.session_state.sinif_col = get_col(
                liste, ["Sınıf", "SINIF", "sinif", "Sinif"]
            )
            st.session_state.sube_col = get_col(
                liste, ["Şube", "ŞUBE", "sube", "Sube", "SUBE"]
            )

        # TXT'yi oku
        try:
            data = pd.read_csv(txt_file, header=None, encoding="cp1254")
        except Exception as e:
            st.error(f"TXT okuma hatası: {e}")
            st.stop()

        data['No'] = [row[no_ilk:no_son].strip() for row in data[0]]
        data['Ad_Soyad'] = [' '.join(row[ad_ilk:ad_son].strip().split()) for row in data[0]]
        data['Kayıt'] = False
        st.session_state.data = data
        st.session_state.data_okuma = []
        st.session_state.idx = 0
        st.session_state.step = 1
        st.rerun()


# ---------- ADIM 1: ÖĞRENCİ İŞLEME ----------

elif st.session_state.step == 1:
    liste = st.session_state.liste
    liste_variations = st.session_state.liste_variations
    alan_col = st.session_state.alan_col
    sinif_col = st.session_state.sinif_col
    sube_col = st.session_state.sube_col
    data = st.session_state.data
    no_ilk = st.session_state.no_ilk
    no_son = st.session_state.no_son
    son_sutun = st.session_state.son_sutun
    no_len = st.session_state.no_len
    idx = st.session_state.idx

    if idx >= len(data):
        st.session_state.step = 2
        st.rerun()

    # İlerleme çubuğu
    st.progress(idx / len(data), text=f"{idx}/{len(data)} işlendi")

    row = data.iloc[idx]
    ad_soyad = row['Ad_Soyad']

    # Eşleşmeleri yalnızca idx değiştiğinde hesapla (rerun'larda yeniden çalışmasın)
    if st.session_state.get("current_eslesmeler_idx") != idx:
        with st.spinner(f"'{ad_soyad}' için eşleşmeler aranıyor..."):
            st.session_state.current_eslesmeler = find_matches(
                ad_soyad, liste, liste_variations, alan_col, sinif_col, sube_col
            )
        st.session_state.current_eslesmeler_idx = idx
    eslesmeler = st.session_state.current_eslesmeler

    st.markdown(f"### {idx+1}/{len(data)} : **{ad_soyad}** öğrencisi için işlem")

    def kaydet_ve_ilerle(ogr_no_str):
        st.session_state.data_okuma.append([
            row[0][0:no_ilk],
            ogr_no_str.rjust(no_len) if len(ogr_no_str) < no_len else ogr_no_str,
            row[0][no_son:son_sutun],
        ])
        data.at[idx, 'Kayıt'] = True
        st.session_state.idx += 1

    # OTOMATİK EŞLEŞME (tek sonuç ve >= 0.95)
    if len(eslesmeler) == 1 and eslesmeler[0][2] >= 0.95:
        st.success(
            f"Otomatik eşleşme: {eslesmeler[0][0]} "
            f"(No: {eslesmeler[0][1]}, Oran: {eslesmeler[0][2]:.2f})"
        )
        kaydet_ve_ilerle(str(eslesmeler[0][1]))
        st.rerun()
    else:
        with st.form("ogrenci_form"):
            if len(eslesmeler) > 0:
                st.info(
                    f"{len(eslesmeler)} eşleşme bulundu. "
                    f"En yüksek benzerlik: {eslesmeler[0][2]:.2f}"
                )
                secenekler = [
                    f"{i+1}. {e[0]} | No:{e[1]} | "
                    f"Alan:{e[3]}, Sınıf:{e[4]}, Şube:{e[5]} | Oran:{e[2]:.2f}"
                    for i, e in enumerate(eslesmeler)
                ]
                secenekler.append("Hiçbiri (manuel no gir)")
                secenekler.append("Atla (kaydetme, sonraki öğrenciye geç)")
                secim = st.radio("Uygun öğrenciyi seçiniz", secenekler, index=0)
                manuel_no = ""
                if secim.startswith("Hiçbiri"):
                    manuel_no = st.text_input(
                        f"{ad_soyad} için manuel öğrenci numarası giriniz:"
                    )
            else:
                st.warning(f"{ad_soyad} için eşleşme bulunamadı!")
                secenekler = ["Hiçbiri (manuel no gir)", "Atla (kaydetme, sonraki öğrenciye geç)"]
                secim = st.radio("Seçim", secenekler, index=0)
                manuel_no = ""
                if secim.startswith("Hiçbiri"):
                    manuel_no = st.text_input(
                        f"{ad_soyad} için manuel öğrenci numarası giriniz:"
                    )

            kaydet = st.form_submit_button("Kaydet ve Sonraki")

        if kaydet:
            if secim.startswith("Atla"):
                st.session_state.idx += 1
                st.rerun()
            elif secim.startswith("Hiçbiri"):
                if manuel_no.strip() == "":
                    st.warning("Numara girilmedi!")
                else:
                    kaydet_ve_ilerle(str(manuel_no).strip())
                    st.rerun()
            else:
                secilen_idx = int(secim.split(".")[0]) - 1
                kaydet_ve_ilerle(str(eslesmeler[secilen_idx][1]))
                st.rerun()


# ---------- ADIM 2: SONUÇ ----------

elif st.session_state.step == 2:
    st.success("Tüm öğrenciler işlendi. Sonuçlar aşağıda:")
    df_okuma = pd.DataFrame(
        st.session_state.data_okuma, columns=["ön", "No", "son"]
    )
    st.dataframe(df_okuma, use_container_width=True)

    txt = io.StringIO()
    df_okuma.to_csv(txt, header=False, index=False, sep='@')
    st.download_button(
        label="Sonuç TXT dosyasını indir",
        data=txt.getvalue().encode("cp1254", errors="replace"),
        file_name="sonuc.txt",
        mime="text/plain",
    )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Aynı Kurum, Yeni TXT",
            help="Excel listesini ve sütun ayarlarını koruyarak yeni bir TXT işle.",
            use_container_width=True,
        ):
            reset_only_txt_state()
            st.session_state.step = 0
            st.rerun()
    with col2:
        if st.button(
            "Yeni Kurum (Sıfırdan)",
            help="Excel listesi dahil her şeyi sıfırla.",
            use_container_width=True,
        ):
            reset_all_state()
            st.rerun()
