from fastapi import APIRouter, HTTPException

from app.services.operations_data_service import (
    get_case_by_id,
    get_dashboard_summary,
    get_exception_by_id,
    get_reconciliation_break_by_id,
    get_trade_by_id,
)

router = APIRouter(
    prefix="/operations",
    tags=["Operations Data"],
)


@router.get("/summary")
def dashboard_summary():
    return get_dashboard_summary()


@router.get("/trades/{trade_id}")
def trade_detail(trade_id: str):
    trade = get_trade_by_id(trade_id)

    if not trade:
        raise HTTPException(
            status_code=404,
            detail=f"Trade '{trade_id}' not found.",
        )

    return trade


@router.get("/exceptions/{exception_id}")
def exception_detail(exception_id: str):
    exception = get_exception_by_id(exception_id)

    if not exception:
        raise HTTPException(
            status_code=404,
            detail=f"Exception '{exception_id}' not found.",
        )

    return exception


@router.get("/reconciliation-breaks/{break_id}")
def reconciliation_break_detail(break_id: str):
    reconciliation_break = get_reconciliation_break_by_id(break_id)

    if not reconciliation_break:
        raise HTTPException(
            status_code=404,
            detail=f"Reconciliation break '{break_id}' not found.",
        )

    return reconciliation_break


@router.get("/cases/{case_id}")
def case_detail(case_id: str):
    case = get_case_by_id(case_id)

    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Case '{case_id}' not found.",
        )

    return case