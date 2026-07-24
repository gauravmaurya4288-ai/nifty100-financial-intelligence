"""
Sector API.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def sectors():
    """
    Placeholder endpoint.
    """

    return {
        "message": "Sector endpoint coming in Day 40"
    }