from mdptools import MarkovDecisionProcess as MDP
from mdptools.set_methods import persistent_set
from mdptools.utils import highlight as _h, format_str
from helpers import at_root, display_dot


def make_process(i: int):
    return MDP(
        [
            # format: (action, pre, post)
            (f"demand_{i}", f"noncrit_{i}", f"wait_{i}"),
            (f"request_{i}", (f"wait_{i}", "x=0"), f"wait_{i}"),
            (f"enter_{i}", (f"wait_{i}", f"x={i}"), f"crit_{i}"),
            (f"exit_{i}", f"crit_{i}", (f"noncrit_{i}", "x:=0")),
        ],
        init=f"noncrit_{i}",
        name=f"P{i}",
    )


def make_resource_manager(n: int):
    trs = []
    for i in range(1, n + 1):
        trs += [
            (f"request_{i}", "idle", {f"prepare_{i}": 0.9, "idle": 0.1}),
            (f"grant_{i}", f"prepare_{i}", ("idle", f"x:={i}")),
        ]
    return MDP(trs, init=("idle", "x:=0"), name="RM")


# %%
n = 2
processes = [make_process(i) for i in range(1, n + 1)]
processes += [make_resource_manager(n)]

for process in processes:
    print(process, "\n")

m = MDP(*processes)

print(m, "\n")

# %%
visited_states = []

for s, action_map in m.search(set_method=persistent_set):
    visited_states.append((s, action_map))

for s, action_map in visited_states:
    print(s, "->")
    for a, dist in action_map.items():
        print(
            f"  [{_h[_h.action, a]}]",
            " + ".join(f"{format_str(p)}:{s_}" for s_, p in dist.items()),
        )

# %%
display_dot(
    m.to_graph(
        at_root("out/graphs/baier2004_persistent.gv"),
        set_method=persistent_set,
    )
)
