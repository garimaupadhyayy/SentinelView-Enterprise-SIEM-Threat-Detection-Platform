from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_admin, require_any_role
from app.models.rule import DetectionRule
from app.models.user import User
from app.rules.builtin_rules import BUILTIN_RULES
from app.schemas.rule import RuleCreate, RuleOut, RuleUpdate

router = APIRouter(prefix="/rules", tags=["rules"])

_VALID_RULE_TYPES = {r["rule_type"] for r in BUILTIN_RULES} | {"threshold_generic"}


@router.get("", response_model=list[RuleOut])
def list_rules(db: Session = Depends(get_db), _: User = Depends(require_any_role)):
    return db.query(DetectionRule).order_by(DetectionRule.id).all()


@router.get("/types")
def list_rule_types(_: User = Depends(require_any_role)):
    """Rule types the engine knows how to evaluate -- drives the dropdown
    in the frontend's custom rule builder form."""
    return sorted(_VALID_RULE_TYPES)


@router.post("", response_model=RuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(
    payload: RuleCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)
):
    if payload.rule_type not in _VALID_RULE_TYPES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Unknown rule_type '{payload.rule_type}'. Valid types: {sorted(_VALID_RULE_TYPES)}",
        )
    if db.query(DetectionRule).filter(DetectionRule.name == payload.name).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "A rule with this name already exists")

    rule = DetectionRule(**payload.model_dump(), is_builtin=False)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.patch("/{rule_id}", response_model=RuleOut)
def update_rule(
    rule_id: int,
    payload: RuleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Admins can retune ANY rule's config/severity/enabled state --
    including built-ins -- without touching code. This is what makes the
    rules engine 'extensible': a new detection = a new row, a retuned
    detection = an edit here."""
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found")

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(rule, field, value)

    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rule not found")
    if rule.is_builtin:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Built-in rules can't be deleted -- disable them instead (PATCH enabled=false)",
        )
    db.delete(rule)
    db.commit()
