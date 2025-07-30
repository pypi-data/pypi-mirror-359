import typing

from fundi import CallableInfo, Parameter


def flatenize_parameters(info: CallableInfo[typing.Any]) -> list[Parameter]:
    flat_parameters: list[Parameter] = []

    walk_thru: list[CallableInfo[typing.Any]] = [info]
    walked_thru: list[typing.Callable[..., typing.Any]] = []

    while walk_thru:
        for info in walk_thru.copy():
            for parameter in info.parameters:
                if parameter.from_ is not None:
                    if parameter.from_.call not in walked_thru:
                        walk_thru.append(parameter.from_)
                    continue

                flat_parameters.append(parameter)

            walked_thru.append(info.call)
            walk_thru.remove(info)

    return flat_parameters
