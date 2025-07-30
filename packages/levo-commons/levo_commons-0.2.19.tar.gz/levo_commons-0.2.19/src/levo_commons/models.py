#
#  Copyright ©2022. Levo.ai Inc. All Rights Reserved.
#  You may not copy, reproduce, distribute, publish, display, perform, modify, create derivative works, transmit,
#  or in any way exploit any such software/code, nor may you distribute any part of this software/code over any network,
#  including a local area network, sell or offer it for commercial purposes.
#

from __future__ import annotations

import datetime
import logging
import threading
from enum import Enum, auto
from logging import LogRecord
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from uuid import uuid4

import attr
import curlify
import requests

from .cwe import CWE
from .failures import Evidence
from .status import Status
from .types import Headers, ResponseValueLocation
from .utils import base64_decode, base64_encode, format_exception


class Payload:
    """Base class for module-specific payload."""


@attr.s(slots=True, repr=False)
class Case:
    text_lines: Optional[List[str]] = attr.ib(default=None)
    requests_code: Optional[str] = attr.ib(default=None)
    curl_code: Optional[str] = attr.ib(default=None)


class Risk(str, Enum):
    """Risk on a failed assertion."""

    low = "Low"
    medium = "Medium"
    high = "High"

    def __str__(self) -> str:
        return self.value


class Confidence(str, Enum):
    """Confidence of an assertion."""

    low = "Low"
    medium = "Medium"
    high = "High"

    def __str__(self) -> str:
        return self.value


class Module(Enum):
    """Equivalent to the "Module" enum in the test_manifest.proto file."""

    BESPOKE = auto()
    SCHEMATHESIS = auto()
    ZAPROXY = auto()

    def __str__(self) -> str:
        return self.name


@attr.s(slots=True, repr=False)
class ResponseDiffProof:
    """Assertion proof based on response difference."""

    left_interaction_id: str = attr.ib()
    right_interaction_id: str = attr.ib()
    should_be_same: bool = attr.ib()
    diff: float = attr.ib()
    diff_gte: Optional[float] = attr.ib(default=None)
    diff_lte: Optional[float] = attr.ib(default=None)


@attr.s(slots=True, repr=False)
class ResponseStatusProof:
    """Assertion proof based on response status."""

    interaction_id: str = attr.ib()
    status: int = attr.ib()
    in_range: Tuple[int, int] = attr.ib(default=None)
    not_in_range: Tuple[int, int] = attr.ib(default=None)


@attr.s(slots=True, repr=False)
class ResponseExpectedValuesProof:
    """Assertion proof based on response values."""

    interaction_id: str = attr.ib()
    expected_values: List[Tuple[ResponseValueLocation, str, Any]] = attr.ib()
    not_expected_values: List[Tuple[ResponseValueLocation, str, Any]] = attr.ib()


AssertionProof = Union[
    ResponseDiffProof, ResponseStatusProof, ResponseExpectedValuesProof
]


@attr.s(slots=True, repr=False)
class AssertionResult:
    """Assertion result."""

    name: str = attr.ib()
    status: Status = attr.ib()
    interactions: List[Interaction] = attr.ib(factory=list)
    elapsed: float = attr.ib(factory=float)
    confidence: Confidence = attr.ib(default=Confidence.low)
    risk: Risk = attr.ib(default=Risk.low)
    id: str = attr.ib(factory=(lambda: str(uuid4())))
    recorded_at: str = attr.ib(factory=lambda: datetime.datetime.now().isoformat())
    evidence: Optional[Evidence] = attr.ib(default=None)
    proofs: Optional[List[AssertionProof]] = attr.ib(default=None)
    reference: Optional[str] = attr.ib(default=None)
    solution: Optional[str] = attr.ib(default=None)
    message: Optional[str] = attr.ib(default=None)
    code: Optional[str] = attr.ib(default=None)
    cwe: Optional[CWE] = attr.ib(default=None)
    extra_data: Optional[dict[str, Any]] = attr.ib(default=None)


