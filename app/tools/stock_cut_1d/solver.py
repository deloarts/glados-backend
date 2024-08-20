"""
    Stock Cutting Solver
"""

import copy
from itertools import permutations
from time import perf_counter
from typing import Collection
from typing import List
from typing import Tuple

from const import N_MAX
from const import N_MAX_PRECISE
from tools.stock_cut_1d.models.model_job import Job
from tools.stock_cut_1d.models.model_result import Result
from tools.stock_cut_1d.models.model_result import SolverType


def distribute(job: Job) -> Result:
    """Distributes the job to a suiting solver.

    Args:
        job (Job): The incoming job

    Raises:
        OverflowError: Raised when no solver can be used due to a too large job size.

    Returns:
        Result: The result as model.
    """
    time: float = perf_counter()

    lengths: List[List[int]]
    solver_type: SolverType

    if len(job) <= N_MAX_PRECISE:
        lengths = _solve_bruteforce(job)
        solver_type = SolverType.bruteforce
    elif len(job) <= N_MAX:
        lengths = _solve_FFD(job)
        solver_type = SolverType.FFD
    else:
        raise OverflowError("Input too large")

    time_us = int((perf_counter() - time) * 1000 * 1000)

    return Result(job=job, solver_type=solver_type, time_us=time_us, lengths=lengths)


def _solve_bruteforce(job: Job) -> List[List[int]]:
    """Solves the job using brute force approach.
    This method is CPU-bound, O(n!).

    Args:
        job (Job): The job to solve.

    Raises:
        OverflowError: Raised if the input is too large for brute force method.

    Returns:
        List[List[int]]: The resulting list of lists of cuts.
    """
    if len(job) > 12:
        raise OverflowError("Input too large")

    all_orderings = permutations(job.iterate_sizes())
    minimal_trimmings = len(job) * job.max_length
    best_stock: List[List[int]] = []

    for combination in all_orderings:
        stocks, trimmings = _split_combination(
            combination=combination,  # type: ignore
            max_length=job.max_length,
            cut_width=job.cut_width,
        )
        if trimmings < minimal_trimmings:
            best_stock = stocks
            minimal_trimmings = trimmings

    return best_stock


def _split_combination(combination: Tuple[int], max_length: int, cut_width: int) -> Tuple[List[List[int]], int]:
    """Collects sizes until length is reached, then starts another stock

    Args:
        combination (Tuple[int]): The permutation of all sizes.
        max_length (int): The max stock length
        cut_width (int): The cut width

    Returns:
        Tuple: stocks and trimmings (leftovers)
    """
    stocks: List[List[int]] = []
    trimmings = 0

    current_size = 0
    current_stock: List[int] = []
    for size in combination:
        if (current_size + size + cut_width) > max_length:
            # Begin with the next stock
            stocks.append(current_stock)
            trimmings += _get_trimming(max_length, current_stock, cut_width)
            current_size = 0
            current_stock: List[int] = []

        current_size += size + cut_width
        current_stock.append(size)

    # Catch leftover lengths
    if current_stock:
        stocks.append(current_stock)
        trimmings += _get_trimming(max_length, current_stock, cut_width)
    return stocks, trimmings


def _solve_FFD(job: Job) -> List[List[int]]:
    """Solves the problem using ffd.

    Args:
        job (Job): The job to solve.

    Returns:
        List[List[int]]: The resulting list of lists of cuts.
    """

    # TODO: rewrite to use native map instead?
    mutable_sizes = copy.deepcopy(job.target_sizes)
    sizes = sorted(mutable_sizes, reverse=True)

    stocks: List[List[int]] = [[]]

    i_target = 0

    while i_target < len(sizes):
        current_size = sizes[i_target]

        for i, stock in enumerate(stocks):
            # calculate current stock length
            stock_length = sum(stock) + (len(stock) - 1) * job.cut_width
            # step through existing stocks until current size fits
            if (job.max_length - stock_length) > current_size.length:
                # add size
                stock.append(current_size.length)
                break
        else:  # nothing fit, opening next bin
            stocks.append([current_size.length])

        # decrease/get next
        if current_size.quantity <= 1:
            i_target += 1
        else:
            current_size.quantity -= 1

    return stocks


def _get_trimming(max_length: int, lengths: Collection[int], cut_width: int) -> int:
    """Gets the leftover from the stock.

    Raises:
        OverflowError: Raised if the leftover is negative

    Returns:
        int: The leftover value
    """
    sum_lengths = sum(lengths)
    sum_cuts = len(lengths) * cut_width

    trimmings = max_length - (sum_lengths + sum_cuts)

    if trimmings < 0:
        raise OverflowError

    return trimmings
