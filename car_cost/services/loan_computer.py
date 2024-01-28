class LoanComputer:

    def compute_annuity(
        self, capital: int, rate_percentage: float, duration: int
    ) -> float:
        if capital == 0:
            return 0
        rate = rate_percentage / 100
        return rate * capital / (1 - (1 + rate) ** (-duration))

    def compute_debt(
        self, year: int, capital: int, rate_percentage: float, duration: int
    ) -> float:
        if (capital == 0) or (year > duration):
            return 0
        annuity = self.compute_annuity(
            capital=capital, rate_percentage=rate_percentage, duration=duration
        )
        return annuity * (duration - year)