@attr.s(slots=True, repr=False)
class Request:
    """Request data extracted from TestCase."""

    method: str = attr.ib()
    uri: str = attr.ib()
    body: Optional[str] = attr.ib()
    headers: Headers = attr.ib()

    @classmethod
    def from_prepared_request(cls, prepared: requests.PreparedRequest) -> "Request":
        """A prepared request version is already stored in `requests.Response`."""
        body = prepared.body

        if isinstance(body, str):
            # can be a string for `application/x-www-form-urlencoded`
            body = body.encode("utf-8")

        # these values have `str` type at this point
        uri = cast(str, prepared.url)
        method = cast(str, prepared.method)
        return cls(
            uri=uri,
            method=method,
            headers={key: [value] for (key, value) in prepared.headers.items()},
            body=base64_encode(body) if body is not None else body,
        )

    def as_curl_command(self) -> str:
        """Construct a curl command for a given Request."""
        prepared_request = requests.PreparedRequest()
        prepared_request.prepare(
            url=self.uri,
            method=self.method,
            headers={
                key: ";".join(value) if isinstance(value, list) else value
                for (key, value) in self.headers.items()
            },
            data=base64_decode(self.body) if self.body is not None else None,
        )

        return curlify.to_curl(prepared_request)


def serialize_payload(payload: bytes) -> str:
    return base64_encode(payload)


@attr.s(slots=True, repr=False)
class Response:
    """Unified response data."""

    status_code: int = attr.ib()
    message: str = attr.ib()
    headers: Dict[str, List[str]] = attr.ib()
    method: str = attr.ib()
    uri: str = attr.ib()
    body: Optional[str] = attr.ib()
    encoding: Optional[str] = attr.ib()
    http_version: str = attr.ib()

    @classmethod
    def from_requests(cls, response: requests.Response) -> "Response":
        """Create a response from requests.Response."""
        headers = {
            name: response.raw.headers.getlist(name)
            for name in response.raw.headers.keys()
        }
        # Similar to http.client:319 (HTTP version detection in stdlib's `http` package)
        http_version = "1.0" if response.raw.version == 10 else "1.1"

        def is_empty(_response: requests.Response) -> bool:
            # Assume the response is empty if:
            #   - no `Content-Length` header
            #   - no chunks when iterating over its content
            return (
                "Content-Length" not in headers and list(_response.iter_content()) == []
            )

        body = None if is_empty(response) else serialize_payload(response.content)

        original_request = (
            response.history[0].request
            if response.history and len(response.history) > 0
            else response.request
        )

        return cls(
            status_code=response.status_code,
            message=response.reason,
            method=original_request.method if original_request.method else "",
            uri=cast(str, original_request.url),
            body=body,
            encoding=response.encoding,
            headers=headers,
            http_version=http_version,
        )


@attr.s(slots=True)
class Interaction:
    """A single interaction with the target app."""

    request: Request = attr.ib()
    status: Status = attr.ib()
    id: str = attr.ib(factory=(lambda: str(uuid4())))
    response: Optional[Response] = attr.ib(default=None)
    elapsed: Optional[float] = attr.ib(default=None)
    name: Optional[str] = attr.ib(factory=str)
    recorded_at: str = attr.ib(factory=lambda: datetime.datetime.now().isoformat())
    tampered_headers: List[str] = attr.ib(factory=list)
    user_profile: Optional[str] = attr.ib(default=None)

    @classmethod
    def from_requests(
        cls, response: requests.Response, status: Status
    ) -> "Interaction":
        original_request = (
            response.history[0].request
            if response.history and len(response.history) > 0
            else response.request
        )
        return cls(
            request=Request.from_prepared_request(original_request),
            response=Response.from_requests(response),
            status=status,
            elapsed=response.elapsed.total_seconds() * 1000,
        )

    @classmethod
    def from_errored_request(cls, request: requests.PreparedRequest) -> "Interaction":
        return cls(
            request=Request.from_prepared_request(request),
            status=Status.error,
        )


