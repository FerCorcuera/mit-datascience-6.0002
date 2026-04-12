class Food:
    """
    With this class we will be able to create each food and access to
    its name, value and calories (cost)
    """

    def __init__(self, name, value, calories):
        self.name = name
        self.value = value
        self.calories = calories

    def getValue(self):
        return self.value

    def getCost(self):
        return self.calories

    def density(self):
        return self.getValue() / self.getCost()

    def __str__(self):
        return self.name + ": <" + str(self.value) + ", " + str(self.calories) + ">"


def buildMenu(names, values, calories):
    """With this function we will be able to create our own menu filled with different object of the class food
    names, values calories lists of the same length.
    name a list of strings
    values and calories lists of numbers
    returns list of Foods"""

    menu = []

    for i in range(len(values)):
        menu.append(Food(names[i], values[i], calories[i]))

    return menu


#  key function will be used to sort the items,
# we want to sort them the best to worst for example, keyfunction will just return the value, or the weight, or anything
# with this function we are just iterating


def greedy(items, maxCost, keyFunction):
    """
    With this function we are simulating our greedy algorithm for the knack sack problem,
    We are just finding the best combination by defining the category that we value most, and then
    adding all the food from the most value able in that term until we have no more calories left.

    Assumes items a list, maxCost >= 0,
    keyFunction maps elements of items to numbers
    """

    itemsCopy = sorted(items, key=keyFunction, reverse=True)

    result = []

    totalValue, totalCost = 0.0, 0.0

    for i in range(len(itemsCopy)):
        if (totalCost + itemsCopy[i].getCost()) <= maxCost:
            result.append(itemsCopy[i])

            totalCost += itemsCopy[i].getCost()

            totalValue += itemsCopy[i].getValue()

    return (result, totalValue)


def testGreedy(items, constraint, keyFunction):
    taken, val = greedy(items, constraint, keyFunction)
    print("Total value of items taken =", val)

    for item in taken:
        print("    ", item)


def testGreedys(maxUnits, foods):
    print("Use greedy by value to allocate", maxUnits, "calories")

    testGreedy(foods, maxUnits, Food.getValue)

    print("\nUse greedy by cost to allocate", maxUnits, "calories")

    testGreedy(foods, maxUnits, lambda x: 1 / Food.getCost(x))

    print("\nUse greedy by density to allocate", maxUnits, "calories")

    testGreedy(foods, maxUnits, Food.density)
