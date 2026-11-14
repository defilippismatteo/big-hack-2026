"""Prepare and print the first T3 writer job; no Google API calls."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from market_mirror.t3_personas import prepare_jobs
from market_mirror.providers import settings
from market_mirror.starter import ROOT
cfg = settings()
out = ROOT / "artifacts/personas_t3"
summary = prepare_jobs(cfg["data_dir"], out)
print((out / "jobs" / (summary["first_probe"] + ".prompt.txt")).read_text())
print("Prompt T3 pronto. Nessuna API generativa invocata.")