class StepRecordType(str, Enum):
    assertion = "assertion"
    interaction = "interaction"
    log = "log"

    def __str__(self) -> str:
        return self.value


@attr.s(slots=True, repr=False)
class StepRecord:
    """Record within a step of a single test."""

    record_id: str = attr.ib()
    type: StepRecordType = attr.ib()
    summary: Optional[str] = attr.ib()


class StepLogRecord(LogRecord):
    id: str = attr.ib(factory=(lambda: str(uuid4())))


@attr.s(slots=True, repr=False)
class Step:
    """Step of a single test."""

    title: str = attr.ib()
    description: Optional[str] = attr.ib(factory=str)
    status: str = attr.ib(default=Status.success)
    records: List[StepRecord] = attr.ib(factory=list)

    def assertion(
        self, assertion: AssertionResult, summary: Optional[str] = None
    ) -> StepRecord:
        record = StepRecord(
            record_id=assertion.id,
            type=StepRecordType.assertion,
            summary=summary,
        )
        self.records.append(record)
        self.status += assertion.status
        return record

    def interaction(
        self, interaction: Interaction, summary: Optional[str] = None
    ) -> StepRecord:
        record = StepRecord(
            record_id=interaction.id,
            type=StepRecordType.interaction,
            summary=summary,
        )
        self.records.append(record)
        return record

    def log(self, log: LogRecord, summary: Optional[str] = None) -> StepRecord:
        record = StepRecord(
            record_id=log.id,  # type: ignore
            type=StepRecordType.log,
            summary=summary,
        )
        self.records.append(record)
        return record


@attr.s(slots=True, repr=False)
class TestResult:
    """Result of a single test."""

    __test__ = False
    assertions: Dict[str, AssertionResult] = attr.ib(factory=dict)
    errors: List[Exception] = attr.ib(factory=list)
    interactions: Dict[str, Interaction] = attr.ib(factory=dict)
    logs: Dict[str, LogRecord] = attr.ib(factory=dict)
    steps: List[Step] = attr.ib(factory=list)
    is_errored: bool = attr.ib(default=False)
    summary: Optional[str] = attr.ib(default=None)
    # To show a proper reproduction code if an error happens and there is no way to get actual headers that were
    # sent over the network. Or there could be no actual requests at all
    overridden_headers: Optional[Dict[str, Any]] = attr.ib(default=None)

    def __add__(self, other: TestResult) -> TestResult:
        return TestResult(
            assertions={**self.assertions, **other.assertions},
            errors=self.errors + other.errors,
            interactions={**self.interactions, **other.interactions},
            logs={**self.logs, **other.logs},
            is_errored=self.is_errored or other.is_errored,
            summary=self.summary,
        )

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def has_failures(self) -> bool:
        return any(
            assertion.status == Status.failure for assertion in self.assertions.values()
        )


@attr.s(slots=True)
class SerializedError:
    exception: str = attr.ib()
    exception_with_traceback: str = attr.ib()
    title: Optional[str] = attr.ib()

    @classmethod
    def from_error(
        cls,
        exception: Exception,
        title: Optional[str] = None,
    ) -> "SerializedError":
        return cls(
            exception=format_exception(exception),
            exception_with_traceback=format_exception(exception, True),
            title=title,
        )


@attr.s(slots=True)
class ValidationError:
    message: str = attr.ib()
    file: Optional[str] = attr.ib(default=None)
    lines: Optional[list[str]] = attr.ib(default=None)


@attr.s(slots=True)
class SerializedCWE:
    code: int = attr.ib()
    summary: str = attr.ib()

    @classmethod
    def from_cwe(cls, cwe: CWE) -> SerializedCWE:
        return cls(code=cwe.code, summary=cwe.summary)


