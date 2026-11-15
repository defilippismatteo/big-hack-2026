"""Prepare and print the first T3 writer job; no Google API calls."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from personas_simulation.runtime.t3_personas import prepare_jobs
from personas_simulation.runtime.providers import settings
from personas_simulation.runtime.starter import ROOT
cfg = settings()
out = ROOT / "data/personas_600"
summary = prepare_jobs(cfg["data_dir"], out)
print((out / "jobs" / (summary["first_probe"] + ".prompt.txt")).read_text())
print("Prompt T3 pronto. Nessuna API generativa invocata.")
