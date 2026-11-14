"""Arricchisce le previsioni 16-30 nov con i segnali interni del kit (benchmark 2025, picco BF, KPI budget)."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

REF_START = pd.Timestamp("2026-11-02")
REF_END = pd.Timestamp("2026-11-15")
BF_WEEK_START = pd.Timestamp("2026-11-23")
BF_WEEK_END = pd.Timestamp("2026-11-29")
BF_DATE = pd.Timestamp("2026-11-27")
CM_DATE = pd.Timestamp("2026-11-30")

# Pesi intra-settimanali nella settimana 23-29 nov: media esatta = 1.0 ((6 * 0.8 + 2.2) / 7 = 1.0)
BF_DAY_WEIGHT = 2.2
OTHER_DAY_WEIGHT = 0.8


def aligned_week_2025(dates: pd.Series) -> pd.Series:
    """Allinea ogni data 2026 al lunedi della settimana corrispondente nel 2025 (-364 giorni)."""
    return (dates - pd.Timedelta(days=364)).dt.to_period("W-SUN").dt.start_time


def compute_reference_indices(history: pd.DataFrame, bench_it: pd.DataFrame) -> pd.DataFrame:
    """Calcola gli indici di riferimento 2025 ponderati per impression nelle ultime 2 settimane note (2-15 nov)."""
    recent = history[history["data"].between(REF_START, REF_END)].copy()
    recent["week_2025"] = aligned_week_2025(recent["data"])
    recent = recent.merge(
        bench_it[["settimana_dal", "vertical", "indice_cpm", "indice_ctr"]],
        left_on=["week_2025", "vertical"],
        right_on=["settimana_dal", "vertical"],
        how="left",
        validate="many_to_one",
    )
    if recent[["indice_cpm", "indice_ctr"]].isna().any().any():
        raise ValueError("Indici 2025 mancanti nel periodo di riferimento")

    rows = []
    for vertical, group in recent.groupby("vertical", sort=True):
        w = group["impression"].to_numpy(dtype=float)
        rows.append(
            {
                "vertical": vertical,
                "ref_indice_cpm": float(np.average(group["indice_cpm"], weights=w)),
                "ref_indice_ctr": float(np.average(group["indice_ctr"], weights=w)),
            }
        )
    return pd.DataFrame(rows)


def apply_internal_enrichment(
    base_pred: pd.DataFrame, history: pd.DataFrame, bench: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Applica la curva settimanale 2025 del kit e il profilo picco Black Friday a media settimanale invariata."""
    bench_it = bench[(bench["piattaforma"] == "meta") & (bench["paese"] == "IT")].copy()
    ref_df = compute_reference_indices(history, bench_it)

    df = base_pred.copy()
    df["data"] = pd.to_datetime(df["data"])
    df["week_2025"] = aligned_week_2025(df["data"])
    df = df.merge(
        bench_it[["settimana_dal", "vertical", "indice_cpm", "indice_ctr"]],
        left_on=["week_2025", "vertical"],
        right_on=["settimana_dal", "vertical"],
        how="left",
        validate="many_to_one",
    )
    df = df.merge(ref_df, on="vertical", how="left", validate="many_to_one")
    if df[["indice_cpm", "indice_ctr", "ref_indice_cpm", "ref_indice_ctr"]].isna().any().any():
        raise ValueError("Indici 2025 mancanti sul periodo da prevedere")

    # 1) Fattore settimanale puro dal kit (rapporto su riferimento 2-15 nov)
    df["fattore_settimanale_cpm"] = df["indice_cpm"] / df["ref_indice_cpm"]
    df["fattore_settimanale_ctr"] = df["indice_ctr"] / df["ref_indice_ctr"]

    # 2) Concentrazione intra-settimanale sul Black Friday (27/11) a media settimanale invariata
    in_bf_week = df["data"].between(BF_WEEK_START, BF_WEEK_END)
    day_weight = np.where(
        ~in_bf_week,
        1.0,
        np.where(df["data"] == BF_DATE, BF_DAY_WEIGHT, OTHER_DAY_WEIGHT),
    )
    df["fattore_picco_cpm"] = 1.0 + (df["fattore_settimanale_cpm"] - 1.0) * day_weight
    df["fattore_picco_ctr"] = 1.0 + (df["fattore_settimanale_ctr"] - 1.0) * day_weight

    # Verifica conservazione media settimanale su 23-29 nov
    bf_check = df[in_bf_week].groupby("vertical")[["fattore_settimanale_cpm", "fattore_picco_cpm"]].mean()
    np.testing.assert_allclose(bf_check["fattore_settimanale_cpm"], bf_check["fattore_picco_cpm"], rtol=1e-6)

    # Scenari risultanti
    df["cpm_settimanale_kit_eur"] = df["cpm_scelto_eur"] * df["fattore_settimanale_cpm"]
    df["ctr_settimanale_kit_pct"] = np.clip(df["ctr_scelto_pct"] * df["fattore_settimanale_ctr"], 0.0, 100.0)

    df["cpm_arricchito_eur"] = df["cpm_scelto_eur"] * df["fattore_picco_cpm"]
    df["ctr_arricchito_pct"] = np.clip(df["ctr_scelto_pct"] * df["fattore_picco_ctr"], 0.0, 100.0)

    # 3) KPI derivati dal budget ad set (ripartizione uniforme tra gli annunci attivi nell'ad set quel giorno)
    df["n_annunci_attivi_adset"] = df.groupby(["data", "adset_id"])["ad_id"].transform("count")
    df["budget_stimato_annuncio_eur"] = df["budget_giornaliero_adset"] / df["n_annunci_attivi_adset"]

    for suffix, cpm_col, ctr_col in (
        ("base", "cpm_scelto_eur", "ctr_scelto_pct"),
        ("arricchito", "cpm_arricchito_eur", "ctr_arricchito_pct"),
    ):
        imp = (df["budget_stimato_annuncio_eur"] / df[cpm_col]) * 1000.0
        clk = imp * (df[ctr_col] / 100.0)
        cpc = df[cpm_col] / (10.0 * df[ctr_col])
        df[f"impression_stimate_{suffix}"] = imp
        df[f"click_stimati_{suffix}"] = clk
        df[f"cpc_stimato_{suffix}_eur"] = cpc

    if not np.isfinite(df.select_dtypes("number").to_numpy()).all():
        raise ValueError("Valori non finiti nell'arricchimento")
    return df.drop(columns=["settimana_dal"]), ref_df


