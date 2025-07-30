import types
import typing
import inspect

from fundi import TypeResolver

from .util import merge_imports


def resolve_union(*annotations: typing.Any) -> tuple[dict[str, set[str]], str]:
    imports: dict[str, set[str]] = dict()
    pythonic_names: list[str] = []

    for annotation in annotations:
        annotation_imports, annotation_pythonic = resolve_annotation(annotation)

        imports = merge_imports(imports, annotation_imports)
        pythonic_names.append(annotation_pythonic)

    return imports, " | ".join(sorted(pythonic_names, key=len))


def resolve_parameterized(origin: typing.Any, *args: typing.Any) -> tuple[dict[str, set[str]], str]:
    imports: dict[str, set[str]] = dict()

    pythonic_name = origin.__name__

    modulename = origin.__module__
    if modulename != "builtins":
        imports[modulename] = {pythonic_name}

    pythonic_parameters: list[str] = []

    for subannotation in args:
        parameter_imports, parameter_pythonic = resolve_annotation(subannotation)

        imports = merge_imports(imports, parameter_imports)
        pythonic_parameters.append(parameter_pythonic)

    return imports, pythonic_name + f"[{', '.join(pythonic_parameters)}]"


def resolve_single(annotation: typing.Any) -> tuple[dict[str, set[str]], str]:
    if not isinstance(annotation, type):
        type_ = type(annotation)  # pyright: ignore[reportUnknownVariableType]
        pythonic_name = type_.__name__
        modulename = type_.__module__

    else:
        pythonic_name = annotation.__name__
        modulename = annotation.__module__

    if modulename != "builtins":
        return {modulename: {pythonic_name}}, pythonic_name

    return {}, pythonic_name


def resolve_literal(arg: typing.Any) -> tuple[dict[str, set[str]], str]:
    if isinstance(arg, (str, int, float, bool, bytes, types.NoneType)):
        return {"typing": {"Literal"}}, "Literal[" + repr(arg) + "]"
    return resolve_annotation(arg)


def resolve_type_resolver(arg: typing.Any):
    imports, pythonic = resolve_annotation(arg)
    imports = merge_imports(imports, {"fundi": {"FromType"}})

    return imports, "FromType[" + pythonic + "]"


def resolve_annotation(annotation: typing.Any) -> tuple[dict[str, set[str]], str]:
    if annotation is inspect.Parameter.empty:
        return {"typing": {"Any"}}, "Any"

    if annotation is None or annotation is types.NoneType:
        return {}, "None"

    if annotation is ...:
        return {}, "..."

    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)

    if origin is types.UnionType or origin is typing.Union:  # pyright: ignore[reportDeprecated]
        return resolve_union(*args)
    elif origin is typing.Literal:
        return resolve_literal(args[0])
    elif origin is typing.Annotated and len(args) == 2 and args[1] is TypeResolver:
        return resolve_type_resolver(args[0])
    elif origin is not None:
        return resolve_parameterized(origin, *args)
    else:
        return resolve_single(annotation)
