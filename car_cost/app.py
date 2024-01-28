import requests
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit_pydantic as sp

from car_cost.services.database import Database
from car_cost.services.deductible_car_expenses_computer import (
    DeductibleCarExpensesComputer,
)
from car_cost.services.loan_computer import LoanComputer
from car_cost.services.tax_computer import TaxComputer

from models.input_form_model import InputFormModel, EngineType
from car_cost.settings import AppSettings

def print_public_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        data = response.json()
        public_ip = data['ip']
        print(f"Public IP: {public_ip}")
    except Exception as e:
        print(f"Error getting public IP: {e}")
        return None

class App:
    _settings: AppSettings

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    def _get_tax_deduction(
        self,
        work_distance: int,
        administrative_power: int,
        taxable_revenue: int,
        engine_type: EngineType,
    ) -> float:
        new_tax_computer = TaxComputer(
            deductible_car_expenses_computer=DeductibleCarExpensesComputer(
                work_distance=work_distance,
                administrative_power=administrative_power,
                engine_type=engine_type,
            )
        )
        new_tax = new_tax_computer.compute_tax(taxable_revenue=taxable_revenue)

        # Compare tax to a no car scenario (10% deduction flat rate)
        max_tax_computer = TaxComputer(
            deductible_car_expenses_computer=DeductibleCarExpensesComputer(
                work_distance=0,
                administrative_power=administrative_power,
                engine_type=engine_type,
            )
        )
        max_tax = max_tax_computer.compute_tax(taxable_revenue=taxable_revenue)

        # Compute the total marginal tax deduction
        tax_deduction = max(0, max_tax - new_tax)

        return float(tax_deduction)

    def _get_costs(self, data: InputFormModel) -> pd.DataFrame:
        loan_computer = LoanComputer(
            capital=data.financing.loan,
            rate_percentage=data.financing.loan_rate,
            duration=data.financing.loan_duration,
        )

        financing = np.zeros((data.settings.n_years))
        financing[0] += (
            data.financing.price
            - data.financing.eco_bonus
            - data.financing.resell
            - data.financing.loan
        )
        financing[
            : min(data.settings.n_years, data.financing.loan_duration)
        ] += loan_computer.compute_annuity()
        costs = pd.DataFrame(
            {
                "Année": list(range(1, data.settings.n_years + 1)),
                "Fiscalité": [
                    -self._get_tax_deduction(
                        data.usage.distance_work,
                        data.car_specs.administrative_power,
                        data.taxes.taxable_revenue,
                        engine_type=data.car_specs.engine_type,
                    )
                ]
                * data.settings.n_years,
                "Financement": financing.tolist(),
                "Assurance": [data.insurance.insurance_cost] * data.settings.n_years,
                "Maintenance": [data.car_specs.maintenance_cost]
                * data.settings.n_years,
                "Carburant": [
                    (data.car_specs.fuel_consumption / 100)
                    * data.energy.fuel_cost
                    * (data.usage.distance_personal + data.usage.distance_work)
                ]
                * data.settings.n_years,
            }
        ).set_index("Année")
        return costs

    def _get_car_value(self, data) -> pd.DataFrame:
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

    def _get_debts(self, data: InputFormModel) -> pd.DataFrame:
        loan_computer = LoanComputer(
            capital=data.financing.loan,
            rate_percentage=data.financing.loan_rate,
            duration=data.financing.loan_duration,
        )
        debts = []
        for year in range(1, data.settings.n_years + 1):
            debt = loan_computer.compute_debt(year=year)
            debts.append(debt)
        depts_values = pd.DataFrame(
            {"Année": list(range(1, data.settings.n_years + 1)), "Dette": debts}
        ).set_index("Année")
        return depts_values

    def _plot_costs(self, data: InputFormModel, costs: pd.DataFrame) -> None:
        bar_fig = px.bar(
            costs, title=f"Coût du véhicule par an sur {data.settings.n_years} ans"
        )

        st.plotly_chart(bar_fig, use_container_width=True)

    def _plot_cum_costs(self, data: InputFormModel, costs: pd.DataFrame) -> None:
        area_fig = px.area(
            costs.cumsum(),
            title=f"Coût cumulé au fil des années sur {data.settings.n_years} ans",
        )

        st.plotly_chart(area_fig, use_container_width=True)

    def _plot_costs_pie(self, data: InputFormModel, costs: pd.DataFrame) -> None:
        pie_data = costs
        pie_data = pie_data.map(lambda x: max(0, x))
        pie_data = pie_data.cumsum().T.reset_index(names="Dépenses")
        area_fig = px.pie(
            pie_data,
            values=data.settings.n_years,
            names="Dépenses",
            title=f"Répartition des coûts cumulés sur {data.settings.n_years} ans",
        )
        st.plotly_chart(area_fig, use_container_width=True)

    def _plot_depts(self, data: InputFormModel, depts: pd.DataFrame) -> None:
        area_fig = px.area(
            depts,
            title="Dette restante",
        )

        st.plotly_chart(area_fig, use_container_width=True)

    def _plot_car_value(self, data: InputFormModel, car_value: pd.DataFrame) -> None:
        value_fig = px.area(
            car_value,
            title=(
                "Valeur du véhicule à la revente au fil des années sur"
                f" {data.settings.n_years} ans"
            ),
        )
        st.plotly_chart(value_fig, use_container_width=True)

    def _plot_patrimony(
        self,
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
                "Evolution du patrimoine au fil des années sur"
                f" {data.settings.n_years} ans"
            ),
        )

        st.plotly_chart(area_fig, use_container_width=True)

    def run(self):
        st.write(
            """
        # Budget voiture
        """
        )

        data = sp.pydantic_form(key="input_form", model=InputFormModel)

        if data:
            costs = self._get_costs(data)
            depts = self._get_debts(data)
            car_value = self._get_car_value(data)

            self._plot_patrimony(data, costs, car_value, depts)

            with st.expander("Détails des coûts"):
                st.dataframe(costs, use_container_width=True)
                self._plot_costs(data, costs)
                self._plot_cum_costs(data, costs)
                self._plot_costs_pie(data, costs)

            with st.expander("Détails des dettes"):
                self._plot_depts(data, depts)

            with st.expander("Détails de la valeur du véhicule"):
                self._plot_car_value(data, car_value)

            Database(self._settings.database_settings).add_query(data)


if __name__ == "__main__":
    print_public_ip()
    app_settings = AppSettings()
    App(settings=app_settings).run()
