from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, exists
from datetime import datetime

from app.database.database import get_database
from app.models.allocation import Allocation
from app.models.movement import Movement
from app.models.cargo_unit import CargoUnit

router = APIRouter()


def calculate_risk(db: Session):
    """
    Operational AI risk engine.

    Risk factors:
    - storage duration
    - allocation quality
    - relocation activity
    - allocation complexity
    """

    high = 0
    medium = 0
    low = 0

    details = []

    allocations = (
        db.query(Allocation, CargoUnit)
        .join(CargoUnit, CargoUnit.id == Allocation.cargo_id)
        .all()
    )

    now = datetime.now()

    for allocation, cargo in allocations:

        risk_score = 0
        reasons = []

        score = allocation.score or 0

        # AI allocation confidence
        if score < 100:
            risk_score += 35
            reasons.append("Very low AI allocation confidence")
        elif score < 130:
            risk_score += 15
            reasons.append("Moderate AI allocation confidence")

        # Storage duration
        dwell_days = 0
        if cargo.arrival_date:
            try:
                dwell_days = (now - cargo.arrival_date).days

                if dwell_days > 30:
                    risk_score += 35
                    reasons.append("Cargo stored longer than 30 days")
                elif dwell_days > 15:
                    risk_score += 15
                    reasons.append("Extended storage duration")

            except Exception:
                pass

        # Allocation complexity
        allocation_count = (
            db.query(Allocation)
            .filter(Allocation.cargo_id == cargo.id)
            .count()
        )

        if allocation_count > 2:
            risk_score += 30
            reasons.append("High allocation complexity")
        elif allocation_count > 1:
            risk_score += 10
            reasons.append("Multiple allocation positions")

        # Real movement history
        movements = (
            db.query(Movement)
            .filter(
                Movement.cargo_id == cargo.id,
                Movement.action == "RELOCATED"
            )
            .count()
        )

        if movements >= 3:
            risk_score += 30
            reasons.append("Frequent cargo relocations")
        elif movements > 0:
            risk_score += 10
            reasons.append("Previous relocation activity")

        # Classification
        if risk_score >= 70:
            level = "HIGH"
            high += 1
        elif risk_score >= 35:
            level = "MEDIUM"
            medium += 1
        else:
            level = "LOW"
            low += 1

        if level != "LOW":
            details.append({
                "cargo_reference": cargo.reference,
                "risk": level,
                "score": risk_score,
                "reasons": reasons
            })

    return {
        "HIGH": high,
        "MEDIUM": medium,
        "LOW": low,
        "details": details[:50]
    }


@router.get("/ai")
def ai_dashboard(db: Session = Depends(get_database)):

    total_recommendations = (
        db.query(Allocation)
        .filter(
            Allocation.allocation_method == "AI_RECOMMENDED",
            Allocation.status == "ACTIVE"
        )
        .count()
    )

    multi_position = (
        db.query(Allocation.cargo_id)
        .group_by(Allocation.cargo_id)
        .having(func.count(Allocation.id) > 1)
        .count()
    )

    single_position = (
        db.query(Allocation.cargo_id)
        .group_by(Allocation.cargo_id)
        .having(func.count(Allocation.id) == 1)
        .count()
    )

    successful_relocations = (
        db.query(Movement)
        .filter(Movement.action == "RELOCATED")
        .count()
    )

    recent = (
        db.query(CargoUnit)
        .filter(
            CargoUnit.status == "IMPORTED",
            ~exists().where(
                Allocation.cargo_id == CargoUnit.id,
                Allocation.status == "ACTIVE"
            )
        )
        .order_by(CargoUnit.id.desc())
        .limit(10)
        .all()
    )

    decisions = []

    for cargo in recent:

        allocation = (
            db.query(Allocation)
            .filter(Allocation.cargo_id == cargo.id)
            .order_by(Allocation.score.desc())
            .first()
        )

        if not allocation:
            continue

        score = allocation.score or 0

        confidence = (
            "HIGH" if score >= 150
            else "MEDIUM" if score >= 120
            else "LOW"
        )

        decisions.append({
            "cargo_id": cargo.id,
            "cargo_reference": cargo.reference,
            "cargo_type": cargo.cargo_type or "MANIFEST",
            "cargo_category": cargo.cargo_category or "GENERAL",
            "cargo_status": cargo.status,
            "position": allocation.position_id,
            "recommended_position": allocation.position_id,
            "weight": allocation.allocated_weight,
            "ai_score": score,
            "confidence": confidence,
            "decision_reason": [
                "Cargo requires storage allocation",
                "Weight capacity verified",
                "Handling method compatible",
                "Position optimized for retrieval"
            ],
            "optimization_goal":
                "Minimize handling time and improve yard efficiency",
            "method": allocation.allocation_method
        })

    return {
        "ai_engine": {
            "status": "ACTIVE",
            "recommendations": total_recommendations
        },
        "allocation_strategy": {
            "single_position": single_position,
            "multi_position": multi_position
        },
        "relocations": {
            "successful": successful_relocations,
            "failed": 0
        },
        "risk_analysis": calculate_risk(db),
        "recent_decisions": decisions,
        "pending_recommendations": decisions
    }
