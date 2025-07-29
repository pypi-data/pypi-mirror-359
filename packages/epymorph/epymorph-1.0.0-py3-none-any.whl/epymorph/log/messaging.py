"""Displaying epymorph simulation progress in console (or similar outputs)."""
# ruff: noqa: T201

from contextlib import contextmanager
from functools import partial
from math import ceil
from time import perf_counter
from typing import Generator

import humanize
from humanize import naturalsize

from epymorph.attribute import NAME_PLACEHOLDER
from epymorph.event import ADRIOProgress, EventBus, OnStart, OnTick
from epymorph.util import progress, subscriptions

_events = EventBus()


@contextmanager
def sim_messaging(
    *,
    adrio: bool = True,
    live: bool = True,
) -> Generator[None, None, None]:
    """
    Run simulations in this context manager to output (print) progress messages during
    simulation activity.

    Parameters
    ----------
    adrio :
        True to include ADRIO progress updates.
    live :
        True if this is being used in an interactive environment like
        the console or a Jupyter Notebook. When rendering static documents
        (such as with Quarto), the output may look better by setting this to False.

    Examples
    --------
    ```python
    with sim_messaging():
        sim = BasicSimulator(rume)
        my_results = sim.run()
    ```
    """

    start_time: float | None = None

    def on_start(e: OnStart) -> None:
        start_date = e.rume.time_frame.start_date
        end_date = e.rume.time_frame.end_date
        duration_days = e.rume.time_frame.days

        print(f"Running simulation ({e.simulator}):")
        print(f"• {start_date} to {end_date} ({duration_days} days)")
        print(f"• {e.rume.scope.nodes} geo nodes")
        if live:
            print(progress(0.0), end="\r")

        nonlocal start_time
        start_time = perf_counter()

    # keeping track of the length of the last line we printed
    # lets us clear any trailing characters when rendering stuff
    # after the progress bar of varying width
    last_progress_length = 0

    def on_tick(e: OnTick) -> None:
        # NOTE: tick updates will be skipped entirely if `live=False`
        nonlocal last_progress_length
        ticks_complete = e.tick_index + 1
        total_process_time = perf_counter() - start_time
        average_process_time = total_process_time / ticks_complete

        percent_complete = (e.tick_index + 1) / e.ticks
        ticks_left = e.ticks - ticks_complete

        # multiply the remaining ticks by the average processing time
        estimate = ticks_left * average_process_time

        time_remaining = humanize.precisedelta(ceil(estimate), minimum_unit="seconds")
        formatted_time = f"({time_remaining} remaining)"
        line = f"  {progress(percent_complete)}"
        # if no time remaining, omit the time progress
        if estimate > 0:
            line += f"{formatted_time}"
        print(line.ljust(last_progress_length), end="\r")
        last_progress_length = len(line)

    def on_finish(_: None) -> None:
        end_time = perf_counter()
        line = f"  {progress(1.0)}"
        print(line.ljust(last_progress_length), end="\n")
        if start_time is not None:
            print(f"Runtime: {(end_time - start_time):.3f}s")

    def on_adrio_progress(e: ADRIOProgress) -> None:
        nonlocal last_progress_length
        if e.ratio_complete == 0:
            if e.attribute == NAME_PLACEHOLDER:
                print(f"Loading {e.adrio_name}:")
            else:
                print(f"Loading {e.attribute} ({e.adrio_name}):")
        if not e.final:
            if e.download is None:
                dl = ""
            else:
                total, downloaded, speed = e.download
                ff = partial(naturalsize, binary=False)  # format file size
                dwn = "?" if downloaded is None else ff(downloaded)
                tot = "?" if total is None else ff(total)
                spd = "?" if speed is None else ff(speed)
                dl = f" {dwn}/{tot} ({spd}/s)"

            if live:
                line = f"  {progress(e.ratio_complete)}{dl}"
                print(line.ljust(last_progress_length), end="\r")
                last_progress_length = len(line)
        else:
            if e.duration is None:
                dur = ""
            else:
                dur = f" ({e.duration:0.3f}s)"
            line = f"  {progress(e.ratio_complete)}{dur}"
            print(line.ljust(last_progress_length))
            last_progress_length = 0

    with subscriptions() as subs:
        # Set up a subscriptions context, subscribe our handlers,
        # then yield to the outer context (ostensibly where the sim will be run).
        subs.subscribe(_events.on_start, on_start)
        if live:
            subs.subscribe(_events.on_tick, on_tick)
        subs.subscribe(_events.on_finish, on_finish)
        if adrio:
            subs.subscribe(_events.on_adrio_progress, on_adrio_progress)
        yield  # to outer context
        # And now our event handlers will be unsubscribed.