def summarize_adsets(df: pd.DataFrame) -> pd.DataFrame:
    """Aggrega i KPI stimati per ad set per supportare le decisioni di allocazione budget."""
    grouped = df.groupby(["vertical", "adset_id"], as_index=False).agg(
        righe=("ad_id", "count"),
        annunci_distinti=("ad_id", "nunique"),
        budget_totale_15gg_eur=("budget_stimato_annuncio_eur", "sum"),
        imp_base=("impression_stimate_base", "sum"),
        click_base=("click_stimati_base", "sum"),
        imp_arricchite=("impression_stimate_arricchito", "sum"),
        click_arricchiti=("click_stimati_arricchito", "sum"),
        cpm_arricchito_medio_eur=("cpm_arricchito_eur", "mean"),
        ctr_arricchito_medio_pct=("ctr_arricchito_pct", "mean"),
    )
    grouped["cpc_base_eur"] = grouped["budget_totale_15gg_eur"] / grouped["click_base"]
    grouped["cpc_arricchito_eur"] = grouped["budget_totale_15gg_eur"] / grouped["click_arricchiti"]
    grouped["var_impression_pct"] = 100.0 * (grouped["imp_arricchite"] - grouped["imp_base"]) / grouped["imp_base"]
    grouped["var_click_pct"] = 100.0 * (grouped["click_arricchiti"] - grouped["click_base"]) / grouped["click_base"]
    return grouped.sort_values(["vertical", "cpc_arricchito_eur"]).reset_index(drop=True)


