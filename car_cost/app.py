from car_cost.services import (
    CarCostApp,
    DeductibleCarExpensesComputer,
    LoanComputer,
    TaxComputer,
)
from car_cost.settings import AppSettings


def main() -> None:
    app_settings = AppSettings()  # type: ignore (injected from environment variables)
    tax_computer = TaxComputer(
        deductible_car_expenses_computer=DeductibleCarExpensesComputer()
    )
    loan_computer = LoanComputer()
    CarCostApp(
        tax_computer=tax_computer, loan_computer=loan_computer, settings=app_settings
    ).run()


if __name__ == "__main__":
    main()
