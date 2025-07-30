from functools import wraps
from typing import Any, Iterable, Optional, Sequence, Union

from rich import get_console
from rich.console import Console
from rich.progress import (
    BarColumn,
    GetTimeCallable,
    Progress,
    ProgressColumn,
    ProgressType,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from cotyper.log.logging import log

console = get_console()

MAX_NUM_TASK_DISPLAY = 4


class SelfCleaningProgress(Progress):
    def __init__(
        self,
        *columns: Union[str, ProgressColumn],
        console: Optional[Console] = None,
        auto_refresh: bool = True,
        refresh_per_second: float = 10,
        speed_estimate_period: float = 30.0,
        transient: bool = False,
        redirect_stdout: bool = True,
        redirect_stderr: bool = True,
        get_time: Optional[GetTimeCallable] = None,
        disable: bool = False,
        expand: bool = False,
        max_number_finished_tasks: int = MAX_NUM_TASK_DISPLAY,
    ) -> None:
        self.max_number_finished_tasks = max_number_finished_tasks
        super().__init__(
            *columns,
            console=console,
            auto_refresh=auto_refresh,
            refresh_per_second=refresh_per_second,
            speed_estimate_period=speed_estimate_period,
            transient=transient,
            redirect_stdout=redirect_stdout,
            redirect_stderr=redirect_stderr,
            get_time=get_time,
            disable=disable,
            expand=expand,
        )

    def add_task(
        self,
        description: str,
        start: bool = True,
        total: Optional[float] = 100.0,
        completed: int = 0,
        visible: bool = True,
        **fields: Any,
    ) -> TaskID:
        task_ids = self.task_ids
        tasks = self.tasks

        finished_tasks = list(
            filter(lambda item: item[1].finished, zip(task_ids, tasks))
        )
        if len(finished_tasks) > MAX_NUM_TASK_DISPLAY:
            to_rm_task_id, to_rm_task = min(finished_tasks, key=lambda item: item[0])

            try:
                self.remove_task(to_rm_task_id)
                log.info(
                    f"removed rich task {to_rm_task.description}, finished in {to_rm_task.finished_time:.3f}s"
                )
            except KeyError as e:
                log.error(e)

        return super().add_task(description, start, total, completed, visible, **fields)


progress = SelfCleaningProgress(
    SpinnerColumn(finished_text=":white_heavy_check_mark:"),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
    TimeElapsedColumn(),
    expand=True,
)


def remove_all_finished_tasks() -> None:
    for task in filter(lambda t: t.finished, progress.tasks):
        try:
            progress.remove_task(task.id)
        except IndexError as e:
            log.error(e)


def log_task(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        log.info(f"starting {fn.__name__}")
        result = fn(*args, **kwargs)
        log.info(f"finished {fn.__name__}")
        return result

    return wrapper


def progress_task(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        task_id = progress.add_task(description=f"{fn.__name__}", start=True, total=1)
        result = log_task(fn)(*args, **kwargs)
        progress.update(task_id, advance=1)

        return result

    return wrapper


def track(
    sequence: Union[Sequence[ProgressType], Iterable[ProgressType]],
    description: str = "Working...",
    total: Optional[float] = None,
    update_period: float = 0.1,
) -> Iterable[ProgressType]:
    remove_all_finished_tasks()

    total = total or len(sequence)

    task_id = progress.add_task(description, total=total)

    yield from progress.track(
        sequence,
        total=total,
        description=description,
        update_period=update_period,
        task_id=task_id,
    )
