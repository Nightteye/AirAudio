class ExponentialSmoother:
    def __init__(self, alpha: float = 0.3):
        """
        alpha: 0 < alpha <= 1
        Lower = smoother, higher = more responsive
        """
        self.alpha = alpha
        self.value = None

    def update(self, new_value: float) -> float:
        if self.value is None:
            self.value = new_value
        else:
            self.value = (
                self.alpha * new_value +
                (1 - self.alpha) * self.value
            )
        return self.value


def rate_limit(new: float, old: float, max_step: float) -> float:
    """
    Prevents sudden jumps.
    """
    delta = new - old
    if abs(delta) > max_step:
        return old + max_step * (1 if delta > 0 else -1)
    return new
