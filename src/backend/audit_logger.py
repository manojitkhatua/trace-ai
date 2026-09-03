from pathlib import Path
import json
from datetime import datetime, timezone


class AuditLogger:
    def __init__(self, path=None):
        root = Path(__file__).resolve().parents[2]
        self.path = Path(
            path or root / "data" / "audit_log.jsonl"
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, transaction, result):
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "transaction": transaction,
            "fraud_probability": result.get("fraud_probability"),
            "anomaly_score": result.get("anomaly_score"),
            "entity_risk": result.get("entity_risk"),
            "risk_score": result.get("risk_score"),
            "risk_level": result.get("risk_level"),
            "decision": result.get("decision"),
            "reasons": result.get("reasons", []),
        }

        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")

        return record