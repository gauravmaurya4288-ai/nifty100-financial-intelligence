"""
Stock Screener API.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_screener():
    """
    Placeholder endpoint.
    """
    return {
        "message": "Screener endpoint coming in Day 40"
    }