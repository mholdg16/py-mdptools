import sys
import numpy as _np

from .types import (
    Action,
    Distribution,
    ErrorCode,
    MarkovDecisionProcess,
    State,
)
from .utils import highlight as _h, format_str


MDP_REQ_EN_S_NONEMPTY: ErrorCode = (0, "forall s in S : en(s) != {}")
MDP_REQ_SUM_TO_ONE: ErrorCode = (
    1,
    "forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1",
)


def validate(
    mdp: MarkovDecisionProcess, raise_exception: bool = False
) -> bool:
    mdp.errors = []
    buffer = []

    def add_err(err_code: ErrorCode, err: str):
        mdp.errors += [(err_code, err)]
        return [fail(err_code[1], err)]

    en_s_nonempty, errors = __validate_enabled_nonempty(mdp)
    if not en_s_nonempty:
        for err in errors:
            buffer += add_err(MDP_REQ_EN_S_NONEMPTY, err)

    sum_to_one, errors = __validate_sum_to_one(mdp)
    if not sum_to_one:
        for err in errors:
            buffer += add_err(MDP_REQ_SUM_TO_ONE, err)

    if len(buffer) != 0:
        message = _h[_h.error, f"Not a valid MDP [{mdp.name}]:\n"] + "\n".join(
            buffer
        )
        if raise_exception:
            sys.tracebacklimit = 0
            raise Exception(message)

    return len(buffer) == 0


def __validate_enabled_nonempty(
    mdp: MarkovDecisionProcess,
) -> tuple[bool, list[str]]:
    """Validate: 'forall s in S : en(s) != {}'"""
    errors = [
        f"{_h[_h.function, 'en']}({format_str(s, _h.state)}) -> {_h[_h.error, '{}']}"
        for s in mdp.S
        if len(mdp.enabled(s)) == 0
    ]
    return (len(errors) == 0, errors)


def __validate_sum_to_one(
    mdp: MarkovDecisionProcess,
) -> tuple[bool, list[str]]:
    """Validate: 'forall s in S, a in en(s) : sum_(s' in S) P(s, a, s') = 1'"""
    errors = []

    for s in mdp.S:
        for a, dist in mdp.actions(s).items():
            sum_a = _np.abs(sum(dist.values()))
            if sum_a - 1.0 >= 10 * _np.spacing(_np.float64(1)):
                errors += __format_sum_to_one(dist, s, a, sum_a)

    return (len(errors) == 0, errors)


def __format_sum_to_one(
    dist: Distribution, s: State, a: Action, sum_a: float
) -> list[str]:
    return [
        f"{_h[_h.function, 'Dist']}({format_str(s, _h.state)}, "
        f"{_h[_h.action, a]}) -> {format_str(dist)} "
        f"{_h[_h.comment, '// sum -> '] + _h[_h.error, str(sum_a)]}"
    ]


def fail(message, code) -> str:
    return (
        f"[{_h[_h.fail, 'Failed']}] {_h[_h.note, message]}\n{' '*9}>> {code}"
    )
