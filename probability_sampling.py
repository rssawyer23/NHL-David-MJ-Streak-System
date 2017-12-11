import numpy as np

rate_x = 2.0
uncertainty_x = 0.2

rate_y = 1.5
uncertainty_y = 0.2


# Probability function for Poisson random variable X
#   P(X = k | lamb)
def poisson_pf(k, lamb):
    pr = lamb ** k * np.e**(-lamb) / np.math.factorial(k)
    return pr


# Calculating win probability, draw probability, loss probability
#   from two poisson random variables with rates rate_h and rate_a
def calculate_home_win_probability(rate_h, rate_a):
    win_p = 0
    draw_p = 0
    away_p = 0
    for i in range(0, 15):
        for j in range(0, 15):
            score_probability = poisson_pf(i, rate_a) * poisson_pf(j, rate_h)
            if i < j:
                win_p += score_probability
            elif i == j:
                draw_p += score_probability
            else:
                away_p += score_probability
    return win_p, draw_p, away_p

n = 10000
x_samples = np.random.normal(rate_x, uncertainty_x, (n,))
y_samples = np.random.normal(rate_y, uncertainty_y, (n,))

win_p_samples = []
for i in range(n):
    win_p_samples.append(calculate_home_win_probability(x_samples[i], y_samples[i]))

# Expected win probability based off expected value of each rate
print(calculate_home_win_probability(rate_x, rate_y))

# Expected win probability based off sampled rates (symmetrically distributed about their expectation)
print(np.array(win_p_samples).mean(axis=0))

# Standard deviation of win probability categories based off sampled rates
print(np.array(win_p_samples).std(axis=0))
