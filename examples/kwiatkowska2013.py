from itertools import chain
from mdptools import MarkovDecisionProcess as MDP, graph
from mdptools.set_methods import stubborn_sets
from helpers import at_root, display_graph


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
        name=f"S",
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


def make_system(n: int) -> MDP:
    if n == 1:
        processes = [make_anon_sensor(), make_anon_device()]
    else:
        processes = [make_sensor(i + 1) for i in range(n)]
        processes += [make_device(n)]
    return MDP(*processes)


# %%
system = make_system(1).rename(
    (r"^([a-z])[a-z]*", r"\1")
    # (r"^([a-z]{1,2}[aeiouy][^aeiouy]?|[a-z]{1,2}[^aeiouy])[a-z]*", r"\1")
)

# %%
graph(
    *system.processes,
    file_path="out/graphs/example_processes",
    file_format="pdf",
)

# %%
graph(system, file_path="out/graphs/example_system", file_format="pdf")

# %%
graph(
    *system.processes,
    system,
    file_path="out/graphs/example_all",
    file_format="pdf",
)

# %%
system = make_system(2).rename(
    (r"^([a-z])[a-z]*", r"\1")
    # (r"^([a-z]{1,2}[aeiouy][^aeiouy]?|[a-z]{1,2}[^aeiouy])[a-z]*", r"\1")
)

# %%
graph(
    system,
    file_path="out/graphs/example_2_composed",
    file_format="pdf",
    set_method=stubborn_sets,
    highlight=True,
)

# %%
graph(
    system.rename((r"^([a-z])[a-z]*", r"\1")),
    file_path="out/graphs/example_2_reduced",
    file_format="pdf",
    set_method=stubborn_sets,
)

# %%
# print(system.to_prism(at_root("out/prism/kwiatkowska_composed.prism")))

# %%
sensor_count = 5

for n in range(1, sensor_count + 1):
    test_system = make_system(n)
    state_space = list(test_system.search(silent=True))
    state_space_ps = list(
        test_system.search(set_method=stubborn_sets, silent=True)
    )
    t = len(state_space)
    r = len(state_space_ps)
    p = round(abs(t - r) / t * 100)
    print(f"{n} sensors: {t} ({r} reduced, {p}% reduction)")
