from fastapi import APIRouter

router=APIRouter(prefix="/models", tags=["Model Actions"])

@router.get("/list")
async def list_models():
    return{"available_models": ["Phi-2"]}