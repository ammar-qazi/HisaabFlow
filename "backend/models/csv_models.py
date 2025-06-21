# New file: backend/models/csv_models.py
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date
from typing import Optional, List

class CSVRow(BaseModel):
    date: date
    amount: Decimal
    description: str
    balance: Optional[Decimal] = None

class BankDetectionResult(BaseModel):
    bank_name: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list)