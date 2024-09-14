from fastapi import APIRouter, HTTPException
from classes.GoogleMaps import Maps

router = APIRouter(prefix="/geolocation", tags=["Geolocation"])
# Geolocation Autocomplete
@router.get("/autocomplete")
async def geolocation_autocomplete(input: str):
    # Call Google Maps Places API for autocomplete
    try:
        return Maps().autocomplete(input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
