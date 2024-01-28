import pandas as pd

from car_cost.models import EngineType


class DeductibleCarExpensesComputer:
    """Compute taxable revenue deduction dur to car expenses"""

    _d1: int = 5000
    _d2: int = 20000
    _p1: int = 3
    _p2: int = 4
    _p3: int = 5
    _p4: int = 6
    _deductible_scale: pd.DataFrame = pd.DataFrame(
        {
            "distance": ["d1"] * 5 + ["d2"] * 5 + ["d3"] * 5,
            "power": ["p1", "p2", "p3", "p4", "p5"] * 3,
            "a": [
                0.529,
                0.606,
                0.636,
                0.665,
                0.697,
                0.316,
                0.340,
                0.357,
                0.374,
                0.394,
                0.370,
                0.407,
                0.427,
                0.447,
                0.470,
            ],
            "b": [0] * 5 + [1065, 1330, 1395, 1457, 1515] + [0] * 5,
        }
    )
    _ev_additional_deduction_rate: float = 1.2
    _minimal_deductible_rate: float = 0.9

    def compute_deduction(
        self,
        taxable_revenue: int,
        work_distance: int,
        administrative_power: int,
        engine_type: EngineType,
    ) -> float:
        if work_distance < self._d1:
            d = "d1"
        elif self._d1 < work_distance < self._d2:
            d = "d2"
        else:
            d = "d3"

        if administrative_power <= self._p1:
            p = "p1"
        elif administrative_power == self._p2:
            p = "p2"
        elif administrative_power == self._p3:
            p = "p3"
        elif administrative_power == self._p4:
            p = "p4"
        else:
            p = "p5"

        a = self._deductible_scale.loc[
            (self._deductible_scale["distance"] == d)
            & (self._deductible_scale["power"] == p)
        ]["a"].iloc[0]
        b = self._deductible_scale.loc[
            (self._deductible_scale["distance"] == d)
            & (self._deductible_scale["power"] == p)
        ]["b"].iloc[0]

        # work travel deduction
        taxable_revenue_deduction = a * work_distance + b
        # 20% more deduction for electric vehicules
        if engine_type == "Electrique":
            taxable_revenue_deduction *= self._ev_additional_deduction_rate

        new_taxable_revenue = taxable_revenue - taxable_revenue_deduction

        # Flat-rate deduction if it decrease taxable revenue
        new_taxable_revenue = min(
            new_taxable_revenue, taxable_revenue * self._minimal_deductible_rate
        )

        return new_taxable_revenue
