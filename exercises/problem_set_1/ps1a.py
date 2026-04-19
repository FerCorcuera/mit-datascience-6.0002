###########################
# 6.0002 Problem Set 1a: Space Cows
# Name:
# Collaborators:
# Time:

from ps1_partition import get_partitions
import time

# ================================
# Part A: Transporting Space Cows
# ================================


# Problem 1
def load_cows(filename):
    """
    Read the contents of the given file.  Assumes the file contents contain
    data in the form of comma-separated cow name, weight pairs, and return a
    dictionary containing cow names as keys and corresponding weights as values.

    Parameters:
    filename - the name of the data file as a string

    Returns:
    a dictionary of cow name (string), weight (int) pairs
    """
    with open("ps1_cow_data.txt", "r", encoding="utf-8") as f:
        read_data = f.read()

    clean_data = read_data.split("\n")

    cows = {}

    for value in clean_data:
        cow_info = value.split(",")
        cows[cow_info[0]] = int(cow_info[1])

    return cows


# Problem 2
def greedy_cow_transport(cows, limit=10):
    """
    Uses a greedy heuristic to determine an allocation of cows that attempts to
    minimize the number of spaceship trips needed to transport all the cows. The
    returned allocation of cows may or may not be optimal.
    The greedy heuristic should follow the following method:

    1. As long as the current trip can fit another cow, add the largest cow that will fit
        to the trip
    2. Once the trip is full, begin a new trip to transport the remaining cows

    Does not mutate the given dictionary of cows.

    Parameters:
    cows - a dictionary of name (string), weight (int) pairs
    limit - weight limit of the spaceship (an int)

    Returns:
    A list of lists, with each inner list containing the names of cows
    transported on a particular trip and the overall list containing all the
    trips
    """

    if max(cows.values()) > limit:
        raise ValueError("One cow is heavier than the limit, remove it please!")

    iterable_cows = cows.copy()

    trips = []

    while iterable_cows:
        n_trip = []

        remaining_cows = sorted(iterable_cows, key=iterable_cows.get, reverse=True)

        new_limit = limit

        for cow in remaining_cows:
            if new_limit - cows[cow] >= 0:
                n_trip.append(cow)
                new_limit -= cows[cow]

                iterable_cows.pop(cow)

        if n_trip != []:
            trips.append(n_trip)

    return trips


# Problem 3
def brute_force_cow_transport(cows, limit=10):
    """
    Finds the allocation of cows that minimizes the number of spaceship trips
    via brute force.  The brute force algorithm should follow the following method:

    1. Enumerate all possible ways that the cows can be divided into separate trips
        Use the given get_partitions function in ps1_partition.py to help you!
    2. Select the allocation that minimizes the number of trips without making any trip
        that does not obey the weight limitation

    Does not mutate the given dictionary of cows.

    Parameters:
    cows - a dictionary of name (string), weight (int) pairs
    limit - weight limit of the spaceship (an int)

    Returns:
    A list of lists, with each inner list containing the names of cows
    transported on a particular trip and the overall list containing all the
    trips
    """
    names_of_cows = list(cows.keys())
    total_travels = list(get_partitions(names_of_cows))
    valid_travels = []

    for i, travel in enumerate(total_travels):
        total_trips = len(travel)

        excedeed_limit = False

        for trip in travel:
            weight_trip = sum(cows[cow] for cow in trip)
            if weight_trip > limit:
                excedeed_limit = True
                break

        if not excedeed_limit:
            valid_travels.append((i, total_trips))

    min_travel_index = min(valid_travels, key=lambda x: x[1])

    return total_travels[min_travel_index[0]]


# Pr blem 4
def compare_cow_transport_algorithms():
    """
    Using the data from ps1_cow_data.txt and the specified weight limit, run your
    greedy_cow_transport and brute_force_cow_transport functions here. Use the
    default weight limits of 10 for both greedy_cow_transport and
    brute_force_cow_transport.

    Print out the number of trips returned by each method, and how long each
    method takes to run in seconds.

    Returns:
    Does not return anything.
    """
    cow_data = load_cows("ps1_cow_data.txt")

    greedy_start_time = time.time()
    greedy_result = greedy_cow_transport(cow_data)
    greedy_end_time = time.time()

    brute_strat_time = time.time()
    brute_result = brute_force_cow_transport(cow_data)
    brute_end_time = time.time()

    print("==============================")
    print(
        f"Greedy algorithm took {greedy_end_time - greedy_start_time}",
        "\n With this result:",
        greedy_result,
        f"with {len(greedy_result)} trips",
    )
    print("==============================")
    print(
        f"Brute force algorithm took {brute_end_time - brute_strat_time}",
        "\n With this resutl:",
        brute_result,
        f"with {len(brute_result)} trips",
    )


compare_cow_transport_algorithms()
