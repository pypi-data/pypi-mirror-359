import warnings
from collections.abc import Callable
from collections.abc import Iterable
from multiprocessing import current_process
from multiprocessing import get_context
from typing import Any

from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm

warnings.filterwarnings(action="ignore", category=TqdmExperimentalWarning)

track = tqdm

CONTEXT = "fork"


def par_track(
    func: Callable,
    *iterables: Iterable,
    initializer: Callable[..., None] | None = None,
    initargs: Iterable[Any] | None = None,
    progress: tqdm | None = None,
    num_cpus: int | float | None = None,
    total: int | None = None,
    no_par: bool = False,
    pass_index: bool = False,
) -> list[Any]:
    """Performs a parallel ordered imap with tqdm progress."""
    total_items = _calculate_total_items(iterables, total)
    results: list[Any] = [None] * total_items

    if no_par or current_process().daemon:
        _execute_sequential(func, iterables, initializer, initargs, results, progress, pass_index)
    else:
        cpu_count = _determine_cpu_count(num_cpus, total_items)
        _execute_parallel(func, iterables, initializer, initargs, results, progress, pass_index, cpu_count)

    if progress is not None:
        progress.close()
    return results


def _calculate_total_items(iterables: tuple[Iterable, ...], total: int | None) -> int:
    """Calculate the total number of items to process."""
    from collections.abc import Sized

    if total is None:
        return min(len(iterable) for iterable in iterables if isinstance(iterable, Sized))
    return int(total)


def _cpu_count() -> int:
    """Get the number of CPUs available."""
    from psutil import cpu_count

    count = cpu_count()
    if count is None:
        return 1
    return count


def _determine_cpu_count(num_cpus: int | float | None, total_items: int) -> int:
    """Determine the optimal number of CPUs to use."""
    if num_cpus is None:
        # Reserve 2 CPUs for system, minimum 1
        optimal_cpus = max(_cpu_count() - 2, 1)
    elif isinstance(num_cpus, float):
        optimal_cpus = int(round(num_cpus * _cpu_count()))
    else:
        optimal_cpus = int(num_cpus)

    return min(optimal_cpus, total_items)


def _create_indexed_iterables(iterables: tuple[Iterable, ...]) -> tuple[Iterable, ...]:
    """Create iterables that include the index as the first argument."""
    # Get the first iterable to enumerate over
    first_iterable = iterables[0]
    remaining_iterables = iterables[1:]

    # Create an enumerated version: (index, first_item), second_item, third_item, ...
    indexed_first = enumerate(first_iterable)

    if remaining_iterables:
        return (indexed_first,) + remaining_iterables
    else:
        return (indexed_first,)


class _IndexedFunctionWrapper:
    """Pickle-able wrapper class for functions that need an index as the first argument."""

    def __init__(self, func: Callable):
        self.func = func

    def __call__(self, indexed_first_arg, *remaining_args):
        index, first_arg = indexed_first_arg
        return self.func(index, first_arg, *remaining_args)


def _wrap_function_with_index(func: Callable) -> Callable:
    """Wrap a function to handle indexed arguments."""
    return _IndexedFunctionWrapper(func)


def _execute_sequential(
    func: Callable,
    iterables: tuple[Iterable, ...],
    initializer: Callable[..., None] | None,
    initargs: Iterable[Any] | None,
    results: list[Any],
    progress: tqdm | None,
    pass_index: bool,
) -> None:
    """Execute a function sequentially without using multiprocessing."""
    if initializer is not None:
        if initargs is not None:
            initializer(*initargs)
        else:
            initializer()

    if pass_index:
        mapped_iterables = _create_indexed_iterables(iterables)
        wrapped_func = _wrap_function_with_index(func)
        iterator = map(wrapped_func, *mapped_iterables)
    else:
        iterator = map(func, *iterables)

    for index, result in enumerate(iterator):
        results[index] = result
        if progress is not None:
            progress.update()


def _execute_parallel(
    func: Callable,
    iterables: tuple[Iterable, ...],
    initializer: Callable[..., None] | None,
    initargs: Iterable[Any] | None,
    results: list[Any],
    progress: tqdm | None,
    pass_index: bool,
    cpu_count: int,
) -> None:
    """Execute a function in parallel using multiprocessing."""
    init_args = initargs if initargs is not None else []

    if pass_index:
        mapped_iterables = _create_indexed_iterables(iterables)
        wrapped_func = _wrap_function_with_index(func)
    else:
        mapped_iterables = iterables
        wrapped_func = func

    with get_context(CONTEXT).Pool(processes=cpu_count, initializer=initializer, initargs=init_args) as pool:
        for index, result in enumerate(pool.imap(wrapped_func, *mapped_iterables, chunksize=1)):
            results[index] = result
            if progress is not None:
                progress.update()
        pool.close()
        pool.join()
