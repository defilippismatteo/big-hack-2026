"""Reuse the supplied v1 preparation code, without editing the source pack."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    path = ROOT / "Wevion_Personas_Architettura_v1" / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"mm_starter_{name}", path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


build_context = module("prepare_safe_inputs").build
build_catalog = module("build_creative_catalog").build
generate_slots = module("make_slots").generate
OUTCOMES = module("decision1_requests").OUTCOMES
