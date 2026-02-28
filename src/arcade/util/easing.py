import math

# easings found here are ported from:
# https://easings.net/#

def ease_in_out_cubic(x: float) -> float:
    if x < 0.5:
        return 4 * x * x * x
    else:
        return 1 - math.pow(-2 * x + 2, 3) / 2