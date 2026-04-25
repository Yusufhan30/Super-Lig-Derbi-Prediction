import math
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────
# SAYFA AYARLARI
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Galatasaray vs Fenerbahçe | Derbi Analiz",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background-color: #0e0e0e; }

    .hero-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }
    .hero-sub {
        text-align: center;
        font-size: 1.05rem;
        color: #aaaaaa;
        margin-bottom: 2rem;
    }
    .gs-color { color: #e3000f; }
    .fb-color { color: #003399; }

    .metric-card {
        background: linear-gradient(135deg, #1a1a1a, #222);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        border: 1px solid #333;
        text-align: center;
    }
    .metric-label {
        color: #888;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 900;
        margin-top: 0.3rem;
    }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #fff;
        border-left: 4px solid #e8c840;
        padding-left: 0.8rem;
        margin: 2rem 0 1rem 0;
    }

    .pred-box {
        background: linear-gradient(135deg, #1a1a1a, #1f1f2e);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid #444;
        text-align: center;
        margin-top: 1rem;
    }
    .pred-score {
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: 4px;
        color: #ffffff;
    }
    .pred-label {
        color: #888;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    .win-badge {
        display: inline-block;
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-top: 0.8rem;
    }

    div[data-testid="stSlider"] > div { color: #ccc; }
    .stSlider label { color: #ccc !important; }
    h1, h2, h3 { color: #fff !important; }
    .stMarkdown p { color: #ccc; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VERİ
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    dakika_df = pd.DataFrame({
        "TAKIM":      ["Galatasaray"]*12 + ["Fenerbahce"]*12,
        "DURUM":      (["Atılan"]*6 + ["Yenilen"]*6) * 2,
        "DAKIKALAR":  ["0-15","16-30","31-45","46-60","61-75","76-90+"] * 4,
        "GOL SAYISI": [11,11,4,16,14,14,  3,2,1,4,7,5,
                       7,8,13,9,12,16,    7,6,3,7,3,5],
    })

    stats_df = pd.DataFrame({
        "istatistik": [
            "mac_basi_gol","mac_basi_yenilen_gol","mac_basi_buyuk_sans",
            "mac_basi_kacirilam_buyuk_sans","mac_basi_isabetli_sut",
            "mac_basi_toplam_sut","topla_oynama_yuzde","isabetli_pas_yuzde",
            "rakip_yari_sahada_isabetli_yuzde","mac_basi_topu_geri_kazanma",
            "mac_basi_tehlike_engelleme","gol_yemedi","gole_neden_olan_hata",
            "penalti_donusum_yuzde",
        ],
        "aciklama": [
            "Maç Başına Gol","Maç Başına Yenilen Gol","Maç Başına Büyük Şans",
            "Kaçırılan Büyük Şans","Maç Başına İsabetli Şut",
            "Maç Başına Toplam Şut","Top Kontrolü %","İsabetli Pas %",
            "Rakip Sahada Pas %","Maç Başına Top Geri Kazanma",
            "Tehlike Engelleme","Gol Yemeden Bitirilen Maç","Gole Neden Olan Hata",
            "Penaltı Dönüşüm %",
        ],
        "galatasaray": [2.3,0.8,3.6,2.0,5.6,16.3,62.0,87.3,81.6,47.1,19.1,11,4,100.0],
        "fenerbahce":  [2.3,1.0,3.1,1.6,6.2,17.2,59.4,85.8,80.6,46.7,16.2,10,4,75.0],
    })
    return dakika_df, stats_df

dakika_df, stats_df = load_data()

# ─────────────────────────────────────────────
# SKOR TAHMİN MODELİ
# ─────────────────────────────────────────────
def tahmin_skoru(gs_w, fb_w, stats):
    """
    Ağırlıklı feature skorlama modeli.
    Her istatistik normalize edilip fark puanına çevrilir.
    Gol beklentisi = sezon ortalaması + normalize_fark * etki_katsayisi
    """
    weights = {
        "mac_basi_gol":                    0.25,
        "mac_basi_yenilen_gol":           -0.20,  # düşük = iyi
        "mac_basi_buyuk_sans":             0.18,
        "mac_basi_kacirilam_buyuk_sans":  -0.08,
        "mac_basi_isabetli_sut":           0.12,
        "mac_basi_toplam_sut":             0.05,
        "topla_oynama_yuzde":              0.08,
        "isabetli_pas_yuzde":              0.05,
        "rakip_yari_sahada_isabetli_yuzde":0.06,
        "mac_basi_topu_geri_kazanma":      0.06,
        "mac_basi_tehlike_engelleme":      0.05,
        "gol_yemedi":                      0.04,
        "gole_neden_olan_hata":           -0.06,
        "penalti_donusum_yuzde":           0.05,
    }

    gs_score = 0.0
    fb_score = 0.0

    for _, row in stats.iterrows():
        key  = row["istatistik"]
        g_v  = row["galatasaray"]
        f_v  = row["fenerbahce"]
        w    = weights.get(key, 0)
        total = abs(g_v) + abs(f_v)
        if total == 0:
            continue
        norm_g = g_v / total
        norm_f = f_v / total
        gs_score += w * norm_g
        fb_score += w * norm_f

    # Sezon gol ortalamasına dayandır
    gs_base = stats.loc[stats.istatistik=="mac_basi_gol","galatasaray"].values[0]
    fb_base = stats.loc[stats.istatistik=="mac_basi_gol","fenerbahce"].values[0]

    # Model skoru → gol beklentisi (lambda for Poisson)
    gs_lambda = max(0.3, gs_base * (1 + gs_score) * gs_w)
    fb_lambda = max(0.3, fb_base * (1 + fb_score) * fb_w)

    # Poisson dağılımı ile olasılık matrisi
    max_gol = 6
    gs_probs = np.array([np.exp(-gs_lambda) * gs_lambda**k / math.factorial(k) for k in range(max_gol+1)])
    fb_probs = np.array([np.exp(-fb_lambda) * fb_lambda**k / math.factorial(k) for k in range(max_gol+1)])

    # Skor matrisi
    score_matrix = np.outer(gs_probs, fb_probs)

    gs_win = np.sum(np.tril(score_matrix, -1))  # GS > FB
    fb_win = np.sum(np.triu(score_matrix, 1))   # FB > GS
    draw   = np.trace(score_matrix)

    # En olası skor
    idx = np.unravel_index(np.argmax(score_matrix), score_matrix.shape)
    best_gs, best_fb = idx

    return {
        "gs_lambda": round(gs_lambda, 2),
        "fb_lambda": round(fb_lambda, 2),
        "best_gs": best_gs,
        "best_fb": best_fb,
        "gs_win_prob": round(gs_win * 100, 1),
        "fb_win_prob": round(fb_win * 100, 1),
        "draw_prob":   round(draw   * 100, 1),
        "score_matrix": score_matrix,
    }

# ─────────────────────────────────────────────
# BAŞLIK
# ─────────────────────────────────────────────
st.markdown('<p class="hero-title"><span class="gs-color">Galatasaray</span> ⚽ <span class="fb-color">Fenerbahçe</span></p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Süper Lig Derbi Analizi · 2025-26 Sezonu İstatistikleri · Veri: SofaScore</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ÖZET METRİKLER
# ─────────────────────────────────────────────
col1, col2, col3, col4, col5, col6 = st.columns(6)
metrics = [
    ("GS Gol", "69", "#e8c840"),
    ("FB Gol", "68", "#3355cc"),
    ("GS Yenilen", "23", "#e8c840"),
    ("FB Yenilen", "30", "#3355cc"),
    ("GS Temiz Kale", "11", "#e8c840"),
    ("FB Temiz Kale", "10", "#3355cc"),
]
for col, (label, val, color) in zip([col1,col2,col3,col4,col5,col6], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color}">{val}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# SİMÜLASYON SİDEBAR / KONTROLLER
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🎛️ İnteraktif Skor Simülasyonu</div>', unsafe_allow_html=True)

ctrl1, ctrl2 = st.columns(2)
with ctrl1:
    gs_weight = st.slider("🟡 Galatasaray Ev Sahibi Avantajı", 0.7, 1.4, 1.05, 0.05,
                          help="GS iç sahada bu katsayı ile güçlenir")
with ctrl2:
    fb_weight = st.slider("🔵 Fenerbahçe Deplasman Etkisi", 0.7, 1.4, 0.95, 0.05,
                          help="FB deplasman performans katsayısı")

tahmin = tahmin_skoru(gs_weight, fb_weight, stats_df)

# ─────────────────────────────────────────────
# TAHMİN KUTUSU
# ─────────────────────────────────────────────
t1, t2, t3 = st.columns([1,2,1])
with t2:
    winner = "Galatasaray 🏆" if tahmin["gs_win_prob"] > tahmin["fb_win_prob"] else \
             ("Fenerbahçe 🏆" if tahmin["fb_win_prob"] > tahmin["gs_win_prob"] else "Beraberlik")
    badge_color = "#e8c840" if "Galatasaray" in winner else ("#3355cc" if "Fenerbahçe" in winner else "#666")

    st.markdown(f"""
    <div class="pred-box">
        <div style="color:#888;font-size:0.85rem;text-transform:uppercase;letter-spacing:2px">Tahmin Edilen Skor</div>
        <div class="pred-score">{tahmin['best_gs']} – {tahmin['best_fb']}</div>
        <div style="margin-top:0.5rem;color:#aaa">
            GS xG: <b style="color:#e8c840">{tahmin['gs_lambda']}</b> &nbsp;|&nbsp;
            FB xG: <b style="color:#6699ff">{tahmin['fb_lambda']}</b>
        </div>
        <span class="win-badge" style="background:{badge_color}22;border:1px solid {badge_color};color:{badge_color}">
            {winner}
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# Olasılık barları
prob_col1, prob_col2, prob_col3 = st.columns(3)
for col, label, prob, color in [
    (prob_col1, "🟡 GS Kazanır", tahmin["gs_win_prob"], "#e8c840"),
    (prob_col2, "🤝 Beraberlik", tahmin["draw_prob"], "#888888"),
    (prob_col3, "🔵 FB Kazanır", tahmin["fb_win_prob"], "#3355cc"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{color}">%{prob}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# SKOR OLASILIK MATRİSİ
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🎲 Skor Olasılık Matrisi</div>', unsafe_allow_html=True)

matrix = tahmin["score_matrix"][:6, :6] * 100
fig_matrix = go.Figure(go.Heatmap(
    z=matrix,
    x=[f"FB {i}" for i in range(6)],
    y=[f"GS {i}" for i in range(6)],
    colorscale=[[0,"#111"],[0.5,"#333"],[1,"#e8c840"]],
    text=[[f"{matrix[i][j]:.1f}%" for j in range(6)] for i in range(6)],
    texttemplate="%{text}",
    textfont={"size": 11},
    hoverongaps=False,
    showscale=True,
))
fig_matrix.update_layout(
    paper_bgcolor="#0e0e0e",
    plot_bgcolor="#0e0e0e",
    font=dict(color="#ccc", family="Inter"),
    height=380,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(side="top", title="Fenerbahçe Golü"),
    yaxis=dict(title="Galatasaray Golü", autorange="reversed"),
)
st.plotly_chart(fig_matrix, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# GOL DAKİKASI HEATMAP
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">⏱️ Gol Dakikası Dağılımı – Kırılma Anları</div>', unsafe_allow_html=True)

periods = ["0-15","16-30","31-45","46-60","61-75","76-90+"]

gs_atilan  = dakika_df[(dakika_df.TAKIM=="Galatasaray") & (dakika_df.DURUM=="Atılan")]["GOL SAYISI"].values
gs_yenilen = dakika_df[(dakika_df.TAKIM=="Galatasaray") & (dakika_df.DURUM=="Yenilen")]["GOL SAYISI"].values
fb_atilan  = dakika_df[(dakika_df.TAKIM=="Fenerbahce")  & (dakika_df.DURUM=="Atılan")]["GOL SAYISI"].values
fb_yenilen = dakika_df[(dakika_df.TAKIM=="Fenerbahce")  & (dakika_df.DURUM=="Yenilen")]["GOL SAYISI"].values

fig_heat = make_subplots(rows=1, cols=2,
                          horizontal_spacing=0.08)

def heat_trace(atilan, yenilen, name):
    return go.Heatmap(
        z=[atilan, yenilen],
        x=periods,
        y=["Atılan", "Yenilen"],
        colorscale=[[0,"#111"],[0.4,"#1a3a1a"],[1,"#00cc44"]],
        text=[[str(v) for v in atilan],[str(v) for v in yenilen]],
        texttemplate="%{text}",
        textfont={"size":13,"color":"white"},
        showscale=False,
        name=name,
    )

fig_heat.add_trace(heat_trace(gs_atilan, gs_yenilen, "GS"), row=1, col=1)
fig_heat.add_trace(heat_trace(fb_atilan, fb_yenilen, "FB"), row=1, col=2)

fig_heat.update_layout(
    paper_bgcolor="#0e0e0e",
    plot_bgcolor="#0e0e0e",
    font=dict(color="#ccc", family="Inter"),
    height=300,
    margin=dict(l=20, r=20, t=60, b=20),
    annotations=[
        dict(text="Galatasaray", x=0.22, y=1.12, xref="paper", yref="paper",
             showarrow=False, font=dict(color="#e8c840", size=15, family="Inter"), xanchor="center"),
        dict(text="Fenerbahçe",  x=0.78, y=1.12, xref="paper", yref="paper",
             showarrow=False, font=dict(color="#6699ff", size=15, family="Inter"), xanchor="center"),
    ],
)

st.plotly_chart(fig_heat, use_container_width=True)

# Kırılma anı yorumu
with st.expander("📊 Kırılma Anı Analizi"):
    st.markdown("""
    | Periyot | Galatasaray | Fenerbahçe | Yorum |
    |---------|-------------|------------|-------|
    | 0-15 dk | 11 gol | 7 gol | GS erken baskısı belirgin |
    | 16-30 dk | 11 gol | 8 gol | GS üstünlüğü devam eder |
    | 31-45 dk | 4 gol | 13 gol | ⚠️ FB 2. yarı başı öncesi 45. dk patlaması |
    | 46-60 dk | 16 gol | 9 gol | GS devre arasından güçlü çıkar |
    | 61-75 dk | 14 gol | 12 gol | Denge dönemi |
    | 76-90+ dk | 14 gol | 16 gol | ⚠️ FB son 15 dakikada eşitlik/geri dönüş tehlikesi |
    """)
    st.markdown("**Kritik Risk:** GS 46-60. dakika üretkenken, FB 31-45 ve 76-90+'da patlıyor. Derbi için 45. dakika öncesi ve 85+ sonrası kritik.")

st.markdown("---")

# ─────────────────────────────────────────────
# RADAR CHART
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📡 Performans Radar Karşılaştırması</div>', unsafe_allow_html=True)

radar_stats = [
    ("Gol Üretimi",        "mac_basi_gol"),
    ("Savunma Sağlamlığı", "mac_basi_yenilen_gol"),  # ters
    ("Büyük Şans",         "mac_basi_buyuk_sans"),
    ("Şut Etkinliği",      "mac_basi_isabetli_sut"),
    ("Top Kontrolü",       "topla_oynama_yuzde"),
    ("Pas Kalitesi",       "isabetli_pas_yuzde"),
    ("Pressing",           "mac_basi_topu_geri_kazanma"),
    ("Tehlike Engelleme",  "mac_basi_tehlike_engelleme"),
    ("Penaltı Etkinliği",  "penalti_donusum_yuzde"),
]

labels = [r[0] for r in radar_stats]
gs_vals, fb_vals = [], []

for label, key in radar_stats:
    row = stats_df[stats_df.istatistik == key]
    gv = float(row.galatasaray.values[0])
    fv = float(row.fenerbahce.values[0])
    # Savunma istatistiğini ters çevir (düşük = iyi → yüksek puan)
    if key == "mac_basi_yenilen_gol":
        total = gv + fv
        gs_vals.append(round((1 - gv/total) * 100, 1))
        fb_vals.append(round((1 - fv/total) * 100, 1))
    else:
        total = gv + fv
        gs_vals.append(round(gv / total * 100, 1))
        fb_vals.append(round(fv / total * 100, 1))

labels_closed  = labels + [labels[0]]
gs_vals_closed = gs_vals + [gs_vals[0]]
fb_vals_closed = fb_vals + [fb_vals[0]]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=gs_vals_closed, theta=labels_closed, fill="toself",
    name="Galatasaray",
    line=dict(color="#e8c840", width=2),
    fillcolor="rgba(232,200,64,0.18)",
    marker=dict(size=5),
))
fig_radar.add_trace(go.Scatterpolar(
    r=fb_vals_closed, theta=labels_closed, fill="toself",
    name="Fenerbahçe",
    line=dict(color="#3355cc", width=2),
    fillcolor="rgba(51,85,204,0.18)",
    marker=dict(size=5),
))
fig_radar.update_layout(
    polar=dict(
        bgcolor="#111",
        radialaxis=dict(visible=True, range=[0,80], tickfont=dict(color="#666",size=9), gridcolor="#333"),
        angularaxis=dict(tickfont=dict(color="#ccc", size=11), gridcolor="#333", linecolor="#444"),
    ),
    paper_bgcolor="#0e0e0e",
    font=dict(color="#ccc", family="Inter"),
    legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(color="#ccc")),
    height=480,
    margin=dict(l=60, r=60, t=40, b=40),
)
st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# İSTATİSTİK KARŞILAŞTIRMA BARLARI
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📊 Detaylı İstatistik Karşılaştırması</div>', unsafe_allow_html=True)

fig_bar = go.Figure()
bar_labels = stats_df["aciklama"].tolist()
gs_bar = stats_df["galatasaray"].tolist()
fb_bar = stats_df["fenerbahce"].tolist()

fig_bar.add_trace(go.Bar(
    name="Galatasaray", y=bar_labels, x=gs_bar,
    orientation="h",
    marker=dict(color="#e8c840", opacity=0.85),
    text=[str(v) for v in gs_bar],
    textposition="inside",
    textfont=dict(color="#000", size=11, family="Inter"),
))
fig_bar.add_trace(go.Bar(
    name="Fenerbahçe", y=bar_labels, x=[-v for v in fb_bar],
    orientation="h",
    marker=dict(color="#3355cc", opacity=0.85),
    text=[str(v) for v in fb_bar],
    textposition="inside",
    textfont=dict(color="#fff", size=11, family="Inter"),
))
fig_bar.update_layout(
    barmode="overlay",
    paper_bgcolor="#0e0e0e",
    plot_bgcolor="#111",
    font=dict(color="#ccc", family="Inter"),
    legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(color="#ccc")),
    height=520,
    margin=dict(l=220, r=20, t=20, b=20),
    xaxis=dict(showticklabels=False, gridcolor="#222", zerolinecolor="#555"),
    yaxis=dict(gridcolor="#222"),
    bargap=0.25,
)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ─────────────────────────────────────────────
# BONUS: xG TREND (CLAUDE'UN EKLEDİĞİ)
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🔬 Beklenen Gol (xG) Periyot Dağılımı <span style="font-size:0.7rem;color:#888">[Bonus Analiz]</span></div>', unsafe_allow_html=True)

total_gs = gs_atilan.sum()
total_fb = fb_atilan.sum()
# periods listesine karşılık gelen xG değerleri (tüm 6 periyot için)
gs_xg_period = np.array([(v / total_gs) * tahmin["gs_lambda"] for v in gs_atilan])
fb_xg_period = np.array([(v / total_fb) * tahmin["fb_lambda"] for v in fb_atilan])

fig_xg = go.Figure()
fig_xg.add_trace(go.Scatter(
    x=periods, y=gs_xg_period,
    mode="lines+markers+text",
    name="GS xG/Periyot",
    line=dict(color="#e8c840", width=2.5, shape="spline"),
    marker=dict(size=8, color="#e8c840"),
    text=[f"{v:.2f}" for v in gs_xg_period],
    textposition="top center",
    textfont=dict(color="#e8c840", size=10),
    fill="tozeroy",
    fillcolor="rgba(232,200,64,0.08)",
))
fig_xg.add_trace(go.Scatter(
    x=periods, y=fb_xg_period,
    mode="lines+markers+text",
    name="FB xG/Periyot",
    line=dict(color="#3355cc", width=2.5, shape="spline"),
    marker=dict(size=8, color="#3355cc"),
    text=[f"{v:.2f}" for v in fb_xg_period],
    textposition="top center",
    textfont=dict(color="#6699ff", size=10),
    fill="tozeroy",
    fillcolor="rgba(51,85,204,0.08)",
))
fig_xg.update_layout(
    paper_bgcolor="#0e0e0e",
    plot_bgcolor="#111",
    font=dict(color="#ccc", family="Inter"),
    legend=dict(bgcolor="#111", bordercolor="#333", borderwidth=1, font=dict(color="#ccc")),
    height=340,
    margin=dict(l=30, r=30, t=20, b=20),
    xaxis=dict(title="Periyot", gridcolor="#222"),
    yaxis=dict(title="xG", gridcolor="#222"),
)
st.plotly_chart(fig_xg, use_container_width=True)
st.caption("xG/Periyot: Sezon gol dağılımı + Poisson lambda ile hesaplanan beklenen gol miktarı — hangi periyotta tehlike yoğunlaşıyor gösterir.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#555;font-size:0.78rem;margin-top:2rem;padding:1.5rem;border-top:1px solid #222">
    Model: Ağırlıklı Feature Skoru + Poisson Dağılımı &nbsp;·&nbsp; Veri: SofaScore 2025-26 Süper Lig<br>
    <span style="color:#444">Bu analiz istatistiksel bir simülasyondur, kesin sonuç garantisi vermez.</span>
</div>
""", unsafe_allow_html=True)