def summarize_levers_history(history: pd.DataFrame) -> list[dict]:
    """Riassume il rendimento storico per settore e leva creativa."""
    agg = history.groupby(["vertical", "leva"], as_index=False).agg(
        righe=("ad_id", "count"),
        annunci=("ad_id", "nunique"),
        click=("click", "sum"),
        impression=("impression", "sum"),
        spesa=("spesa", "sum"),
    )
    agg["ctr_storico_pct"] = 100.0 * agg["click"] / agg["impression"]
    agg["cpm_storico_eur"] = 1000.0 * agg["spesa"] / agg["impression"]
    agg["cpc_storico_eur"] = agg["spesa"] / agg["click"]
    return agg.round(4).to_dict(orient="records")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True, help="Cartella dati/ estratta")
    parser.add_argument("--base-forecast", type=Path, required=True, help="CSV previsioni_2026-11-16_30.csv")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    history = pd.read_csv(args.kit / "storico_giornaliero.csv", parse_dates=["data"])
    bench = pd.read_csv(args.kit / "benchmark_mercato_settimanale_2025.csv", parse_dates=["settimana_dal"])
    base_pred = pd.read_csv(args.base_forecast)

    enriched, ref_df = apply_internal_enrichment(base_pred, history, bench)
    adset_summary = summarize_adsets(enriched)

    daily_summary = (
        enriched.groupby("data", as_index=False)
        .agg(
            n_annunci=("ad_id", "count"),
            ctr_base_mediana=("ctr_scelto_pct", "median"),
            ctr_arricchito_mediana=("ctr_arricchito_pct", "median"),
            cpm_base_mediana=("cpm_scelto_eur", "median"),
            cpm_settimanale_mediana=("cpm_settimanale_kit_eur", "median"),
            cpm_arricchito_mediana=("cpm_arricchito_eur", "median"),
            cpc_arricchito_mediana=("cpc_stimato_arricchito_eur", "median"),
            budget_giornaliero_totale=("budget_stimato_annuncio_eur", "sum"),
            click_stimati_base=("click_stimati_base", "sum"),
            click_stimati_arricchiti=("click_stimati_arricchito", "sum"),
        )
        .sort_values("data")
    )

    args.output.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(
        args.output / "previsioni_arricchite_2026-11-16_30.csv",
        index=False,
        float_format="%.6f",
        date_format="%Y-%m-%d",
    )
    adset_summary.to_csv(
        args.output / "decisioni_adset_budget.csv",
        index=False,
        float_format="%.4f",
    )
    daily_summary.to_csv(
        args.output / "riepilogo_giornaliero.csv",
        index=False,
        float_format="%.4f",
        date_format="%Y-%m-%d",
    )

    report = {
        "fonte": "100% interno al kit organizzatori (nessun trend esterno)",
        "righe_previsione": int(len(enriched)),
        "indici_riferimento_2_15_nov": ref_df.round(4).to_dict(orient="records"),
        "totale_15_giorni": {
            "budget_totale_eur": round(float(enriched["budget_stimato_annuncio_eur"].sum()), 2),
            "impression_stimate_base": int(round(enriched["impression_stimate_base"].sum())),
            "impression_stimate_arricchito": int(round(enriched["impression_stimate_arricchito"].sum())),
            "click_stimati_base": int(round(enriched["click_stimati_base"].sum())),
            "click_stimati_arricchiti": int(round(enriched["click_stimati_arricchito"].sum())),
            "cpc_medio_base_eur": round(
                float(enriched["budget_stimato_annuncio_eur"].sum() / enriched["click_stimati_base"].sum()), 4
            ),
            "cpc_medio_arricchito_eur": round(
                float(enriched["budget_stimato_annuncio_eur"].sum() / enriched["click_stimati_arricchito"].sum()), 4
            ),
        },
        "giorni_chiave": daily_summary[
            daily_summary["data"].isin([pd.Timestamp("2026-11-16"), pd.Timestamp("2026-11-20"), BF_DATE, CM_DATE])
        ]
        .assign(data=lambda x: x["data"].dt.strftime("%Y-%m-%d"))
        .round(4)
        .to_dict(orient="records"),
        "storico_per_leva": summarize_levers_history(history),
    }
    (args.output / "riepilogo_analisi.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Analisi completa generata in {args.output} ({len(enriched)} righe, {len(adset_summary)} ad set)")


if __name__ == "__main__":
    main()
