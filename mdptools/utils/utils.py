import re
from typing import TYPE_CHECKING, Callable, Union

if TYPE_CHECKING:
    from ..mdp import MDP
    from ..graph import Digraph

from .highlight import Highlight
from .types import StrongTransitionMap, RenameFunction


highlight = _c = Highlight()
use_colors = highlight.use_colors


def word_color(word: str, color_map: dict[str,list[str]] = None):
    if isinstance(color_map, str):
        return color_map
    if color_map is not None:
        for new_color, words in color_map.items():
            if word in words:
                return new_color
    return _c.string


def format_strings(s: str, color_map: dict[str,list[str]] = None) -> str:
    str_re = r"\"([^\"\n]*?)\"|'([^'\n]*?)'"
    # pylint: disable=undefined-variable
    return re.sub(str_re, lambda x: (
        word := f"{x[1] or ''}{x[2] or ''}",
        color := word_color(word, color_map),
        color + word + _c.reset)[-1], s)


def format_floats(s: str) -> str:
    float_re = (r"([^\w\\'])"
        r"(?:(?:(?:(0*[1-9][0-9]*)|0+)(?:\.?0+|(\.?0*[1-9][0-9]*)))|(\.[0-9]+))"
        r"([^\w\\'])")
    return re.sub(float_re, r"\1" + _c.numeral + r"\2\3\4" + _c.reset + r"\5", s)


def round_floats(s: str) -> str:
    round_re = r"(\.[0-9]*?[1-9]+)0+[1-9](?![0-9])"
    return re.sub(round_re, r"\1", s)


def lit_str(obj, color_map: dict[str,list[str]] = None) -> str:
    return format_strings(format_floats(round_floats(obj.__str__())), color_map)


def map_list(lst: list[str]) -> dict[str, int]:
    if lst is None:
        return {}
    if isinstance(lst, str):
        lst = re.split(r"\s*,\s*", lst)
    return {value: index for index, value in enumerate(lst)}


def key_by_value(obj: dict, value) -> str:
    if not value in obj.values():
        return None
    return list(obj.keys())[list(obj.values()).index(value)]


def parse_sas_str(sas: any) -> tuple[str, str, str]:
    res = [None, None, None]

    if sas is None:
        return res

    if not isinstance(sas, str):
        sas = "->".join(sas)

    for idx, value in enumerate(re.split(r"\s*->\s*", f"{sas}")):
        if idx < len(res) and value != '':
            res[idx] = value

    return res


def walk_dict(obj, callback, path: list[str] = None, default_value: float = 1.0):
    if path is None:
        path = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            walk_dict(value, callback, path + [key])
    elif isinstance(obj, set):
        for key in obj:
            callback(path + [key], default_value)
    elif isinstance(obj, str):
        callback(path + [obj], default_value)
    else:
        callback(path, obj)


def prompt_fail(prompt, code):
    return f"[{_c[_c.fail, 'Failed']}] {_c[_c.note, prompt]}\n{' '*9}>> {code}"


def prompt_error(error, tip, code):
    return f"{_c[_c.error, error]}\n{' '*11}{tip}\n{' '*11}>> {code}"


def mdp_to_str(mdp: 'MDP'):
    lines = []
    # Name and validity
    lines += [f"{_c[_c.variable, mdp.name]} -> {_c[_c.typing, 'MDP']} "
              f"[{_c[_c.ok, 'Valid'] if mdp.is_valid else _c[_c.fail, 'Invalid']}]:"]
    # States and start state
    lines += [f"  {_c[_c.variable, 'S']} := {lit_str(tuple(mdp.S), _c.state)},"
              f" {_c[_c.variable, 's_init']} := {_c[_c.state, mdp.s_init]} "
             + _c[_c.comment, f"// {len(mdp.S)}"]]
    # Actions
    lines += [f"  {_c[_c.variable, 'A']} := {lit_str(tuple(mdp.A), _c.action)} "
             + _c[_c.comment, f"// {len(mdp.A)}"]]
    # Enabled transitions
    lines += [(en_s := mdp[s], f"  {_c[_c.function, 'en']}({_c[_c.state, s]}) ->"
              f" {lit_str(en_s, mdp_color_map(mdp))} " + _c[_c.comment, f"// {len(en_s)}"])[-1]
              for s in mdp.S]
    # Errors
    lines += [prompt_fail(msg, code) for (_, msg), code in mdp.errors]
    return "\n".join(lines)


def mdp_color_map(mdp: 'MDP'):
    if _c.state == '':
        return {}
    return {
        _c.state: list(mdp.S.keys()),
        _c.action: list(mdp.A.keys())
    }


def dist_wrong_value(s, a, value):
    return prompt_error(
        "Set is not allowed as a distribution value.",
        "Please use a Dictionary instead.",
        f"{_c[_c.function, 'Dist']}({_c[_c.state, s]}, {_c[_c.action, a]}) -> {lit_str(value)}")




def rename_map(obj: dict, rename: RenameFunction) -> dict[str, str]:
    rename = ensure_rename_function(rename)
    return { s: rename(s) for s in obj }



def rename_transition_map(old_map: StrongTransitionMap, states_map: dict[str, str],
        actions_map: dict[str, str]) -> StrongTransitionMap:
    return { states_map[s]: { actions_map[a]: { states_map[s_prime]: p
                for s_prime, p in dist_a.items() }
            for a, dist_a in act_s.items() }
        for s, act_s in old_map.items() }

def ensure_rename_function(rename: RenameFunction) -> Callable[[str], str]:
    if isinstance(rename, tuple):
        old, new = rename
        rename = lambda s: re.sub(old, new, s)
    elif isinstance(rename, list):
        rename_list = iter(rename)
        rename = lambda _: next(rename_list)
    elif isinstance(rename, dict):
        re_map = rename
        rename = lambda s: re_map[s] if s in re_map else s
    elif rename is None or not isinstance(rename, Callable):
        return lambda s: s
    return rename


def lazy_parallel(m1: 'MDP', m2: 'MDP', name: str = None) -> 'MDP':
    from ..parallel import parallel as _parallel
    return _parallel(m1, m2, name)


def lazy_graph(mdp: Union['MDP', list['MDP']], file_path: str,
    file_format: str = 'svg', engine: str = 'dot', rankdir: str = 'TB') -> 'Digraph':
    from ..graph import graph as _graph
    return _graph(mdp, file_path, file_format, engine, rankdir)
