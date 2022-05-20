#!/bin/python3

# by Andy Jiang (akej111@gmail.com)
# Riot Games - Game of Life Interview Take Home Problem

import numpy as np
import concurrent.futures

INT_MIN = -9223372036854775808
INT_MAX = 9223372036854775807

NUM_ITERATIONS = 10
THREAD_COUNT = 4

LIFE_VERSION = "#Life 1.06"

def get_next_state_single_thread(alive_cells):
    # add all alive cells to cells we want to check for next state
    check_for_next = alive_cells.copy()
    for cell in alive_cells:
        # add all of current alive cell's surrounding cells to check for next state
        check_for_next.update(get_surrounding_cells(cell))
    return get_alive_cells_for_next_state(check_for_next, alive_cells)

'''
For a larger problem space, we can split up cells_to_check and use a thread pool to 
execute get_alive_cells_for_next_state, then merge the results into a single set

get_alive_cells_for_next_state only reads from the shared data structure, no writing and locking needed
shared resource: alive_cells (the set of all currently alive cells)
'''
def get_next_state_multi_thread(alive_cells, thread_count):
    # add all alive cells to cells we want to check for next state
    check_for_next = alive_cells.copy()
    for cell in alive_cells:
        # add all of current alive cell's surrounding cells to check for next state
        check_for_next.update(get_surrounding_cells(cell))

    next_cells = set()
    cell_lists = split_into_n_lists(list(check_for_next), thread_count)

    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = []
        for cell_list in cell_lists:
            futures.append(executor.submit(get_alive_cells_for_next_state, cell_list, alive_cells))
        for future in concurrent.futures.as_completed(futures):
              next_cells.update(future.result())
    return next_cells

# For each cell to check, see if it will be alive in the  next state
# Returns all cells in input set that will be alive in the next state
def get_alive_cells_for_next_state(cells_to_check, alive_cells):
    next_cells = set()
    for cell in cells_to_check:
        if is_alive_next_state(cell, alive_cells):
            next_cells.add(cell)
    return next_cells

# For a single cell, see if it will be alive next set
# Returns True if alive, False if dead
def is_alive_next_state(cell, alive_cells):
    surrounding = get_surrounding_cells(cell)
    count = 0
    for adj_cell in surrounding:
        if adj_cell in alive_cells:
            count += 1
            if count > 3:
                return False
    if cell in alive_cells:
        if count == 2 or count == 3:
            return True
        else:
            return False
    else:
        return count == 3

# Given a list and a number n
# Split the list elements among n different lists
def split_into_n_lists(input_list, n):
    all_lists = []
    for i in range(0, len(input_list), n):
        all_lists.append(input_list[i:i+n])
    return all_lists

# Given a cell (x,y), return the tuples for all
# the surrounding cells, within the bounds of INT_MIN, INT_MAX
def get_surrounding_cells(cell):
    # assumes input pair is in acceptable range
    # given we checked at program start
    cells = []
    x, y = cell
    # top left
    if x > INT_MIN and y < INT_MAX:
        cells.append((x - 1, y + 1))
    # top middle
    if y < INT_MAX:
        cells.append((x, y + 1))
    # top right
    if x < INT_MAX and y < INT_MAX:
        cells.append((x + 1, y + 1))
    # middle left
    if x > INT_MIN:
        cells.append((x - 1, y))
    # middle right
    if x < INT_MAX:
        cells.append((x + 1, y))
    # bot left
    if x > INT_MIN and y > INT_MIN:
        cells.append((x - 1, y - 1))
    # bot middle
    if y > INT_MIN:
        cells.append((x, y - 1))
    # bot right
    if x < INT_MAX and y > INT_MIN:
        cells.append((x + 1, y - 1))
    return cells

def print_in_life_format(cells):
    print(LIFE_VERSION)
    for cell in cells:
        print(cell[0], cell[1])

if __name__ == '__main__':
    '''
    input
    ------
    <# of coords>
    x1, y1
    x2, y2

    example
    ------
    3
    1, 2
    0, -1
    -1, 3
    '''
    n = int(input().strip())
    cells = set()
    for _ in range(n):
        input_pair = input().strip().split(',')
        x = int(input_pair[0].strip())
        y = int(input_pair[1].strip())
        if x >= INT_MIN and x <= INT_MAX and y >= INT_MIN and y <= INT_MAX:
            cells.add((x,y))
    for _ in range(NUM_ITERATIONS):
        # cells = get_next_state_single_thread(cells)
        cells = get_next_state_multi_thread(cells, THREAD_COUNT)
    print_in_life_format(list(cells))
