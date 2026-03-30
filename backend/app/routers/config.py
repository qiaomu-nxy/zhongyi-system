import json
import os

from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter(prefix="/api/v1", tags=["配置"])

_SYMPTOM_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "symptom_config.json")


@router.get("/config/symptoms", summary="12个部位+症状标签配置")
def get_symptom_config():
    path = os.path.normpath(_SYMPTOM_CONFIG_PATH)
    if not os.path.exists(path):
        return {"body_parts": []}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@router.get("/qrcode", summary="生成患者端 H5 二维码")
def get_qrcode(base_url: str = "http://localhost:5173"):
    import qrcode
    import io
    img = qrcode.make(base_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")