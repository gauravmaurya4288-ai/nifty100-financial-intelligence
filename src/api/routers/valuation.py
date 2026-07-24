"""
Valuation API.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def valuation():
    """
    Placeholder endpoint.
    """

    return {
        "message": "Valuation endpoint coming in Day 40"
    }