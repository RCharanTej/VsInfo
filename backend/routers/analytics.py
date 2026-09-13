from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.inspection import Inspection, Defect, InspectionStatus
from schemas.inspection import AnalyticsSummaryResponse
from routers.auth import get_current_user
from routers.telemetry import INSPECTIONS_DB

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns aggregated quality metrics: total inspections, pass rate, 
    defect breakdown by category, and average severity score.
    """
    # Total count
    total_inspections = db.query(Inspection).filter(Inspection.user_id == current_user.id).count()

    if total_inspections == 0:
        return {
            "total_inspections": 0,
            "pass_rate_percentage": 100.0,
            "defect_breakdown": {},
            "average_severity": 0.0,
            "recent_inspections": []
        }

    # Passed count
    passed_count = (
        db.query(Inspection)
        .filter(Inspection.user_id == current_user.id, Inspection.status == InspectionStatus.PASSED)
        .count()
    )
    pass_rate = (passed_count / total_inspections) * 100.0

    # Defect breakdown
    defect_counts = (
        db.query(Defect.defect_type, func.count(Defect.id))
        .join(Inspection, Inspection.id == Defect.inspection_id)
        .filter(Inspection.user_id == current_user.id)
        .group_by(Defect.defect_type)
        .all()
    )
    defect_breakdown = {defect_type: count for defect_type, count in defect_counts}

    # Average severity score
    avg_severity = (
        db.query(func.avg(Inspection.severity_score))
        .filter(Inspection.user_id == current_user.id)
        .scalar()
    ) or 0.0

    # Recent inspections
    recent_inspections = (
        db.query(Inspection)
        .filter(Inspection.user_id == current_user.id)
        .order_by(Inspection.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_inspections": total_inspections,
        "pass_rate_percentage": round(pass_rate, 2),
        "defect_breakdown": defect_breakdown,
        "average_severity": round(float(avg_severity), 2),
        "recent_inspections": recent_inspections
    }


@router.get("/confidence-distribution")
def get_confidence_distribution():
    buckets = {"99-100%": 0, "95-98%": 0, "90-94%": 0, "<90%": 0}
    for inspection in INSPECTIONS_DB:
        confidence = float(inspection.get("confidence") or 0)
        if confidence >= 0.99:
            buckets["99-100%"] += 1
        elif confidence >= 0.95:
            buckets["95-98%"] += 1
        elif confidence >= 0.90:
            buckets["90-94%"] += 1
        else:
            buckets["<90%"] += 1
    return [{"range": label, "count": count} for label, count in buckets.items()]


@router.get("/pass-rate-benchmark")
def get_pass_rate_benchmark():
    history = [
        {"day": "Mon", "passRate": 95.2, "baseline": 94.8},
        {"day": "Tue", "passRate": 94.6, "baseline": 94.8},
        {"day": "Wed", "passRate": 96.1, "baseline": 94.8},
        {"day": "Thu", "passRate": 95.8, "baseline": 94.8},
    ]
    total = len(INSPECTIONS_DB)
    passed = sum(1 for item in INSPECTIONS_DB if item.get("overall_status") == "PASSED")
    live_rate = round((passed / total) * 100, 1) if total else 100.0
    history.append({"day": "Live", "passRate": live_rate, "baseline": 94.8})
    return history
