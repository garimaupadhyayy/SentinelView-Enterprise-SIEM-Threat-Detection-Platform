from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import require_any_role
from app.models.user import User
from app.services.threat_intel_service import check_ip_reputation

router = APIRouter(prefix="/threat-intel", tags=["threat-intel"])


@router.get("/{ip}")
def get_ip_reputation(ip: str, _: User = Depends(require_any_role)):
    result = check_ip_reputation(ip)
    if result is None:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Threat intel lookup unavailable: no ABUSEIPDB_API_KEY configured, or the lookup failed.",
        )
    return {"ip": ip, **result}
