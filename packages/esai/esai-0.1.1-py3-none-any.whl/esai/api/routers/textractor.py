from typing import List

from fastapi import APIRouter, Body
from .. import application

router = APIRouter()

@router.get("/textract")
def textract(file:str):
    return application.get().pipeline("textractor", (file,))

@router.post("/batchtextract")
def batchtextract(files: List[str] = Body(...)):
    return application.get().pipeline("textractor", (files,))