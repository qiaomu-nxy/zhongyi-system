from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import visit as visit_crud
from app.dependencies import DbSession, get_current_doctor
from app.models.lab_result import LabResult
from app.models.symptom import SymptomRecord
from app.models.visit import Visit
from app.models.medical_record import MedicalRecord

router = APIRouter(prefix="/api/v1/analysis", tags=["数据分析"])


@router.get("/patients/{patient_id}/symptom-trend", summary="症状趋势折线图")
def symptom_trend(patient_id: int, db: DbSession, _=Depends(get_current_doctor)):
    visits = (
        db.query(Visit)
        .filter(Visit.patient_id == patient_id, Visit.status == "已完成")
        .order_by(Visit.visit_date)
        .all()
    )
    visit_labels = [{"visit_number": v.visit_number, "visit_date": str(v.visit_date)} for v in visits]
    visit_ids = [v.id for v in visits]

    if not visit_ids:
        return {"visits": [], "series": []}

    symptoms = (
        db.query(SymptomRecord)
        .filter(SymptomRecord.visit_id.in_(visit_ids))
        .all()
    )
    symptom_map: dict[str, dict[int, int]] = defaultdict(dict)
    for s in symptoms:
        symptom_map[s.symptom_name][s.visit_id] = s.severity

    series = [
        {
            "symptom": name,
            "data": [symptom_map[name].get(vid, None) for vid in visit_ids],
        }
        for name in symptom_map
    ]
    return {"visits": visit_labels, "series": series}


@router.get("/patients/{patient_id}/radar", summary="症状雷达图（首诊 vs 最近）")
def symptom_radar(patient_id: int, db: DbSession, _=Depends(get_current_doctor)):
    body_parts = ["头部", "面部", "颈部", "肩部", "胸部", "腹部", "腰部", "背部", "上肢", "下肢", "足部", "全身"]

    visits = (
        db.query(Visit)
        .filter(Visit.patient_id == patient_id, Visit.status == "已完成")
        .order_by(Visit.visit_date)
        .all()
    )
    if len(visits) < 2:
        return {"indicators": body_parts, "first_visit": [], "latest_visit": [], "message": "至少需要2次就诊"}

    def avg_severity(visit_id: int) -> list[float]:
        symptoms = db.query(SymptomRecord).filter(SymptomRecord.visit_id == visit_id).all()
        part_scores: dict[str, list[int]] = defaultdict(list)
        for s in symptoms:
            part_scores[s.body_part].append(s.severity)
        return [
            round(sum(part_scores[p]) / len(part_scores[p]), 1) if part_scores[p] else 0
            for p in body_parts
        ]

    return {
        "indicators": body_parts,
        "first_visit": avg_severity(visits[0].id),
        "latest_visit": avg_severity(visits[-1].id),
    }


@router.get("/patients/{patient_id}/timeline", summary="治疗时间轴")
def treatment_timeline(patient_id: int, db: DbSession, _=Depends(get_current_doctor)):
    visits = (
        db.query(Visit)
        .filter(Visit.patient_id == patient_id)
        .order_by(Visit.visit_date)
        .all()
    )
    events = []
    for v in visits:
        record = db.query(MedicalRecord).filter(MedicalRecord.visit_id == v.id).first()
        import json
        events.append({
            "visit_number": v.visit_number,
            "visit_date": str(v.visit_date),
            "status": v.status,
            "diagnosis": record.diagnosis if record else None,
            "treatment_types": json.loads(record.treatment_types) if record and record.treatment_types else [],
        })
    return {"events": events}


@router.get("/patients/{patient_id}/lab-trend", summary="检验指标趋势")
def lab_trend(patient_id: int, db: DbSession, _=Depends(get_current_doctor)):
    results = (
        db.query(LabResult)
        .filter(LabResult.patient_id == patient_id)
        .order_by(LabResult.created_at)
        .all()
    )
    indicator_map: dict[str, list] = defaultdict(list)
    meta: dict[str, dict] = {}
    for r in results:
        indicator_map[r.indicator_name].append({"date": str(r.created_at.date()), "value": r.value, "is_abnormal": r.is_abnormal})
        if r.indicator_name not in meta:
            meta[r.indicator_name] = {"unit": r.unit, "reference_range": r.reference_range}

    return {
        "indicators": [
            {"name": name, **meta[name], "data": indicator_map[name]}
            for name in indicator_map
        ]
    }