"""
Peer Comparison API.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def peers():
    """
    Placeholder endpoint.
    """

    return {
        "message": "Peer endpoint coming in Day 40"
    }