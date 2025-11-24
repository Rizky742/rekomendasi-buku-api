import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

# ============================
# LOAD DATA
# ============================

peminjaman = pd.read_csv("./data/trx.csv")
member = pd.read_csv("./data/member prodi.csv")
koleksi = pd.read_csv("./data/koleksi yang dipinjam.csv")

# Join dataset
df = member.merge(peminjaman, on="member_id", how="left")
df = df.merge(koleksi, on="Collection_id", how="left")

# Gabungan text untuk TF-IDF
df["combined"] = df["Title"].fillna("") + " " + df["Subject"].fillna("")

# ============================
# TF–IDF MODEL
# ============================

tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["combined"])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Map judul → index matrix
idx_map = {t: i for i, t in enumerate(df["Title"])}

# ============================
# FUNGSI REKOMENDASI
# ============================

def rekomendasi_buku_member(member_id, top_n=10, w_tfidf=0.3, w_prodi=0.5, w_cf=0.2):
    if member_id not in df["member_id"].values:
        return None, "❌ member_id tidak ditemukan"

    data_member = df[df["member_id"] == member_id].iloc[0]
    prodi_id = data_member["ProgramStudi_id"]

    # Buku yang sudah dipinjam user
    buku_user = df[df["member_id"] == member_id]["Title"].dropna().unique().tolist()

    df_titles = df[["Title", "Subject"]].drop_duplicates().reset_index(drop=True)
    df_titles["score_tfidf"] = 0.0

    # ============================
    # 1. TF-IDF SCORE
    # ============================
    if len(buku_user) > 0:
        idx_user_books = [idx_map[b] for b in buku_user if b in idx_map]

        if len(idx_user_books) > 0:
            sim_scores = cosine_sim[idx_user_books].mean(axis=0)
            df_titles["score_tfidf"] = sim_scores[:len(df_titles)]

    # ============================
    # 2. SKOR PRODI (POPULAR DI PRODI SAMA)
    # ============================

    df_prodi = df[df["ProgramStudi_id"] == prodi_id]
    # popular_prodi = (
    #     df_prodi["Title"]
    #     .value_counts()
    #     .reset_index()
    #     .rename(columns={"index": "Title", "Title": "JumlahDipinjam"})
    # )
    popular_prodi = (
        df_prodi["Title"]
        .value_counts()
        .reset_index()
    )
    popular_prodi.columns = ["Title", "JumlahDipinjam"]

    df_titles = df_titles.merge(popular_prodi, on="Title", how="left").fillna({"JumlahDipinjam": 0})

    max_pop = df_titles["JumlahDipinjam"].max()
    df_titles["score_prodi"] = df_titles["JumlahDipinjam"] / max_pop if max_pop > 0 else 0

    # ============================
    # 3. COLLABORATIVE FILTERING (SIMPLE)
    # ============================

    user_activity = df["member_id"].value_counts()
    df["weight"] = df["member_id"].map(user_activity) / user_activity.max()

    df_cf = df.groupby("Title")["weight"].mean().reset_index()
    df_cf.rename(columns={"weight": "score_cf"}, inplace=True)

    df_titles = df_titles.merge(df_cf, on="Title", how="left").fillna({"score_cf": 0})

    # ============================
    # 4. FINAL SCORE
    # ============================

    df_titles["final_score"] = (
        w_tfidf * df_titles["score_tfidf"]
        + w_prodi * df_titles["score_prodi"]
        + w_cf * df_titles["score_cf"]
    )

    # Hapus buku yang sudah dipinjam user
    hasil = df_titles[~df_titles["Title"].isin(buku_user)]

    hasil = hasil.sort_values("final_score", ascending=False).head(top_n)

    return hasil, "OK"
