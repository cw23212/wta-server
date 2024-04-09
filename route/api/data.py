from fastapi import APIRouter, Depends, Request
from typing import Any, List, Optional

import logging
logger = logging.getLogger("wta."+__name__)

from db import influx
from .model import base, data

router = APIRouter()


@router.get("/")
def collectGet():
    return ""
