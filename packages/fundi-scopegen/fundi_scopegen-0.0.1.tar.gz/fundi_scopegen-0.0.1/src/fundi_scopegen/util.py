def merge_imports(a: dict[str, set[str]], b: dict[str, set[str]]) -> dict[str, set[str]]:
    return {name: a.get(name, set()).union(b.get(name, set())) for name in (*a, *b)}


def snake_to_pascal(source: str, sep: str = "_") -> str:
    return "".join(word[0].upper() + word[1:] for word in source.split(sep) if word)
