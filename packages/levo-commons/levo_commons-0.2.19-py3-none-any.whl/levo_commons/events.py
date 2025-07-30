#
#  Copyright ©2022. Levo.ai Inc. All Rights Reserved.
#  You may not copy, reproduce, distribute, publish, display, perform, modify, create derivative works, transmit,
#  or in any way exploit any such software/code, nor may you distribute any part of this software/code over any network,
#  including a local area network, sell or offer it for commercial purposes.
#

# This file is not exposed to customer in UI
import threading
import time
from typing import Generic, List, Optional, TypeVar

import attr

from .models import Payload, ValidationError

P = TypeVar("P", bound=Payload)


@attr.s()
class Event(Generic[P]):
    """Base event for all other Levo events."""

    # Whether the given event should be the last one in a stream.
    is_terminal = False
    # Shortcut to convert events to dictionaries
    asdict = attr.asdict
    payload: Optional[P] = attr.ib(kw_only=True, default=None)


@attr.s(slots=True)
class Initialized(Event[P], Generic[P]):
    """Denotes the beginning of some process."""

    start_time: float = attr.ib(factory=time.monotonic)


@attr.s(slots=True)
class BeforeTestSuiteExecution(Event[P], Generic[P]):
    """Just before a test suite."""

    start_time: float = attr.ib(factory=time.monotonic)


@attr.s(slots=True)
class AfterTestSuiteExecution(Event[P], Generic[P]):
    """After a test suite."""

    # Total execution time
    running_time: float = attr.ib()


@attr.s(slots=True)
class BeforeTestCaseExecution(Event[P], Generic[P]):
    """Just before a test case."""


@attr.s(slots=True)
class BeforeTestStepExecution(Event[P], Generic[P]):
    """Before each step inside a test case."""


@attr.s(slots=True)
class AfterTestStepExecution(Event[P], Generic[P]):
    """After each step in a test case."""


@attr.s(slots=True)
class AfterTestCaseExecution(Event[P], Generic[P]):
    """After a test case."""


@attr.s(slots=True)
class Interrupted(Event):
    """If execution was interrupted by Ctrl-C, or a received SIGTERM."""

    thread_id: int = attr.ib(factory=threading.get_ident)


@attr.s(slots=True)
class InternalError(Event):
    """An error happened during the process.

    Contains meta-information about the occured Python exception.
    """

    message: str = attr.ib()
    exception_type: str = attr.ib()
    exception: Optional[str] = attr.ib(default=None)
    exception_with_traceback: Optional[str] = attr.ib(default=None)
    is_terminal: bool = attr.ib(default=True)
    thread_id: int = attr.ib(factory=threading.get_ident)


@attr.s(slots=True)
class PlanValidationError(Event):
    """An error happened during the process.

    Contains meta-information about the occured Python exception.
    """

    message: str = attr.ib()
    errors: List[ValidationError] = attr.ib()
    is_terminal: bool = attr.ib(default=True)


@attr.s(slots=True)
class Skipped(Event):
    """Test case was skipped for some reason. Reason will be captured in the reason field."""

    reason: str = attr.ib()
    test_plan_id: Optional[str] = attr.ib(default=None)
    test_suite_id: Optional[str] = attr.ib(default=None)
    test_case_id: Optional[str] = attr.ib(default=None)


@attr.s(slots=True)
class Finished(Event[P], Generic[P]):
    """The final event of the run.

    No more events after this point.
    """

    is_terminal = True

    # Total execution time
    running_time: float = attr.ib()
