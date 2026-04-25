import streamlit as st
import pandas as pd
import difflib
import unicodedata
import io

st.set_page_config(
    page_title="Öğrenci No Eşleştirici",
    page_icon=":mortar_board:",
    layout="wide",
)


# ---------- Tema ----------

BRAND_PRIMARY = "#4F46E5"        # indigo
BRAND_PRIMARY_DARK = "#3730A3"
BRAND_PRIMARY_LIGHT = "#818CF8"
BRAND_ACCENT = "#F59E0B"         # amber
BRAND_ACCENT_DARK = "#D97706"
BRAND_SUCCESS = "#10B981"
BRAND_INFO = "#0EA5E9"
BRAND_WARN = "#F59E0B"
BRAND_DANGER = "#EF4444"
BRAND_BG = "#F9FAFB"
BRAND_TEXT = "#111827"
BRAND_TEXT_MUTED = "#6B7280"

CUSTOM_CSS = f"""
<style>
.stApp {{
    background: linear-gradient(180deg, #F9FAFB 0%, #EEF2FF 100%);
}}

/* Hero başlık */
.nk-hero {{
    background: linear-gradient(135deg, {BRAND_PRIMARY} 0%, {BRAND_PRIMARY_LIGHT} 60%, {BRAND_ACCENT} 130%);
    color: white;
    padding: 1.6rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.45);
}}
.nk-hero h1 {{
    color: white !important;
    margin: 0 0 0.25rem 0;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}}
.nk-hero p {{
    color: rgba(255,255,255,0.9);
    margin: 0;
    font-size: 1rem;
}}

/* Adım göstergesi */
.nk-steps {{
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.25rem;
    flex-wrap: wrap;
}}
.nk-step {{
    flex: 1;
    min-width: 140px;
    padding: 0.7rem 1rem;
    border-radius: 12px;
    background: white;
    border: 2px solid #E5E7EB;
    color: {BRAND_TEXT_MUTED};
    font-weight: 600;
    text-align: center;
    transition: all 0.2s;
}}
.nk-step.active {{
    background: linear-gradient(90deg, {BRAND_PRIMARY} 0%, {BRAND_PRIMARY_LIGHT} 100%);
    color: white;
    border-color: {BRAND_PRIMARY};
    box-shadow: 0 6px 18px -6px rgba(79,70,229,0.5);
}}
.nk-step.done {{
    background: #ECFDF5;
    color: {BRAND_SUCCESS};
    border-color: {BRAND_SUCCESS};
}}

/* Kart */
.nk-card {{
    background: white;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 14px -8px rgba(17,24,39,0.08);
    margin-bottom: 1rem;
}}
.nk-card-title {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {BRAND_PRIMARY_DARK};
    margin-bottom: 0.5rem;
}}

/* Etiket / badge */
.nk-badge {{
    display: inline-block;
    padding: 0.18rem 0.6rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    background: #EEF2FF;
    color: {BRAND_PRIMARY_DARK};
    margin-right: 0.3rem;
}}
.nk-badge.accent {{ background: #FEF3C7; color: {BRAND_ACCENT_DARK}; }}
.nk-badge.success {{ background: #D1FAE5; color: #065F46; }}

/* Butonlar */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {{
    background: linear-gradient(90deg, {BRAND_PRIMARY} 0%, {BRAND_PRIMARY_LIGHT} 100%);
    color: white;
    border: none;
    padding: 0.55em 1.2em;
    border-radius: 10px;
    font-weight: 700;
    transition: transform 0.08s, box-shadow 0.15s, filter 0.15s;
    box-shadow: 0 4px 12px -4px rgba(79,70,229,0.45);
}}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {{
    transform: translateY(-1px);
    filter: brightness(1.05);
    box-shadow: 0 8px 18px -6px rgba(79,70,229,0.55);
    color: white;
}}
.stButton > button:focus, .stDownloadButton > button:focus, .stFormSubmitButton > button:focus {{
    color: white;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.35);
}}

/* İkincil buton (secondary) — daha sade */
.stButton > button[kind="secondary"] {{
    background: white;
    color: {BRAND_PRIMARY_DARK};
    border: 2px solid {BRAND_PRIMARY_LIGHT};
    box-shadow: none;
}}
.stButton > button[kind="secondary"]:hover {{
    background: #EEF2FF;
    color: {BRAND_PRIMARY_DARK};
}}

/* Progress bar rengi */
.stProgress > div > div > div > div {{
    background: linear-gradient(90deg, {BRAND_PRIMARY} 0%, {BRAND_ACCENT} 100%);
}}

/* File uploader */
[data-testid="stFileUploader"] section {{
    border: 2px dashed {BRAND_PRIMARY_LIGHT};
    background: #F5F3FF;
    border-radius: 12px;
}}

/* Başlık renkleri */
h1, h2, h3 {{
    color: {BRAND_PRIMARY_DARK};
    font-weight: 700;
}}

/* st.success / info / warning / error rengini canlandır */
[data-testid="stAlert"] {{
    border-radius: 12px;
    border-left-width: 6px;
}}

/* Alt bilgi */
.nk-footer {{
    text-align: center;
    color: {BRAND_TEXT_MUTED};
    font-size: 0.85rem;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #E5E7EB;
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero(subtitle="TXT sınav verisi ile Excel öğrenci listesini akıllı eşleştirme"):
    st.markdown(
        f"""
        <div class="nk-hero">
            <h1>Öğrenci No Eşleştirici</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_steps(current_step):
    """current_step: 0 (yükleme), 1 (eşleştirme), 2 (sonuç)"""
    labels = ["1. Veri & Sınıf Seçimi", "2. Eşleştirme", "3. Sonuç"]
    parts = []
    for i, label in enumerate(labels):
        if i < current_step:
            cls = "done"
        elif i == current_step:
            cls = "active"
        else:
            cls = ""
        parts.append(f'<div class="nk-step {cls}">{label}</div>')
    st.markdown(f'<div class="nk-steps">{"".join(parts)}</div>', unsafe_allow_html=True)


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
    """Excel listesindeki her satır için isim varyasyonlarını önceden hesapla.
    Liste'nin index sırasına göre list döner."""
    out = []
    for _, list_row in liste.iterrows():
        ad_soyad = list_row['Ad_soyad']
        soyad_ad = list_row['Soyad_ad']
        out.append(prepare_name_variations(ad_soyad) | prepare_name_variations(soyad_ad))
    return out


