from fastapi import APIRouter

router= APIRouter(prefix="/health", tags=["System Health"])

@router.get("/")
async def check_health():
    return{"status":"healthy", "database_connected": False}
