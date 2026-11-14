"""Build a v4 submission candidate without Gemini or a running T3 session."""
import platform
import subprocess
from pathlib import Path

from .analytics import audiences, evidence, load_kit, quality_audit, write_csv
from .contracts import digest, write
from .forecast import backtest_baseline, baseline, from_timestral_ref, seasonal_scenarios, validate_forecast
from .marketing import decisions


def deliver(data_dir, out, timestral_ref=None):
    data = load_kit(data_dir)
    out = Path(out)
    audit = quality_audit(data)
    if audit["history_rows"] != 1879 or audit["future_rows"] != 699 or audit["future_outcomes_present"]:
        raise ValueError("Kit diverso dalla specifica v4: controllare righe ed esiti futuri")
    validation, backtest_rows = backtest_baseline(data["history"])
    write_csv(out / "baseline_backtest.csv", backtest_rows)
    validation["reported_external"] = None
    source = {"method": "weighted_hierarchical_14d_v1", "inference": "executed_locally"}
    if timestral_ref:
        forecast, imported = from_timestral_ref(timestral_ref, data["future"], data["history"])
        write_csv(out / "source_timestral_28m.csv", imported.pop("raw_forecast"))
        source = {"method": forecast[0]["model_version"], "inference": "imported_precomputed_not_rerun", **imported}
        validation["reported_external"] = imported["reported_metrics"]
    else:
        forecast = baseline(data["history"], data["future"], "2026-11-15")
    validate_forecast(forecast, data["future"])
    ev = evidence(data["history"], "2026-11-15")
    audience = audiences(ev)
    if len(audience["adsets"]) != 12:
        raise ValueError("Servono 12 audience, una per ad set")
    # Publish fold-specific evidence as well, so retrospective explanations cannot read later history.
    for cutoff in ("2026-10-18", "2026-11-01"):
        fold_evidence = evidence(data["history"], cutoff)
        write(out / f"audience_evidence_{cutoff}.json", fold_evidence)
        write(out / f"audience_hypotheses_{cutoff}.json", audiences(fold_evidence))
    decision = decisions(data["history"], forecast, data["budgets"])
    scenarios = seasonal_scenarios(data["history"], data["future"], data["market"], "2026-11-15")
    write_csv(out / "forecasts_2026-11-16_30.csv", forecast)
    write_csv(out / "decisions.csv", decision["rows"])
    write_csv(out / "ad_delivery.csv", decision["ad_delivery"])
    write_csv(out / "seasonal_scenarios.csv", scenarios)
    write(out / "persona_adset.json", audience)
    write(out / "audience_evidence_2026-11-15.json", ev)
    write(out / "validation_metrics.json", validation)
    write(out / "data_quality.json", audit)
    write(out / "decisions.json", decision)
    try:
        workspace_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        workspace_commit = None
    code = {p.name: p.read_text() for p in Path(__file__).parent.glob("*.py")}
    manifest = {"schema_version": "1.0", "specification": "BigHack2026_Wevion_Specifica_Operativa_v4.md",
                "cutoff": "2026-11-15", "python": platform.python_version(),
                "workspace_base_commit": workspace_commit, "runtime_source_sha256": digest(code),
                "kit_sha256": digest(data), "forecast_source": source,
                "forecast_rows": len(forecast), "audience_cards": len(audience["adsets"]),
                "decision_rows": len(decision["rows"]), "decision_budget_bound": .2,
                "decision_kind": "conditional_what_if", "persona_simulation_required": False,
                "remaining": ["Confrontare CatBoost e completare la selezione del modello",
                              "Calibrare gli intervalli e validare il ranking delle creatività",
                              "Rivedere le ipotesi di pubblico e le evidenze che le sostengono",
                              "Registrare e verificare il video di 180 secondi"],
                "checks": {"exact_forecast_keys": True, "valid_ctr_cpm": True,
                           "temporal_baseline_backtests": True, "twelve_audiences": True}}
    write(out / "manifest.json", manifest)
    from .viewer import render_viewer
    (out / "viewer.html").write_text(render_viewer(forecast, audience, decision, validation, manifest, audit, data["assets"]), encoding="utf-8")
    report = ["# Wevion · consegna candidata v4", "", f"Metodo: {source['method']}.",
              "699 previsioni CTR/CPM, 12 audience ipotizzate, 180 scenari adset/giorno e viewer.html.",
              "", "Gli output sono calcolati dai dati del kit sintetico; nessun risultato futuro è osservato.",
              "Gli scenari stagionali derivano dal benchmark 2025 del kit, non da campagne esterne.",
              "La selezione importata confronta baseline e Timestral sul primo fold WMAE; CatBoost resta da confrontare.",
              "Le audience sono ipotesi comportamentali a confidenza bassa, con alternative; nessuna demografia è osservata.",
              "I budget sono conservati per campagna/giorno entro ±20%; pacing e quote delivery sono ipotesi dichiarate.",
              "", "## Audience e ragionamento", ""]
    for card in audience["adsets"]:
        report.extend([f"### {card['adset_id']}", card["segmento_ipotizzato"],
                       f"CTR storico {card['segnali_osservati']['ctr_storico_pct']:.3f}%; CPM {card['segnali_osservati']['cpm_storico_eur']:.2f} €.",
                       "Alternativa: " + card["alternative"][0], ""])
    report.extend(["## Da completare prima della consegna finale", *[f"- {r}" for r in manifest["remaining"]]])
    (out / "README.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return manifest