def find_matches(ad_soyad, liste, liste_variations, alan_col, sinif_col, sube_col, threshold=0.70):
    """Bir TXT öğrencisi için Excel listesinden eşleşmeleri bul.
    liste'nin index'i 0..N-1 (reset_index uygulanmış) olmalı."""
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
    """Sadece TXT'ye özel state'i temizle. Excel listesi, sınıf filtresi ve sütun ayarları korunur."""
    for k in [
        "data", "data_okuma", "idx",
        "current_eslesmeler", "current_eslesmeler_idx",
        "liste_active", "liste_active_variations",
    ]:
        st.session_state.pop(k, None)


def reset_excel_only():
    """Excel listesi ile ilgili her şeyi sil (sütun ayarları korunur)."""
    for k in [
        "liste_full", "liste_full_variations",
        "liste_active", "liste_active_variations",
        "alan_col", "sinif_col", "sube_col",
        "selected_sinif", "available_sinif",
        "current_eslesmeler", "current_eslesmeler_idx",
        "data", "data_okuma", "idx",
    ]:
        st.session_state.pop(k, None)


def reset_all_state():
    """Tüm state'i sıfırla (yeni kurum için)."""
    for k in list(st.session_state.keys()):
        del st.session_state[k]


def read_excel_into_state(excel_file):
    """Excel'i oku, varyasyonları hesapla, sütunları tespit et, sınıfları çıkar."""
    try:
        liste = pd.read_excel(excel_file)
    except Exception as e:
        st.error(f"Excel okuma hatası: {e}")
        return False

    if "Adı" not in liste.columns or "Soyadı" not in liste.columns:
        st.error("Excel dosyasında 'Adı' ve 'Soyadı' sütunları bulunamadı.")
        return False

    liste = liste.reset_index(drop=True)
    liste['Ad_soyad'] = liste.apply(lambda r: f"{r['Adı']} {r['Soyadı']}", axis=1)
    liste['Soyad_ad'] = liste.apply(lambda r: f"{r['Soyadı']} {r['Adı']}", axis=1)

    st.session_state.liste_full = liste
    st.session_state.liste_full_variations = precompute_liste_variations(liste)
    st.session_state.alan_col = get_col(liste, ["Alan", "ALAN", "alan", "Alanı", "ALANI", "Dal", "DAL", "dal"])
    st.session_state.sinif_col = get_col(liste, ["Sınıf", "SINIF", "sinif", "Sinif"])
    st.session_state.sube_col = get_col(liste, ["Şube", "ŞUBE", "sube", "Sube", "SUBE"])

    if st.session_state.sinif_col:
        sinif_values = liste[st.session_state.sinif_col].dropna().astype(str).str.strip()
        sinif_values = sinif_values[sinif_values != ""]
        # Doğal sıralama: önce sayısal sınıflar, sonra harfli (Mezun vs.)
        unique_sinif = sorted(set(sinif_values), key=lambda x: (not x[:2].strip().isdigit(), x))
        st.session_state.available_sinif = unique_sinif
        st.session_state.selected_sinif = unique_sinif.copy()
    else:
        st.session_state.available_sinif = []
        st.session_state.selected_sinif = []

    return True


