import numpy as np
import operator

STATS_COLORS = {"red": 0, "green": 0, "black": 0}
STATS_PROB = {i: 0 for i in range(15)}

GREEN_DISTANCE_COUNT = 0
AVG_GREEN_DISTANCE = 0
GREEN_DISTANCES = []

def is_red(n:int) -> bool:
    return n >= 1 and n <= 7

def is_black(n:int) -> bool:
    return n >= 8 and n <= 14

def is_green(n:int) -> bool:
    return n == 0

def update_stats(nums: list[int]):
    global STATS_PROB
    global STATS_COLORS
    global GREEN_DISTANCE_COUNT
    global GREEN_DISTANCES
    global AVG_GREEN_DISTANCE

    STATS_COLORS = {"red": 0, "green": 0, "black": 0}
    STATS_PROB = {i: 0 for i in range(15)}

    GREEN_DISTANCE_COUNT = 0
    AVG_GREEN_DISTANCE = 0
    GREEN_DISTANCES = []

    r,b,g = 0,0,0
    for n in nums:
        if n in range(1, 8):
            r += 1
            GREEN_DISTANCE_COUNT += 1
        elif n in range(8, 15):
            b += 1
            GREEN_DISTANCE_COUNT += 1
        elif n == 0:
            g += 1
            GREEN_DISTANCES.append(GREEN_DISTANCE_COUNT)
            GREEN_DISTANCE_COUNT = 0

        STATS_PROB[n] = nums.count(n) / len(nums)

    STATS_COLORS["red"]  = r / (r+b+g)
    STATS_COLORS["black"] = b / (r+b+g)
    STATS_COLORS["green"] = g / (r+b+g)

    AVG_GREEN_DISTANCE = round(float(sum(GREEN_DISTANCES) / len(GREEN_DISTANCES)),2)


def pretty_print_stats():
    sorted_words = sorted(STATS_PROB.items(), key=operator.itemgetter(1))
    for s, p in sorted_words:
        print(f"{s} -> {round(p*100,4)}%")

    print(
        f"\nR:{round(STATS_COLORS['red']*100, 3)}% \ G:{round(STATS_COLORS['green']*100,3)}% \ B:{round(STATS_COLORS['black']*100,3)}%"
    )
    print(
        f"\nLast green in {GREEN_DISTANCE_COUNT}\n{GREEN_DISTANCES}\nAvg Green distance: {AVG_GREEN_DISTANCE}"
    )
