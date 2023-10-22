class LoanComputer:
    def __init__(self, capital: int, rate_percentage: float, duration: int) -> None:
        self._capital = capital
        self._rate_percentage = rate_percentage
        self._duration = duration

    def compute_annuity(self) -> float:
        if self._capital == 0:
            return 0
        rate = self._rate_percentage / 100
        return rate * self._capital / (1 - (1 + rate) ** (-self._duration))

    def compute_debt(self, year: int) -> float:
        if (self._capital == 0) or (year > self._duration):
            return 0
        annuity = self.compute_annuity()
        return annuity * (self._duration - year)