# ---------- Hero & Adımlar ----------

render_hero()
render_steps(st.session_state.get("step", 0))


# ---------- State başlangıç değerleri ----------

st.session_state.setdefault("step", 0)
st.session_state.setdefault("data_okuma", [])
st.session_state.setdefault("idx", 0)
# Sütun konumları (1-tabanlı, kullanıcının gördüğü değerler).
# Form widget'ına 'value=' ile geçtiğimiz için Streamlit'in widget-state
# temizleme tuhaflığından bağımsız olarak her oturumda korunur.
st.session_state.setdefault("col_no_ilk", 2)
st.session_state.setdefault("col_no_son", 7)
st.session_state.setdefault("col_ad_ilk", 13)
st.session_state.setdefault("col_ad_son", 32)
st.session_state.setdefault("col_son_sutun", 215)


# ---------- ADIM 0: VERİ & SINIF SEÇİMİ ----------

if st.session_state.step == 0:
    has_excel = "liste_full" in st.session_state

    # --- Excel yükleme bloğu ---
    if not has_excel:
        st.markdown(
            '<div class="nk-card"><div class="nk-card-title">1. Excel öğrenci listesini yükleyin</div>'
            'Liste yüklendiğinde sınıf seviyeleri otomatik olarak çıkarılır.</div>',
            unsafe_allow_html=True,
        )
        excel_file = st.file_uploader("Excel dosyasını seçiniz (.xlsx)", type=["xlsx"], key="excel_uploader")
        if excel_file is not None:
            with st.spinner("Excel okunuyor ve isim varyasyonları hazırlanıyor..."):
                ok = read_excel_into_state(excel_file)
            if ok:
                st.rerun()
        st.stop()

    # --- Excel yüklendi: özet kart ---
    liste_full = st.session_state.liste_full
    sinif_col = st.session_state.sinif_col
    alan_col = st.session_state.alan_col

    badges = [f'<span class="nk-badge">{len(liste_full)} öğrenci</span>']
    if sinif_col:
        badges.append(f'<span class="nk-badge accent">Sınıf sütunu: {sinif_col}</span>')
    if alan_col:
        badges.append(f'<span class="nk-badge success">Alan sütunu: {alan_col}</span>')

    col_info, col_change = st.columns([4, 1])
    with col_info:
        st.markdown(
            f'<div class="nk-card"><div class="nk-card-title">Excel listesi hazır</div>'
            f'{"".join(badges)}</div>',
            unsafe_allow_html=True,
        )
    with col_change:
        st.write("")
        if st.button("Excel'i değiştir", use_container_width=True, key="btn_change_excel"):
            reset_excel_only()
            st.rerun()

    # --- Sınıf filtresi ---
    if st.session_state.available_sinif:
        st.markdown(
            '<div class="nk-card"><div class="nk-card-title">2. Sınav hangi sınıflara uygulanıyor?</div>'
            'Yalnızca seçtiğiniz sınıflardaki öğrenciler arasında eşleştirme yapılır. '
            'Örneğin TYT için 12. sınıf ve Mezun seçebilirsiniz.</div>',
            unsafe_allow_html=True,
        )
        col_pick, col_quick = st.columns([3, 1])
        with col_quick:
            if st.button("Tümünü seç", use_container_width=True, key="btn_pick_all"):
                st.session_state.selected_sinif = st.session_state.available_sinif.copy()
                st.rerun()
            if st.button("Tümünü temizle", use_container_width=True, key="btn_pick_none"):
                st.session_state.selected_sinif = []
                st.rerun()
        with col_pick:
            st.session_state.selected_sinif = st.multiselect(
                "Eşleştirmede kullanılacak sınıflar",
                options=st.session_state.available_sinif,
                default=st.session_state.selected_sinif,
                key="multiselect_sinif",
            )
        n_filt = liste_full[sinif_col].astype(str).str.strip().isin(st.session_state.selected_sinif).sum()
        st.caption(
            f"Seçilen sınıflarda **{n_filt}** öğrenci var "
            f"(toplam {len(liste_full)} kayıttan)."
        )
    else:
        st.warning("Excel'de 'Sınıf' sütunu bulunamadı — sınıf filtrelemesi devre dışı, tüm liste kullanılacak.")

    # --- TXT yükleme + sütun ayarları ---
    st.markdown(
        '<div class="nk-card"><div class="nk-card-title">3. TXT sınav dosyası ve sütun ayarları</div></div>',
        unsafe_allow_html=True,
    )
    txt_file = st.file_uploader("TXT dosyasını seçiniz", type=["txt"], key="txt_uploader")

    with st.form("col_form"):
        st.markdown("**Kolon konumları (1-tabanlı)** — önceki oturumdaki değerler hatırlanır, gerekirse değiştirin.")
        c1, c2 = st.columns(2)
        with c1:
            no_ilk_1 = st.number_input(
                "Öğrenci No Başlangıç Sütunu", min_value=1, step=1,
                value=st.session_state.col_no_ilk,
            )
            ad_ilk_1 = st.number_input(
                "Ad Başlangıç Sütunu", min_value=1, step=1,
                value=st.session_state.col_ad_ilk,
            )
            son_sutun_1 = st.number_input(
                "Son Sütun Numarası", min_value=1, step=1,
                value=st.session_state.col_son_sutun,
            )
        with c2:
            no_son_1 = st.number_input(
                "Öğrenci No Bitiş Sütunu", min_value=1, step=1,
                value=st.session_state.col_no_son,
            )
            ad_son_1 = st.number_input(
                "Ad Bitiş Sütunu", min_value=1, step=1,
                value=st.session_state.col_ad_son,
            )
        submit_cols = st.form_submit_button("İşleme Başla")

    if submit_cols:
        if not txt_file:
            st.warning("TXT dosyası yüklenmeli!")
            st.stop()
        if st.session_state.available_sinif and not st.session_state.selected_sinif:
            st.warning("En az bir sınıf seçmelisiniz!")
            st.stop()

        # 1-tabanlı değerleri sonraki oturumlar için sakla
        st.session_state.col_no_ilk = no_ilk_1
        st.session_state.col_no_son = no_son_1
        st.session_state.col_ad_ilk = ad_ilk_1
        st.session_state.col_ad_son = ad_son_1
        st.session_state.col_son_sutun = son_sutun_1

        # 0-tabanlı slice değerleri (işleme için)
        no_ilk = no_ilk_1 - 1
        no_son = no_son_1 - 1
        ad_ilk = ad_ilk_1 - 1
        ad_son = ad_son_1 - 1
        son_sutun = son_sutun_1 - 1

        st.session_state.no_ilk = no_ilk
        st.session_state.no_son = no_son
        st.session_state.ad_ilk = ad_ilk
        st.session_state.ad_son = ad_son
        st.session_state.son_sutun = son_sutun
        st.session_state.no_len = no_son - no_ilk

        # Aktif (filtrelenmiş) liste'yi hazırla
        if sinif_col and st.session_state.available_sinif:
            mask = liste_full[sinif_col].astype(str).str.strip().isin(st.session_state.selected_sinif)
            keep_indices = list(liste_full.index[mask])
            active = liste_full.loc[mask].reset_index(drop=True)
            active_vars = [st.session_state.liste_full_variations[i] for i in keep_indices]
        else:
            active = liste_full.reset_index(drop=True)
            active_vars = list(st.session_state.liste_full_variations)

        if len(active) == 0:
            st.error("Seçilen sınıflarda öğrenci yok. Lütfen başka sınıf seçin.")
            st.stop()

        st.session_state.liste_active = active
        st.session_state.liste_active_variations = active_vars

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
    liste = st.session_state.liste_active
    liste_variations = st.session_state.liste_active_variations
    alan_col = st.session_state.alan_col
    sinif_col = st.session_state.sinif_col
    sube_col = st.session_state.sube_col
    data = st.session_state.data
    no_ilk = st.session_state.no_ilk
    no_son = st.session_state.no_son
    ad_ilk = st.session_state.ad_ilk
    ad_son = st.session_state.ad_son
    son_sutun = st.session_state.son_sutun
    no_len = st.session_state.no_len
    idx = st.session_state.idx

    if idx >= len(data):
        st.session_state.step = 2
        st.rerun()

    # Bilgi şeridi
    sinif_info = ""
    if st.session_state.get("selected_sinif"):
        sinif_info = (
            f'<span class="nk-badge accent">Sınıflar: '
            f'{", ".join(st.session_state.selected_sinif)}</span>'
        )
    st.markdown(
        f'<div class="nk-card" style="padding:0.7rem 1rem;">'
        f'<span class="nk-badge">Aktif liste: {len(liste)} öğrenci</span>'
        f'{sinif_info}'
        f'<span class="nk-badge success">İşlendi: {idx}/{len(data)}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.progress(idx / len(data), text=f"{idx}/{len(data)} işlendi")

    row = data.iloc[idx]
    ad_soyad = row['Ad_Soyad']

    if st.session_state.get("current_eslesmeler_idx") != idx:
        with st.spinner(f"'{ad_soyad}' için eşleşmeler aranıyor..."):
            st.session_state.current_eslesmeler = find_matches(
                ad_soyad, liste, liste_variations, alan_col, sinif_col, sube_col
            )
        st.session_state.current_eslesmeler_idx = idx
    eslesmeler = st.session_state.current_eslesmeler

    st.markdown(
        f'<div class="nk-card"><div class="nk-card-title">'
        f'Öğrenci #{idx+1} / {len(data)} &nbsp;—&nbsp; {ad_soyad}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    def kaydet_ve_ilerle(ogr_no_str):
        st.session_state.data_okuma.append([
            row[0][0:no_ilk],
            ogr_no_str.rjust(no_len) if len(ogr_no_str) < no_len else ogr_no_str,
            row[0][no_son:son_sutun],
        ])
        data.at[idx, 'Kayıt'] = True
        st.session_state.idx += 1

    # --- TXT satırının tamamı (detaylı inceleme için) ---
    raw_line = row[0] if isinstance(row[0], str) else str(row[0])
    no_slice = raw_line[no_ilk:no_son]
    ad_slice = raw_line[ad_ilk:ad_son]
    with st.expander(
        "TXT satırının tamamını göster",
        expanded=(len(eslesmeler) == 0),
    ):
        st.code(raw_line, language="text")
        st.caption(
            f"Numara bölgesi (sütun {no_ilk+1}-{no_son}): `{no_slice}`  •  "
            f"Ad bölgesi (sütun {ad_ilk+1}-{ad_son}): `{ad_slice}`  •  "
            f"Toplam uzunluk: {len(raw_line)} karakter"
        )

    # --- Yan menü: Excel'de manuel arama ---
    with st.sidebar:
        st.markdown("### Manuel Arama")
        st.caption(
            "Eşleşme bulunamazsa Excel listesinde sınıf veya isimle arayıp "
            "doğrudan öğrenciyi seçebilirsiniz."
        )

        full_liste = st.session_state.liste_full
        sinif_col_full = st.session_state.sinif_col
        available_sinif_full = st.session_state.get("available_sinif", [])

        sb_sinif = []
        if available_sinif_full and sinif_col_full:
            st.session_state.setdefault("sb_sinif", list(available_sinif_full))
            sb_sinif = st.multiselect(
                "Sınıf filtresi",
                options=available_sinif_full,
                key="sb_sinif",
            )

        sb_query = st.text_input(
            "İsim ara",
            placeholder="örn. ahmet yılmaz",
            key="sb_query",
        )

        filtered = full_liste
        if sb_sinif and sinif_col_full:
            filtered = filtered[
                filtered[sinif_col_full].astype(str).str.strip().isin(sb_sinif)
            ]
        if sb_query.strip():
            q = normalize_turkish(sb_query)
            filtered = filtered[
                filtered['Ad_soyad'].apply(lambda x: q in normalize_turkish(str(x)))
            ]

        st.caption(f"**{len(filtered)}** sonuç")

        max_show = 100
        if len(filtered) > 0:
            shown = filtered.head(max_show)
            opt_labels = []
            opt_no = []
            for _, r in shown.iterrows():
                sinif_str = str(r[sinif_col_full]) if sinif_col_full else "?"
                opt_labels.append(
                    f"{r['Ad_soyad']} — No:{r['Öğrenci No']} — Sınıf:{sinif_str}"
                )
                opt_no.append(str(r["Öğrenci No"]))

            sel_label = st.selectbox(
                "Öğrenci seç",
                options=opt_labels,
                key="sb_pick",
            )

            if st.button(
                "Bu öğrenciyi kaydet ve ilerle",
                use_container_width=True,
                key="sb_save",
            ):
                if sel_label in opt_labels:
                    kaydet_ve_ilerle(opt_no[opt_labels.index(sel_label)])
                    st.rerun()

            if len(filtered) > max_show:
                st.caption(f"İlk {max_show} sonuç gösteriliyor — daha çok daraltın.")
        else:
            st.info("Filtreye uyan öğrenci yok.")

    # OTOMATİK EŞLEŞME (tek sonuç ve >= 0.95)
    if len(eslesmeler) == 1 and eslesmeler[0][2] >= 0.95:
        st.success(
            f"Otomatik eşleşme: **{eslesmeler[0][0]}** "
            f"— No: `{eslesmeler[0][1]}` — Oran: {eslesmeler[0][2]:.2f}"
        )
        kaydet_ve_ilerle(str(eslesmeler[0][1]))
        st.rerun()
    else:
        with st.form("ogrenci_form"):
            if len(eslesmeler) > 0:
                st.info(
                    f"**{len(eslesmeler)}** eşleşme bulundu. "
                    f"En yüksek benzerlik: **{eslesmeler[0][2]:.2f}**"
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
                    manuel_no = st.text_input(f"{ad_soyad} için manuel öğrenci numarası giriniz:")
            else:
                st.warning(f"{ad_soyad} için eşleşme bulunamadı!")
                secenekler = ["Hiçbiri (manuel no gir)", "Atla (kaydetme, sonraki öğrenciye geç)"]
                secim = st.radio("Seçim", secenekler, index=0)
                manuel_no = ""
                if secim.startswith("Hiçbiri"):
                    manuel_no = st.text_input(f"{ad_soyad} için manuel öğrenci numarası giriniz:")

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
    st.markdown(
        '<div class="nk-card"><div class="nk-card-title">Tüm öğrenciler işlendi</div>'
        'Sonuçları aşağıdan inceleyebilir, TXT olarak indirebilirsiniz.</div>',
        unsafe_allow_html=True,
    )

    df_okuma = pd.DataFrame(st.session_state.data_okuma, columns=["ön", "No", "son"])
    st.dataframe(df_okuma, use_container_width=True)

    txt = io.StringIO()
    df_okuma.to_csv(txt, header=False, index=False, sep='@')
    st.download_button(
        label="Sonuç TXT dosyasını indir",
        data=txt.getvalue().encode("cp1254", errors="replace"),
        file_name="sonuc.txt",
        mime="text/plain",
        use_container_width=True,
    )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Aynı Kurum, Yeni TXT",
            help="Excel listesini, sınıf seçimini ve sütun ayarlarını koruyarak yeni TXT işle.",
            use_container_width=True,
            key="btn_same_inst",
        ):
            reset_only_txt_state()
            st.session_state.step = 0
            st.rerun()
    with col2:
        if st.button(
            "Yeni Kurum (Sıfırdan)",
            help="Excel listesi dahil her şeyi sıfırla.",
            use_container_width=True,
            key="btn_new_inst",
        ):
            reset_all_state()
            st.rerun()


st.markdown(
    '<div class="nk-footer">Öğrenci No Eşleştirici — '
    '<a href="https://www.dijimind.com" target="_blank" '
    f'style="color:{BRAND_PRIMARY}; text-decoration:none; font-weight:600;">dijimind.com</a>'
    '</div>',
    unsafe_allow_html=True,
)