@attr.s(slots=True, repr=False)
class SerializedBaseProof:
    type: str = attr.ib()

    @classmethod
    def from_proof(cls, proof: AssertionProof) -> "SerializedBaseProof":
        if isinstance(proof, ResponseDiffProof):
            return SerializedResponseDiffProof(
                type="response_diff",
                left_interaction_id=proof.left_interaction_id,
                right_interaction_id=proof.right_interaction_id,
                diff=proof.diff,
                should_be_same=proof.should_be_same,
                diff_gte=proof.diff_gte,
                diff_lte=proof.diff_lte,
            )
        if isinstance(proof, ResponseStatusProof):
            return SerializedResponseStatusProof(
                type="response_status",
                interaction_id=proof.interaction_id,
                status=proof.status,
                in_range=proof.in_range,
                not_in_range=proof.not_in_range,
            )
        if isinstance(proof, ResponseExpectedValuesProof):
            return SerializedResponseExpectedValuesProof(
                type="response_expected_values",
                interaction_id=proof.interaction_id,
                expected_values=proof.expected_values,
                not_expected_values=proof.not_expected_values,
            )


@attr.s(slots=True, repr=False)
class SerializedResponseDiffProof(SerializedBaseProof):
    left_interaction_id: str = attr.ib()
    right_interaction_id: str = attr.ib()
    should_be_same: bool = attr.ib()
    diff: float = attr.ib()
    diff_gte: Optional[float] = attr.ib(default=None)
    diff_lte: Optional[float] = attr.ib(default=None)


@attr.s(slots=True, repr=False)
class SerializedResponseStatusProof(SerializedBaseProof):
    interaction_id: str = attr.ib()
    status: int = attr.ib()
    in_range: Tuple[int, int] = attr.ib(default=None)
    not_in_range: Tuple[int, int] = attr.ib(default=None)


@attr.s(slots=True, repr=False)
class SerializedResponseExpectedValuesProof(SerializedBaseProof):
    interaction_id: str = attr.ib()
    expected_values: List[Tuple[ResponseValueLocation, str, Any]] = attr.ib()
    not_expected_values: List[Tuple[ResponseValueLocation, str, Any]] = attr.ib()


@attr.s(slots=True)
class SerializedAssertionResult:
    name: str = attr.ib()
    status: str = attr.ib()
    interactions: List[SerializedInteraction] = attr.ib()
    elapsed: float = attr.ib()
    confidence: str = attr.ib()
    risk: str = attr.ib()
    recorded_at: str = attr.ib()
    evidence: Optional[Evidence] = attr.ib()
    proofs: Optional[List[SerializedBaseProof]] = attr.ib()
    reference: Optional[str] = attr.ib()
    solution: Optional[str] = attr.ib()
    message: Optional[str] = attr.ib()
    code: Optional[str] = attr.ib()
    cwe: Optional[SerializedCWE] = attr.ib()
    extra_data: Optional[dict[str, Any]] = attr.ib()

    @classmethod
    def from_assertion_result(
        cls, assertion_result: AssertionResult
    ) -> "SerializedAssertionResult":
        return cls(
            name=assertion_result.name,
            status=str(assertion_result.status),
            interactions=[
                SerializedInteraction.from_interaction(interaction)
                for interaction in assertion_result.interactions
            ],
            elapsed=assertion_result.elapsed,
            confidence=str(assertion_result.confidence),
            risk=str(assertion_result.risk),
            recorded_at=assertion_result.recorded_at,
            evidence=assertion_result.evidence,
            proofs=[
                SerializedBaseProof.from_proof(proof)
                for proof in assertion_result.proofs
            ]
            if assertion_result.proofs
            else None,
            reference=assertion_result.reference,
            solution=assertion_result.solution,
            message=assertion_result.message,
            code=assertion_result.code,
            cwe=(
                SerializedCWE.from_cwe(assertion_result.cwe)
                if assertion_result.cwe
                else None
            ),
            extra_data=assertion_result.extra_data,
        )


