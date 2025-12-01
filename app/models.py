from django.db import models
from dataclasses import dataclass
from typing import Optional

@dataclass
class InsulinCalculation:
    current_glucose: float  # ТУГ
    target_glucose: float   # ЦУГ
    sensitivity_coeff: float  # КЧ
    bread_units: float      # ХЕ
    calculated_dose: Optional[float] = None  # ДБИ
    calculation_time: Optional[str] = None
