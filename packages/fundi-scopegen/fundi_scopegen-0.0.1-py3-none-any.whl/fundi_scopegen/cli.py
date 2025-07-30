import os
import sys
from importlib import import_module

import rich
import typer
from rich.syntax import Syntax
from fundi import Parameter, scan

from .resolve import resolve_annotation
from .flatenize import flatenize_parameters
from .build import build_imports, build_scope
from .util import merge_imports, snake_to_pascal


app = typer.Typer()


@app.command()
def codegen(
    pythonic_path: str,
    colored: bool = False,
    no_imports: bool = False,
):
    sys.path.append(os.getcwd())
    package, _, dependant_name = pythonic_path.rpartition(".")

    if package == "":
        module = import_module(dependant_name)

        dependant = getattr(module, dependant_name, None)

    else:
        module = import_module(package)

        dependant = getattr(module, dependant_name)

    if dependant is None:
        raise ValueError("Dependant not found")

    scope_name = snake_to_pascal(dependant_name)

    info = scan(dependant)

    flat_parameters = flatenize_parameters(info)

    parameters: list[tuple[Parameter, str]] = []
    imports: dict[str, set[str]] = {}

    for parameter in flat_parameters:
        parameter_imports, pythonic_annotation = resolve_annotation(parameter.annotation)

        imports = merge_imports(imports, parameter_imports)
        parameters.append((parameter, pythonic_annotation))

    if no_imports:
        pythonic_imports = ""
    else:
        pythonic_imports = build_imports(imports)

    typed_dict = build_scope(
        parameters,
        sort_parameters=lambda p: sorted(p, key=len, reverse=True),
        class_name=scope_name + "Scope",
    )

    code = (pythonic_imports + "\n\n" + typed_dict).strip()

    if not colored:
        print(code)
        exit()

    rich.print(Syntax(code, "python3"))


if __name__ == "__main__":
    app()
