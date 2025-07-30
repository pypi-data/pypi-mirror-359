import typing
from textwrap import dedent
from collections.abc import Sequence, Set

from fundi import Parameter


def build_imports(
    raw_imports: dict[str, set[str]],
    sort_names: typing.Callable[[Set[str]], Sequence[str]] = lambda n: sorted(n, key=len),
    sort_lines: typing.Callable[[Sequence[str]], Sequence[str]] = lambda n: sorted(n, key=len),
    group_packages: typing.Callable[[Sequence[str]], Sequence[Sequence[str]]] = lambda n: [n],
) -> str:
    package_groups = group_packages(list(raw_imports.keys()))

    import_groups: list[list[str]] = []

    for package_group in package_groups:
        import_group: list[str] = []
        import_groups.append(import_group)

        for package in package_group:
            names = raw_imports[package]
            import_group.append(
                "from {package} import {names}".format(
                    package=package, names=", ".join(sort_names(names))
                )
            )

    return "\n".join("\n".join(sort_lines(imports)) for imports in import_groups)


def build_parameters(
    parameters: list[tuple[Parameter, str]],
    sort_lines: typing.Callable[[Sequence[str]], Sequence[str]] = lambda l: sorted(l, key=len),
    sep: str = "\n",
) -> str:
    pythonic_parameters: list[str] = []
    for parameter, pythonic_annotation in parameters:
        typehint = ": " + pythonic_annotation
        if parameter.has_default:
            typehint = ": NotRequired[" + pythonic_annotation + "]"

        pythonic_parameters.append(f"{parameter.name}{typehint}")

    return sep.join(sort_lines(pythonic_parameters))


def build_scope(
    parameters: list[tuple[Parameter, str]],
    sort_parameters: typing.Callable[[Sequence[str]], Sequence[str]] = lambda l: sorted(l, key=len),
    class_name: str = "Scope",
) -> str:
    pythonic_parameters = build_parameters(parameters, sort_parameters, sep="\n    ")

    class_template = dedent(
        """
        class {name}(TypedDict):
            {parameters}
        """
    ).strip()

    klass = class_template.format(parameters=pythonic_parameters, name=class_name)

    return klass
