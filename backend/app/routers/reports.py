from io import BytesIO
from datetime import datetime

import pandas as pd

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

from app.database.database import get_database

from app.models.cargo_unit import CargoUnit
from app.models.storage_position import StoragePosition
from app.models.movement import Movement
from app.models.allocation import Allocation


router = APIRouter()


# =========================================================
# HELPERS
# =========================================================

def format_datetime(value):
    if not value:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)


def safe_value(value):
    if value is None:
        return ""
    return str(value)


def get_inventory_rows(db: Session):
    cargo_list = (
        db.query(CargoUnit)
        .order_by(CargoUnit.id.desc())
        .all()
    )

    return [
        {
            "Reference": c.reference,
            "Type": c.cargo_type,
            "Category": c.cargo_category,
            "Weight (kg)": c.weight,
            "Status": c.status,
            "Arrival Date": format_datetime(c.arrival_date),
        }
        for c in cargo_list
    ]


def get_storage_rows(db: Session):
    positions = (
        db.query(StoragePosition)
        .order_by(StoragePosition.id.asc())
        .all()
    )

    rows = []

    for p in positions:
        current_weight = p.current_weight or 0
        max_weight = p.max_weight or 0
        available = max_weight - current_weight

        rows.append({
            "Position": p.position_code,
            "Capacity (kg)": max_weight,
            "Current Weight (kg)": current_weight,
            "Available (kg)": available,
            "Occupied": "Yes" if p.occupied else "No",
        })

    return rows


def get_movement_rows(db: Session):
    movements = (
        db.query(Movement, CargoUnit)
        .outerjoin(CargoUnit, CargoUnit.id == Movement.cargo_id)
        .order_by(Movement.created_at.desc())
        .all()
    )

    rows = []

    for movement, cargo in movements:
        rows.append({
            "Date": format_datetime(movement.created_at),
            "Action": movement.action,
            "Cargo Reference": cargo.reference if cargo else f"Cargo #{movement.cargo_id}",
            "From": movement.from_position or "-",
            "To": movement.to_position or "-",
            "Performed By": movement.performed_by or "SYSTEM",
            "Reason": movement.reason or "-",
        })

    return rows


def get_ai_rows(db: Session):
    allocations = (
        db.query(Allocation, CargoUnit, StoragePosition)
        .outerjoin(CargoUnit, CargoUnit.id == Allocation.cargo_id)
        .outerjoin(StoragePosition, StoragePosition.id == Allocation.position_id)
        .filter(Allocation.allocation_method.ilike("%AI%"))
        .order_by(Allocation.allocated_at.desc())
        .all()
    )

    rows = []

    for allocation, cargo, position in allocations:
        rows.append({
            "Cargo Reference": cargo.reference if cargo else f"Cargo #{allocation.cargo_id}",
            "Position": position.position_code if position else f"Position #{allocation.position_id}",
            "Weight (kg)": allocation.allocated_weight,
            "Score": round(allocation.score, 3) if allocation.score is not None else "",
            "Method": allocation.allocation_method,
            "Status": allocation.status,
            "Reason": allocation.reason or "-",
            "Allocated At": format_datetime(allocation.allocated_at),
        })

    return rows


def get_report_rows(report: str, db: Session):
    report = report.lower()

    if report == "inventory":
        return get_inventory_rows(db)

    if report == "storage":
        return get_storage_rows(db)

    if report == "movements":
        return get_movement_rows(db)

    if report in ["ai", "decision", "decisions"]:
        return get_ai_rows(db)

    raise HTTPException(status_code=404, detail="Unknown report type")


def get_report_title(report: str):
    report = report.lower()

    titles = {
        "inventory": "Inventory Report",
        "storage": "Storage Report",
        "movements": "Movement Report",
        "ai": "Decision Report",
        "decision": "Decision Report",
        "decisions": "Decision Report",
    }

    return titles.get(report, "Report")


def get_pdf_column_widths(report: str):
    report = report.lower()

    if report == "inventory":
        return [42*mm, 28*mm, 30*mm, 24*mm, 24*mm, 34*mm]

    if report == "storage":
        return [32*mm, 28*mm, 32*mm, 30*mm, 20*mm]

    if report == "movements":
        return [28*mm, 22*mm, 34*mm, 20*mm, 20*mm, 26*mm, 76*mm]

    if report in ["ai", "decision", "decisions"]:
        return [34*mm, 24*mm, 22*mm, 16*mm, 28*mm, 20*mm, 56*mm, 28*mm]

    return None


def build_pdf(report: str, rows: list[dict]):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=10 * mm,
        rightMargin=10 * mm,
        topMargin=12 * mm,
        bottomMargin=10 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.black,
        spaceAfter=8
    )

    meta_style = ParagraphStyle(
        "MetaStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.black,
        spaceAfter=10
    )

    cell_style = ParagraphStyle(
        "CellStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.black
    )

    header_cell_style = ParagraphStyle(
        "HeaderCellStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    elements = []

    title = get_report_title(report)

    elements.append(Paragraph("DJENDJEN PORT", title_style))
    elements.append(Paragraph("AI Port Storage Optimization Platform", meta_style))
    elements.append(Paragraph(title, ParagraphStyle(
        "SubTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        textColor=colors.black,
        spaceAfter=4
    )))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
    elements.append(Spacer(1, 4))

    if not rows:
        elements.append(Paragraph("No data available for this report.", styles["Normal"]))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    columns = list(rows[0].keys())

    table_data = [
        [Paragraph(safe_value(col), header_cell_style) for col in columns]
    ]

    for row in rows:
        table_data.append([
            Paragraph(safe_value(row.get(col, "")), cell_style)
            for col in columns
        ])

    col_widths = get_pdf_column_widths(report)

    table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#94a3b8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer


def build_excel(report: str, rows: list[dict]):
    buffer = BytesIO()

    df = pd.DataFrame(rows)

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        sheet_name = get_report_title(report).replace(" ", "_")
        df.to_excel(writer, index=False, sheet_name=sheet_name)

        ws = writer.sheets[sheet_name]

        for column_cells in ws.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter

            for cell in column_cells:
                try:
                    cell_length = len(str(cell.value)) if cell.value is not None else 0
                    if cell_length > max_length:
                        max_length = cell_length
                except Exception:
                    pass

            ws.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 45)

    buffer.seek(0)
    return buffer


# =========================================================
# JSON REPORTS
# =========================================================

@router.get("/inventory")
def inventory_report(db: Session = Depends(get_database)):
    return get_inventory_rows(db)


@router.get("/storage")
def storage_report(db: Session = Depends(get_database)):
    return get_storage_rows(db)


@router.get("/movements")
def movement_report(db: Session = Depends(get_database)):
    return get_movement_rows(db)


@router.get("/ai")
def ai_report(db: Session = Depends(get_database)):
    return get_ai_rows(db)


# =========================================================
# EXPORT EXCEL
# =========================================================

@router.get("/{report}/excel")
def export_excel(
    report: str,
    db: Session = Depends(get_database)
):
    rows = get_report_rows(report, db)
    file_buffer = build_excel(report, rows)

    filename = f"{report}_report.xlsx"

    return StreamingResponse(
        file_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


# =========================================================
# EXPORT PDF
# =========================================================

@router.get("/{report}/pdf")
def export_pdf(
    report: str,
    db: Session = Depends(get_database)
):
    rows = get_report_rows(report, db)
    file_buffer = build_pdf(report, rows)

    filename = f"{report}_report.pdf"

    return StreamingResponse(
        file_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )