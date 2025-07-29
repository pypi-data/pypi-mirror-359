from typing import List

from fastapi import APIRouter, Body
from .. import application

router = APIRouter()

@router.get("/tabular")
def tabular(file: str):
    return application.get().pipeline("tabular", (file,))

@router.post("/batchtabular")
def batchtabular(files: List[str] = Body(...)):
    return application.get().pipeline("tabular", (files,))