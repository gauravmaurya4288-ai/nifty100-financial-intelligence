"""
Portfolio API.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def portfolio():
    """
    Placeholder endpoint.
    """

    return {
        "message": "Portfolio endpoint coming in Day 40"
    }