from itertools import chain
from mdptools import MarkovDecisionProcess as MDP


def make_system(n: int) -> MDP:
    return MDP(*([make_sensor(i) for i in range(1, n + 1)] + [make_device(n)]))


def make_sensor(i: int) -> MDP:
    s = [f"active_{i}", f"prepare_{i}", f"detected_{i}", f"inactive_{i}"]
    return MDP(
        [
            (f"detect_{i}", s[0], {s[1]: 0.8, s[2]: 0.2}),
            (f"warn_{i}", s[1], s[2]),
            (f"shutdown_{i}", s[2], s[3]),
            ("tau", s[3]),
        ],
        init=s[0],
        name=f"S{i}",
    )


def make_device(n: int) -> MDP:
    s = ["running", "stopping", "off", "failed"]
    return MDP(
        list(
            chain.from_iterable(
                (
                    (f"warn_{i}", s[0], s[1]),
                    (f"shutdown_{i}", s[0], {s[2]: 0.9, s[3]: 0.1}),
                    (f"shutdown_{i}", s[1], s[2]),
                )
                for i in range(1, n + 1)
            )
        )
        + [
            ("tau", s[2]),
            ("tau", s[3]),
        ],
        init=s[0],
        name="D",
    )


def make_anon_sensor() -> MDP:
    s = ["active", "prepare", "detected", "inactive"]
    return MDP(
        [
            ("detect", s[0], {s[1]: 0.8, s[2]: 0.2}),
            ("warn", s[1], s[2]),
            ("shutdown", s[2], s[3]),
            ("tau", s[3]),
        ],
        init=s[0],
        name="S",
    )


def make_anon_device() -> MDP:
    s = ["running", "stopping", "off", "failed"]
    return MDP(
        [
            ("warn", s[0], s[1]),
            ("shutdown", s[0], {s[2]: 0.9, s[3]: 0.1}),
            ("shutdown", s[1], s[2]),
            ("tau", s[2]),
            ("tau", s[3]),
        ],
        init=s[0],
        name="D",
    )