@attr.s(slots=True)
class SerializedInteraction:
    request: Request = attr.ib()
    status: str = attr.ib()
    recorded_at: str = attr.ib()
    curl_code: str = attr.ib()
    tampered_headers: List[str] = attr.ib(factory=list)
    name: Optional[str] = attr.ib(factory=str)
    response: Optional[Response] = attr.ib(default=None)
    elapsed: Optional[float] = attr.ib(default=None)
    user_profile: Optional[str] = attr.ib(default=None)

    @classmethod
    def from_interaction(cls, interaction: Interaction) -> "SerializedInteraction":
        return cls(
            request=interaction.request,
            response=interaction.response,
            status=str(interaction.status),
            recorded_at=interaction.recorded_at,
            elapsed=interaction.elapsed,
            curl_code=interaction.request.as_curl_command(),
            name=interaction.name,
            tampered_headers=interaction.tampered_headers,
            user_profile=interaction.user_profile,
        )


@attr.s(slots=True)
class SerializedStepRecord:
    record_id: str = attr.ib()
    type: str = attr.ib()
    summary: str = attr.ib()

    @classmethod
    def from_step_record(cls, step_record: StepRecord) -> "SerializedStepRecord":
        return cls(
            record_id=str(step_record.record_id),
            type=str(step_record.type),
            summary=step_record.summary if step_record.summary else "",
        )


@attr.s(slots=True)
class SerializedStep:
    title: str = attr.ib()
    description: str = attr.ib()
    records: List[SerializedStepRecord] = attr.ib(factory=list)
    status: str = attr.ib(factory=(lambda: str(Status.success)))

    @classmethod
    def from_step(cls, step: Step) -> "SerializedStep":
        return cls(
            title=step.title,
            description=step.description if step.description else "",
            records=[
                SerializedStepRecord.from_step_record(record) for record in step.records
            ],
            status=str(step.status),
        )


@attr.s(slots=True)
class SerializedTestResult:
    assertions: Dict[str, SerializedAssertionResult] = attr.ib()
    errors: List[SerializedError] = attr.ib()
    interactions: Dict[str, SerializedInteraction] = attr.ib()
    logs: Dict[str, dict] = attr.ib()
    steps: List[SerializedStep] = attr.ib()
    summary: Optional[str] = attr.ib()
    # To show a proper reproduction code if an error happens and there is no way to get actual headers that were
    # sent over the network. Or there could be no actual requests at all
    overridden_headers: Optional[Dict[str, Any]] = attr.ib()
    has_failures: bool = attr.ib()
    has_errors: bool = attr.ib()
    has_logs: bool = attr.ib()
    is_errored: bool = attr.ib()

    @classmethod
    def from_test_result(cls, result: TestResult) -> "SerializedTestResult":
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )
        return cls(
            has_failures=result.has_failures,
            has_errors=result.has_errors,
            has_logs=len(result.logs) > 0,
            is_errored=result.is_errored,
            logs={
                str(key): {
                    "message": logging.Formatter("%(message)s").format(record),
                    "formatted": formatter.format(record),
                    "level": record.levelname,
                    "created": record.created,
                }
                for key, record in result.logs.items()
            },
            errors=[SerializedError.from_error(error) for error in result.errors],
            interactions={
                str(interaction_id): SerializedInteraction.from_interaction(interaction)
                for interaction_id, interaction in result.interactions.items()
            },
            assertions={
                str(assertion_id): SerializedAssertionResult.from_assertion_result(
                    assertion_result
                )
                for assertion_id, assertion_result in result.assertions.items()
            },
            steps=[SerializedStep.from_step(step) for step in result.steps],
            summary=result.summary,
            overridden_headers=result.overridden_headers,
        )


