from fastapi import APIRouter, Query
from embeddings.index.action import Action
from embeddings.index.autoid import AutoId

router = APIRouter()

@router.get("/generate-id")
def generate_id(method: str = Query(default="sequence"), data: str = Query(default=None)):
    try:
        method_value = int(method)
    except ValueError:
        method_value = method
    
    id_generator = AutoId(method=method_value)

    unique_id = id_generator(data)
    
    return {"unique_id": unique_id}