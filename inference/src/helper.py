from currency_converter import CurrencyConverter
from datetime import date
import re
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import pandas as pd
import numpy as np
from collections import Counter


REFERENCE_DATE = date(2025, 1, 2)  # Set a reference date for currency conversion


def convert_to_usd(row, column_name, reference_date=REFERENCE_DATE):
    c = CurrencyConverter()
    try:
        return c.convert(row[column_name], row["Currency"], 'USD', date=reference_date)
    except Exception as e:
        print(f"Error converting {row[column_name]} {row['Currency']} to USD: {e}")
        return None


def _normalize_skill_text(value):
    text = "" if pd.isna(value) else str(value).lower()
    # Preserves +, #, and . for tech skills
    text = re.sub(r"[^\w\s\+\#\.]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def _make_ngrams(tokens, ngram_range=(1, 2)):
    output = []
    low, high = ngram_range
    token_count = len(tokens)
    for n_size in range(low, high + 1):
        if token_count >= n_size:
            output.extend(
                " ".join(tokens[idx : idx + n_size])
                for idx in range(token_count - n_size + 1)
            )
    return output

def compute_skill_idf_rarity_by_id(df, skill_col="SKILL", weight_col="WEIGHT", ngram_range=(1, 2)):
    tmp = df.copy()
    tmp[skill_col] = tmp[skill_col].map(_normalize_skill_text)
    
    # Filter stopwords AND keep 1-letter tech skills
    tmp["_skill_ngrams"] = tmp[skill_col].map(
        lambda text: _make_ngrams(
            [t for t in text.split() if t not in ENGLISH_STOP_WORDS],
            ngram_range=ngram_range,
        )
    )

    doc_terms = tmp.groupby(level=0)["_skill_ngrams"].apply(
        lambda rows: set(term for row in rows for term in row)
    )

    num_docs = len(doc_terms)
    df_counter = Counter(term for term_set in doc_terms for term in term_set)

    idf_map = {
        term: float(np.log((1 + num_docs) / (1 + doc_freq)) + 1.0)
        for term, doc_freq in df_counter.items()
    }

    # Extract both mean and max to prevent dilution
    tmp["_skill_rarity_row"] = tmp["_skill_ngrams"].map(
        lambda t: float(np.mean([idf_map.get(x, 0.0) for x in t])) if t else np.nan
    )
    tmp["_skill_rarity_max_row"] = tmp["_skill_ngrams"].map(
        lambda t: float(np.max([idf_map.get(x, 0.0) for x in t])) if t else np.nan
    )

    weights = pd.to_numeric(tmp.get(weight_col, pd.Series(0.0, index=tmp.index)), errors="coerce").fillna(0.0)
    tmp["_rarity_x_weight"] = tmp["_skill_rarity_row"] * weights

    rarity_by_id = tmp.groupby(level=0).agg(
        SKILL_RARITY_IDF=("_skill_rarity_row", "mean"),
        SKILL_RARITY_IDF_MAX=("_skill_rarity_max_row", "max"),
        RARITY_WEIGHTED_SUM=("_rarity_x_weight", "sum"),
        WEIGHT_SUM_FOR_RARITY=(weight_col, "sum"),
    )

    rarity_by_id["SKILL_RARITY_IDF_WMEAN"] = rarity_by_id["RARITY_WEIGHTED_SUM"] / rarity_by_id["WEIGHT_SUM_FOR_RARITY"].replace(0.0, np.nan)
    
    return rarity_by_id[["SKILL_RARITY_IDF", "SKILL_RARITY_IDF_MAX", "SKILL_RARITY_IDF_WMEAN"]]
