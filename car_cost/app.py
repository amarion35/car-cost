from ftplib import parse150
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_pydantic as sp

from models.input_form_model import InputFormModel, EngineType


def fixed_annuity_computation(
    capital: int, rate_percentage: float, duration: int
) -> float:
    """
    Compute fixed annuities of a loan

    Args:
        capital (int): Total capital left
        rate_percentage (float): Loan rate (in %)
        duration (int): Duration left in years

    Returns:
        float: annuity
    """
    if capital == 0:
        return 0
    rate = rate_percentage / 100
    return rate * capital / (1 - (1 + rate) ** (-duration))


def debt_fixed_annuity(
    capital: int, rate_percentage: float, duration: int, year: int
) -> float:
    if (capital == 0) or (year > duration):
        return 0
    rate = rate_percentage / 100
    annuity = fixed_annuity_computation(capital, rate_percentage, duration)
    debt = capital
    for _ in range(year):
        debt -= annuity - (debt * rate)
    return debt


def tax(taxable_revenue: int) -> float:
    tarrif = [
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
    total = 0
    for t in tarrif:
        total += max(0, min(t["to"], taxable_revenue) - t["from"]) * (t["rate"] / 100)
    return total


def tax_deduction(
    work_distance: int,
    administrative_power: int,
    taxable_revenue: int,
    engine_type: EngineType,
) -> float:
    tarrif = pd.DataFrame(
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

    if work_distance < 5000:
        d = "d1"
    elif 5000 < work_distance < 20000:
        d = "d2"
    else:
        d = "d3"

    if administrative_power <= 3:
        p = "p1"
    elif administrative_power == 4:
        p = "p2"
    elif administrative_power == 5:
        p = "p3"
    elif administrative_power == 6:
        p = "p4"
    else:
        p = "p5"

    a = tarrif.loc[(tarrif["distance"] == d) & (tarrif["power"] == p)]["a"].iloc[0]
    b = tarrif.loc[(tarrif["distance"] == d) & (tarrif["power"] == p)]["b"].iloc[0]

    # work travel deduction
    taxable_revenue_deduction = a * work_distance + b
    # 20% more deduction for electric vehicules
    if engine_type == "Electrique":
        taxable_revenue_deduction *= 1.2

    new_taxable_revenue = taxable_revenue - taxable_revenue_deduction

    # Minimal tax deduction 10%
    max_taxable_revenue = taxable_revenue * 0.9

    max_tax = tax(max_taxable_revenue)
    new_tax = tax(new_taxable_revenue)
    tax_deduction = max(0, max_tax - new_tax)

    return float(tax_deduction)


def get_costs(data: InputFormModel) -> pd.DataFrame:
    financing = np.zeros((data.settings.n_years))
    financing[0] += (
        data.financing.price
        - data.financing.eco_bonus
        - data.financing.resell
        - data.financing.loan
    )
    financing[
        : min(data.settings.n_years, data.financing.loan_duration)
    ] += fixed_annuity_computation(
        capital=data.financing.loan,
        rate_percentage=data.financing.loan_rate,
        duration=data.financing.loan_duration,
    )
    costs = pd.DataFrame(
        {
            "Année": list(range(1, data.settings.n_years + 1)),
            "Fiscalité": [
                -tax_deduction(
                    data.usage.distance_work,
                    data.car_specs.administrative_power,
                    data.taxes.taxable_revenue,
                    engine_type=data.car_specs.engine_type,
                )
            ] * data.settings.n_years,
            "Financement": financing.tolist(),
            "Assurance": [data.insurance.insurance_cost] * data.settings.n_years,
            "Maintenance": [data.car_specs.maintenance_cost] * data.settings.n_years,
            "Carburant": [
                (data.car_specs.fuel_consumption / 100)
                * data.energy.fuel_cost
                * (data.usage.distance_personal + data.usage.distance_work)
            ] * data.settings.n_years,
        }
    ).set_index("Année")
    st.dataframe(costs, use_container_width=True)
    return costs


def get_car_value(data) -> pd.DataFrame:
    discount_exp_ratio = (
        data.discount.value_at_5_years / data.discount.initial_value
    ) ** (1 / 5)
    car_value = pd.DataFrame(
        {
            "Année": list(range(1, data.settings.n_years + 1)),
            "Valeur à la revente": [
                data.discount.initial_value * (discount_exp_ratio**i)
                for i in range(0, data.settings.n_years)
            ],
        }
    ).set_index("Année")
    return car_value


def get_debts(data: InputFormModel) -> pd.DataFrame:
    debts = []
    for year in range(1, data.settings.n_years + 1):
        debt = debt_fixed_annuity(
            data.financing.loan,
            data.financing.loan_rate,
            data.financing.loan_duration,
            year,
        )
        debts.append(debt)
    depts_values = pd.DataFrame(
        {"Année": list(range(1, data.settings.n_years + 1)), "Dette": debts}
    ).set_index("Année")
    return depts_values


def plot_costs(data: InputFormModel, costs: pd.DataFrame) -> None:
    bar_fig = px.bar(
        costs, title=f"Coût du véhicule par an sur {data.settings.n_years} ans"
    )

    st.plotly_chart(bar_fig, use_container_width=True)


def plot_cum_costs(data: InputFormModel, costs: pd.DataFrame) -> None:
    area_fig = px.area(
        costs.cumsum(),
        title=f"Coût cumulé au fil des années sur {data.settings.n_years} ans",
    )

    st.plotly_chart(area_fig, use_container_width=True)


def plot_depts(data: InputFormModel, depts: pd.DataFrame) -> None:
    area_fig = px.area(
        depts,
        title="Dette restante",
    )

    st.plotly_chart(area_fig, use_container_width=True)


def plot_car_value(data: InputFormModel, car_value: pd.DataFrame) -> None:
    value_fig = px.area(
        car_value,
        title=(
            "Valeur du véhicule à la revente au fil des années sur"
            f" {data.settings.n_years} ans"
        ),
    )
    st.plotly_chart(value_fig, use_container_width=True)


def plot_cum_costs_with_discount(
    data: InputFormModel, costs: pd.DataFrame, car_value: pd.DataFrame
) -> None:
    discount = np.diff(
        car_value["Valeur à la revente"].to_numpy(), prepend=data.financing.price
    )
    costs["Décote"] = -discount
    area_fig = px.area(
        costs.cumsum(),
        title=(
            f"Coût cumulé au fil des années sur {data.settings.n_years} ans avec décote"
        ),
    )

    st.plotly_chart(area_fig, use_container_width=True)


def plot_patrimony(
    data: InputFormModel,
    costs: pd.DataFrame,
    car_value: pd.DataFrame,
    depts: pd.DataFrame,
) -> None:
    patrimony = car_value["Valeur à la revente"]
    patrimony -= costs.sum(1).cumsum()
    patrimony -= depts["Dette"]
    area_fig = px.area(
        patrimony.to_numpy(),
        title=(
            f"Evolution du patrimoine au fil des années sur {data.settings.n_years} ans"
        ),
    )

    st.plotly_chart(area_fig, use_container_width=True)


def app():
    st.write("""
    # Budget voiture
    """)

    data: InputFormModel = sp.pydantic_form(key="input_form", model=InputFormModel)
    if data:
        costs = get_costs(data)

        plot_costs(data, costs)
        plot_cum_costs(data, costs)

        depts = get_debts(data)
        plot_depts(data, depts)

        car_value = get_car_value(data)
        plot_car_value(data, car_value)
        plot_patrimony(data, costs, car_value, depts)


if __name__ == "__main__":
    app()
