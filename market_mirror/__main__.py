"""Artifact-oriented commands, usable from T3 Code or an ordinary shell."""
import argparse
import importlib.metadata
import os
from pathlib import Path

from .contracts import read, write
from .feed import build_plan
from .handoff import join_forecast
from .personas import make_cards
from .providers import client, decide, settings
from .signals import aggregate
from .starter import ROOT, build_catalog, build_context, generate_slots

DEFAULT_OUT = ROOT / "artifacts" / "market_mirror"


def prepare(data_dir, out, n, seed):
    if n < 6:
        raise ValueError("Usa almeno 6 slot per settore per coprire tutte le fasce d'età")
    context = build_context(data_dir)
    write(out / "safe_inputs/public_context.json", context)
    write(out / "safe_inputs/persona_slots.json", generate_slots(context, n, seed))
    write(out / "decision_inputs/creative_catalog.json", build_catalog(data_dir))
    return context


def parser():
    p = argparse.ArgumentParser(description="Wevion v4: forecast, pubblici motivati e decisioni; feed come estensione")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Stato locale SDK/configurazione; non stampa segreti né chiama API")
    cmd = sub.add_parser("analyze", help="Decision sugli asset, con registro e cache per singola persona")
    cmd.add_argument("--catalog", type=Path, default=DEFAULT_OUT / "decision_inputs/creative_catalog.json")
    cmd.add_argument("--personas", type=Path, default=ROOT / "artifacts/personas_t3/persona_cards.json")
    cmd.add_argument("--asset-id", nargs="+")
    cmd.add_argument("--out", type=Path, default=ROOT / "artifacts/personas_t3/analyses")
    cmd.add_argument("--live", action="store_true")
    cmd.add_argument("--retry-rejected", action="store_true", help="Riprova solo richieste esplicitamente rifiutate, mai timeout/esiti incerti")
    cmd.add_argument("--seed", type=int)
    cmd = sub.add_parser("analysis-view", help="Mostra le risposte Decision già salvate")
    cmd.add_argument("--run", type=Path, default=ROOT / "artifacts/personas_t3/analyses")
    cmd.add_argument("--personas", type=Path, default=ROOT / "artifacts/personas_t3/persona_cards.json")
    cmd.add_argument("--catalog", type=Path, default=DEFAULT_OUT / "decision_inputs/creative_catalog.json")
    cmd = sub.add_parser("t3-prepare", help="Slot e prompt da delegare a Gemini tramite T3; nessuna API")
    cmd.add_argument("--data-dir", type=Path)
    cmd.add_argument("--out", type=Path, default=ROOT / "artifacts" / "personas_t3")
    cmd.add_argument("--n-per-vertical", type=int, default=24)
    cmd.add_argument("--batch-size", type=int, default=4)
    cmd.add_argument("--seed", type=int)
    cmd = sub.add_parser("t3-import", help="Valida le schede restituite da un subagente T3")
    cmd.add_argument("--job", required=True, type=Path)
    cmd.add_argument("--response", required=True, type=Path)
    cmd.add_argument("--receipt", required=True, type=Path)
    cmd.add_argument("--out", type=Path, default=ROOT / "artifacts/personas_t3/persona_cards.json")
    cmd = sub.add_parser("personas-view", help="Visualizza schede T3 reali e il loro feed")
    cmd.add_argument("--cards", type=Path, default=ROOT / "artifacts/personas_t3/persona_cards.json")
    cmd.add_argument("--plan", type=Path)
    cmd.add_argument("--out", type=Path, default=ROOT / "artifacts/personas_t3/viewer.html")
    cmd = sub.add_parser("deliver", help="Consegna candidata v4: 699 forecast, 12 pubblici, decisioni e viewer")
    cmd.add_argument("--data-dir", type=Path)
    cmd.add_argument("--out", type=Path, default=ROOT / "artifacts" / "wevion_v4")
    cmd.add_argument("--timestral-ref", help="Importa Prima_Analisi dal ref Git locale, senza checkout o inferenza")
    for name in ("prepare", "smoke"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--data-dir", type=Path)
        cmd.add_argument("--out", type=Path, default=DEFAULT_OUT)
        cmd.add_argument("--n-per-vertical", type=int, default=24)
        cmd.add_argument("--seed", type=int)
    cmd = sub.add_parser("personas")
    cmd.add_argument("--inputs", type=Path, default=DEFAULT_OUT / "safe_inputs")
    cmd.add_argument("--out", type=Path, default=DEFAULT_OUT / "personas/persona_cards.json")
    cmd.add_argument("--vertical")
    cmd.add_argument("--limit", type=int)
    cmd.add_argument("--live", action="store_true")
    cmd = sub.add_parser("plan")
    cmd.add_argument("--catalog", type=Path, default=DEFAULT_OUT / "decision_inputs/creative_catalog.json")
    cmd.add_argument("--personas", type=Path, default=DEFAULT_OUT / "personas/persona_cards.json")
    cmd.add_argument("--asset-id", required=True)
    cmd.add_argument("--n", type=int, default=4)
    cmd.add_argument("--seed", type=int)
    cmd.add_argument("--out", type=Path, default=DEFAULT_OUT / "decision_inputs/plan.json")
    cmd = sub.add_parser("decide")
    cmd.add_argument("--plan", type=Path, default=DEFAULT_OUT / "decision_inputs/plan.json")
    cmd.add_argument("--out", type=Path, default=DEFAULT_OUT / "decisions/raw.json")
    cmd.add_argument("--live", action="store_true")
    cmd.add_argument("--preflight", action="store_true", help="Verifica piano e parser senza rete o chiamate API")
    cmd = sub.add_parser("aggregate")
    cmd.add_argument("--plan", type=Path, default=DEFAULT_OUT / "decision_inputs/plan.json")
    cmd.add_argument("--raw", type=Path, default=DEFAULT_OUT / "decisions/raw.json")
    cmd.add_argument("--out", type=Path, default=DEFAULT_OUT / "signals/signals_by_asset.json")
    cmd = sub.add_parser("join", help="Solo Analytics: affianca segnali ai CSV Timestral")
    cmd.add_argument("--forecast", type=Path)
    cmd.add_argument("--targets", type=Path)
    cmd.add_argument("--signals", type=Path, nargs="*", default=[])
    cmd.add_argument("--out", type=Path, default=DEFAULT_OUT / "analytics/forecast_with_signals.json")
    return p


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    try:
        cfg = settings()
        seed = getattr(args, "seed", None)
        seed = seed if seed is not None else cfg["seed"]
        if args.command == "analyze":
            from .decision_runs import analyze
            from contextlib import nullcontext
            with client() if args.live else nullcontext(None) as api:
                result = analyze(read(args.catalog), read(args.personas), args.out, api,
                                 args.asset_id, cfg['decision_model'], seed, args.retry_rejected)
            print(f"Asset completati: {len(result)}; nuove richieste API: {sum(r['api_requests'] for r in result)}; risposte riusate: {sum(r['reused_questions'] for r in result)}")
            print(f"Registro: {args.out / 'ledger.json'}")
        elif args.command == "analysis-view":
            from .decision_view import render_analysis
            dest = args.run / 'results.html'
            dest.write_text(render_analysis(read(args.run / 'summary.json'), read(args.personas), read(args.catalog), read(args.run / 'ledger.json')), encoding='utf-8')
            print(f"Risultati: {dest}")
        elif args.command == "t3-prepare":
            from .t3_personas import prepare_jobs
            summary = prepare_jobs(args.data_dir or Path(cfg['data_dir']), args.out,
                                   args.n_per_vertical, args.batch_size, seed)
            print(f"Preparati {summary['n_slots']} slot e {summary['n_jobs']} job T3. Nessuna API chiamata.")
            print(f"Prompt riutilizzabile: {args.out / 'ORCHESTRATE.md'}")
        elif args.command == "t3-import":
            from .t3_personas import import_response
            result = import_response(read(args.job), read(args.response), read(args.receipt),
                                     read(args.out) if args.out.exists() else None)
            write(args.out, result)
            print(f"Schede validate: {len(result['personas'])} → {args.out}")
        elif args.command == "personas-view":
            from .t3_personas import render_cards
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(render_cards(read(args.cards), read(args.plan) if args.plan else None), encoding='utf-8')
            print(f"Viewer: {args.out}")
        elif args.command == "deliver":
            from .delivery import deliver
            manifest = deliver(args.data_dir or Path(cfg["data_dir"]), args.out, args.timestral_ref)
            print(f"Consegna candidata v4: {manifest['forecast_rows']} forecast, {manifest['audience_cards']} pubblici, {manifest['decision_rows']} scenari.")
            print(f"Metodo: {manifest['forecast_source']['method']}\nViewer: {args.out / 'viewer.html'}")
            print("Nessuna chiamata Google. Restano confronto CatBoost, calibrazione intervalli, revisione audience e video.")
        elif args.command == "doctor":
            try:
                sdk = importlib.metadata.version("google-genai")
            except importlib.metadata.PackageNotFoundError:
                sdk = "non installato (richiesto solo live)"
            print(f"SDK: {sdk}\n.env: {'presente' if (ROOT / '.env').exists() else 'assente'}")
            print(f"API key: {'configurata' if os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY') else 'assente'}")
            print(f"Personas: T3/Antigravity, modello richiesto {cfg['persona_model']} (nessuna API generativa)\nDecisioni: {cfg['decision_model']}, API separata")
            print("Nessuna chiamata API eseguita da doctor. La chiave è richiesta solo per Decision.")
        elif args.command in ("prepare", "smoke"):
            data_dir = args.data_dir or Path(cfg["data_dir"])
            context = prepare(data_dir, args.out, args.n_per_vertical, seed)
            if args.command == "smoke":
                cards = make_cards(context, read(args.out / "safe_inputs/persona_slots.json"))
                write(args.out / "personas/persona_cards.json", cards)
                plan = build_plan(read(args.out / "decision_inputs/creative_catalog.json"), cards,
                                  "NDL-S1", n=4, seed=seed, model=cfg["decision_model"])
                write(args.out / "decision_inputs/plan.json", plan)
                raw = decide(plan)
                write(args.out / "decisions/raw.json", raw)
                write(args.out / "signals/signals_by_asset.json", aggregate(plan, raw))
                print(f"SMOKE OFFLINE: {len(cards['personas'])} schede template; reazioni fixture per 4 persone/1 asset. Nessun modello chiamato.")
            print(f"Artefatti: {args.out}")
        elif args.command == "personas":
            if args.live:
                raise ValueError("La generazione usa subagenti Gemini in T3: esegui t3-prepare e t3-import, senza API generativa")
            context = read(args.inputs / "public_context.json")
            slots = read(args.inputs / "persona_slots.json")
            if args.vertical:
                slots["slots"] = [s for s in slots["slots"] if s["vertical"] == args.vertical]
            if args.limit is not None:
                if args.limit < 1:
                    raise ValueError("--limit deve essere positivo")
                slots["slots"] = slots["slots"][:args.limit]
            if not slots["slots"]:
                raise ValueError("Nessuno slot nel settore richiesto")
            cards = make_cards(context, slots)
            write(args.out, cards)
            print(f"Scritte {len(cards['personas'])} personas: {cards['data_kind']} → {args.out}")
        elif args.command == "plan":
            write(args.out, build_plan(read(args.catalog), read(args.personas), args.asset_id,
                                       args.n, seed, cfg["decision_model"]))
            print(f"Piano: {args.out}; {args.n} domande; nessuna chiamata API")
        elif args.command == "decide":
            plan = read(args.plan)
            if args.live and args.preflight:
                raise ValueError('--live e --preflight sono alternativi')
            if args.preflight:
                from .providers import decision_preflight
                write(args.out, decision_preflight(plan))
                print(f'Preflight offline superato; API calls=0 → {args.out}')
                return
            elif args.live:
                if len(plan["request"]["questions"]) > 4:
                    raise ValueError("Primo probe live limitato a 4 persone/1 asset")
                with client() as api:
                    raw = decide(plan, api)
            else:
                raw = decide(plan)
            # Save the raw response before parsing, including incomplete/blocked responses.
            write(args.out, raw)
            print(f"Risposta {raw['data_kind']}: {args.out}")
        elif args.command == "aggregate":
            write(args.out, aggregate(read(args.plan), read(args.raw)))
            print(f"Segnali non calibrati: {args.out}")
        elif args.command == "join":
            forecast = args.forecast or (Path(cfg["forecast_csv"]) if cfg["forecast_csv"] else None)
            if forecast is None:
                raise ValueError("Specifica --forecast o MM_FORECAST_CSV nel .env")
            targets = args.targets or Path(cfg["data_dir"]) / "da_prevedere.csv"
            write(args.out, join_forecast(forecast, targets, [read(s) for s in args.signals]))
            print(f"Join Analytics: {args.out}")
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        # Do not echo HTTP exceptions: they may contain request headers or credentials.
        p.exit(1, f"Errore: {exc}\n")


if __name__ == "__main__":
    main()
