"""
Documents API.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def documents():
    """
    Placeholder endpoint.
    """

    return {
        "message": "Documents endpoint coming in Day 40"
    }