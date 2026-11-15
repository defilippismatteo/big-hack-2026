#!/usr/bin/env bash
set -euo pipefail
REPLICA_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$REPLICA_DIR/../.." && pwd)"
cd -- "$PROJECT_DIR"
if [[ ! -x "$REPLICA_DIR/venv/bin/python" ]]; then
  uv venv --python 3.12.13 "$REPLICA_DIR/venv"
fi
uv pip sync --python "$REPLICA_DIR/venv/bin/python" "$REPLICA_DIR/requirements.lock.txt"
if [[ ! -f "$REPLICA_DIR/source/Prima_Analisi/analisi.py" ]]; then
  mkdir -p "$REPLICA_DIR/source"
  git archive 2d8adf033e747e147c401246c07ce656f9f1cfb7 Prima_Analisi Test_Timestral 'TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE ' | tar -x -C "$REPLICA_DIR/source"
fi
hf download mistralai/Timestral-5M config.json model.safetensors LICENSE README.md --revision bdd20cfc15a3fea0e4cb5ccef37f8d3ca7aa335f --local-dir "$REPLICA_DIR/models/timestral-5m" --quiet
hf download mistralai/Timestral-28M config.json model.safetensors LICENSE README.md --revision 49b26409ac87b5935539a5d8ffe7f397b720db47 --local-dir "$REPLICA_DIR/models/timestral-28m" --quiet
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 HF_HUB_OFFLINE=1
export PYTHONPATH="$REPLICA_DIR/source/Test_Timestral"
mkdir -p "$REPLICA_DIR/results" "$REPLICA_DIR/catboost"
"$REPLICA_DIR/venv/bin/python" -m unittest discover -s "$REPLICA_DIR/source/Test_Timestral" -p 'test_*.py' -v
"$REPLICA_DIR/venv/bin/python" "$REPLICA_DIR/source/Prima_Analisi/analisi.py" \
  --kit "$PROJECT_DIR/info fornite dagli organizzatori /dati" \
  --model-5m "$REPLICA_DIR/models/timestral-5m" --model-28m "$REPLICA_DIR/models/timestral-28m" \
  --output "$REPLICA_DIR/results" > "$REPLICA_DIR/results/inference.log" 2>&1
(
  cd -- "$REPLICA_DIR/catboost"
  "$REPLICA_DIR/venv/bin/python" "$REPLICA_DIR/source/TEST INIZIALI FATTI DA CHAT GPT DA VERIFICARE /Wevion_Validation_Baseline.py" \
    --data "$PROJECT_DIR/info fornite dagli organizzatori /dati" \
    --output catboost_metrics.json > catboost.log 2>&1
)
"$REPLICA_DIR/venv/bin/python" "$REPLICA_DIR/verify.py" > "$REPLICA_DIR/results/verification.log" 2>&1
echo "Replica e verifiche completate: $REPLICA_DIR/results/verification.json"
