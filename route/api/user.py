from fastapi import APIRouter, Depends, Request
from typing import Any, List
from pydantic import BaseModel, Extra

from db import influx

router = APIRouter()