@attr.s(slots=True)
class InitializedPayload(Payload):
    plan_id: str = attr.ib()
    plan_name: str = attr.ib()
    workspace_id: str = attr.ib()

    # The target URL against which the tests are running
    target_url: str = attr.ib()

    # A dictionary to hold some generic attributes like entity metadata, etc.
    attributes: dict = attr.ib(factory=dict)
    app_id: Optional[str] = attr.ib(default=None)


@attr.s(slots=True)
class BeforeTestSuiteExecutionPayload(Payload):
    name: str = attr.ib()
    test_suite_id: Optional[str] = attr.ib(default=None)
    modules: List[str] = attr.ib(factory=list)
    # This is the list of Auth headers for the test suite or endpoint that's being tested.
    # This will enable the event consumers to treat the auth header(s) specially,
    # like masking them or completely removing them from the reported results.
    auth_headers: List[str] = attr.ib(factory=list)
    endpoint_id: Optional[str] = attr.ib(default=None)
    app_id: Optional[str] = attr.ib(default=None)
    target_urls: Optional[List[str]] = attr.ib(default=None)


@attr.s(slots=True)
class AfterTestSuiteExecutionPayload(Payload):
    name: str = attr.ib()
    test_suite_id: Optional[str] = attr.ib(default=None)
    errored: bool = attr.ib(default=False)
    thread_id: int = attr.ib(factory=threading.get_ident)
    endpoint_id: Optional[str] = attr.ib(default=None)
    app_id: Optional[str] = attr.ib(default=None)
    working_target_url: Optional[str] = attr.ib(default=None)


@attr.s(slots=True, kw_only=True)
class BeforeTestExecutionPayload(Payload):
    test_case_id: str = attr.ib()
    name: str = attr.ib()
    method: str = attr.ib()
    path: str = attr.ib()
    relative_path: str = attr.ib()
    categories: list[str] = attr.ib(factory=list)
    test_suite_id: Optional[str] = attr.ib(default=None)
    description: Optional[str] = attr.ib(default=None)

    # The current level of recursion during stateful testing
    recursion_level: int = attr.ib(default=0)

    module: Optional[str] = attr.ib(default=None)
    endpoint_id: Optional[str] = attr.ib(default=None)


@attr.s(slots=True)
class AfterTestExecutionPayload(Payload):
    test_case_id: str = attr.ib()
    name: str = attr.ib()
    method: str = attr.ib()
    path: str = attr.ib()
    relative_path: str = attr.ib()
    status: str = attr.ib()
    elapsed_time: float = attr.ib()
    result: Optional[TestResult] = attr.ib()
    test_suite_id: Optional[str] = attr.ib(default=None)
    thread_id: int = attr.ib(factory=threading.get_ident)
    skipped_reason: Optional[str] = attr.ib(default=None)
    endpoint_id: Optional[str] = attr.ib(default=None)

    def __add__(self, other: AfterTestExecutionPayload) -> AfterTestExecutionPayload:
        if not self.result:
            result = other.result
        elif not other.result:
            result = self.result
        else:
            result = self.result + other.result

        return AfterTestExecutionPayload(
            test_case_id=self.test_case_id,
            name=self.name,
            method=self.method,
            path=self.path,
            relative_path=self.path,
            status=self.status + other.status,
            elapsed_time=self.elapsed_time + other.elapsed_time,
            result=result,
            test_suite_id=self.test_suite_id,
            thread_id=self.thread_id,
            endpoint_id=self.endpoint_id,
        )


@attr.s(slots=True)
class AfterStepExecutionPayload(Payload):
    test_case_id: str = attr.ib()
    sequence: int = attr.ib()
    elapsed_time: float = attr.ib()
    step: Step = attr.ib()


@attr.s(slots=True)
class FinishedPayload(Payload):
    plan_id: str = attr.ib()
    has_failures: bool = attr.ib(default=False)
    has_errors: bool = attr.ib(default=False)
    generic_errors: List[Exception] = attr.ib(factory=list)
    app_id: Optional[str] = attr.ib(default=None)
