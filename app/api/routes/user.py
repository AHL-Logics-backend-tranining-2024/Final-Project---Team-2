from fastapi import APIRouter

router = APIRouter()

# make sure to remove this function
@router.get("/example")
def example():
    return {"message": "this is an example"}
