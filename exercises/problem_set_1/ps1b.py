###########################
# 6.0002 Problem Set 1b: Space Change
# Name:
# Collaborators:
# Time:
# Author: charz, cdenise

# ================================
# Part B: Golden Eggs
# ================================


# Problem 1
def dp_make_weight(egg_weights, target_weight, memo={}):
    """
    Find number of eggs to bring back, using the smallest number of eggs. Assumes there is
    an infinite supply of eggs of each weight, and there is always a egg of value 1.

    Parameters:
    egg_weights - tuple of integers, available egg weights sorted from smallest to largest value (1 = d1 < d2 < ... < dk)
    target_weight - int, amount of weight we want to find eggs to fit
    memo - dictionary, OPTIONAL parameter for memoization (you may not need to use this parameter depending on your implementation)

    Returns: int, smallest number of eggs needed to make target weight
    """

    if target_weight in memo:
        return memo[target_weight]

    elif target_weight == 0:
        return 0

    elif target_weight in egg_weights:
        return 1

    else:
        valid_eggs = [egg for egg in egg_weights if egg <= target_weight]
        actual_min = (
            dp_make_weight(egg_weights, target_weight - valid_eggs[0], memo) + 1
        )

        for i in range(1, len(valid_eggs)):
            new_min = (
                dp_make_weight(egg_weights, target_weight - valid_eggs[i], memo) + 1
            )
            if new_min < actual_min:
                actual_min = new_min

        memo[target_weight] = actual_min

        return actual_min


# EXAMPLE TESTING CODE, feel free to add more if you'd like
if __name__ == "__main__":
    egg_weights = (1, 5, 10, 25)
    n = 99
    print("Egg weights = (1, 5, 10, 25)")
    print("n = 99")
    print("Expected ouput: 9 (3 * 25 + 2 * 10 + 4 * 1 = 99)")
    print("Actual output:", dp_make_weight(egg_weights, n))
    print()
