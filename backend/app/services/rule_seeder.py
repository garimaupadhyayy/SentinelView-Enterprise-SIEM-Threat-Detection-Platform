from sqlalchemy.orm import Session

from app.models.rule import DetectionRule
from app.rules.builtin_rules import BUILTIN_RULES


def seed_builtin_rules(db: Session) -> None:
    """Idempotent: only inserts rules that don't already exist by name.
    Never overwrites a rule a user has since edited (e.g. disabled or
    retuned thresholds on), so re-running this on every startup is safe."""
    existing_names = {r.name for r in db.query(DetectionRule.name).all()}
    for rule_def in BUILTIN_RULES:
        if rule_def["name"] in existing_names:
            continue
        db.add(DetectionRule(**rule_def))
    db.commit()
