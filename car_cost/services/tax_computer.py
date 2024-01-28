import numpy as np

from car_cost.models import EngineType
from car_cost.services.deductible_car_expenses_computer import (
    DeductibleCarExpensesComputer,
)


class TaxComputer:
    """Compute taxes"""

    tax_scale: list[dict[str, float]] = [
        {
            "from": 0,
            "to": 1077,
            "rate": 0,
        },
        {
            "from": 1077,
            "to": 27479,
            "rate": 11,
        },
        {
            "from": 27479,
            "to": 78571,
            "rate": 30,
        },
        {
            "from": 78571,
            "to": 168994,
            "rate": 41,
        },
        {
            "from": 168994,
            "to": np.inf,
            "rate": 45,
        },
    ]

    def __init__(
        self, deductible_car_expenses_computer: DeductibleCarExpensesComputer
    ) -> None:
        self._deductible_car_expenses_computer = deductible_car_expenses_computer

    def compute_tax(
        self,
        taxable_revenue: int,
        work_distance: int,
        administrative_power: int,
        engine_type: EngineType,
    ) -> float:
        net_taxable_revenue = self._deductible_car_expenses_computer.compute_deduction(
            taxable_revenue=taxable_revenue,
            work_distance=work_distance,
            administrative_power=administrative_power,
            engine_type=engine_type,
        )
        total = 0
        for t in self.tax_scale:
            total += max(0, min(t["to"], net_taxable_revenue) - t["from"]) * (
                t["rate"] / 100
            )
        return total
