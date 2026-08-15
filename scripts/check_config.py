#!/usr/bin/env python3
"""Static checks for komodo.toml.

Komodo resolves every `[[NAME]]` placeholder from one namespace holding both
Resource Sync variables and Core secrets. A placeholder with no source behind it
is only discovered at deploy time, on the NAS, so check it here instead:

- every placeholder is either a `[[variable]]` in komodo.toml or a secret
  documented in the README's Required Secrets block
- no secret is committed as a plain `[[variable]]`
- variables that nothing references are reported, since they are usually
  leftovers from a removed stack
"""

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KOMODO_TOML = ROOT / "komodo.toml"
README = ROOT / "README.md"

PLACEHOLDER = re.compile(r"\[\[([A-Z0-9_]+)\]\]")


def documented_secrets() -> set[str]:
    """Secret names from the ```toml [secrets] block in the README."""
    text = README.read_text()
    match = re.search(r"```toml\s*\n\[secrets\]\n(.*?)```", text, re.S)
    if not match:
        sys.exit("README has no [secrets] block; cannot verify placeholders")
    return set(re.findall(r"^([A-Z0-9_]+)\s*=", match.group(1), re.M))


def check_stack_coverage(config: dict) -> list[str]:
    """Every stack directory is managed, and CI validates every stack."""
    errors: list[str] = []

    on_disk = {p.name for p in (ROOT / "services").iterdir() if p.is_dir()}
    declared = {s["config"]["run_directory"].split("/")[-1] for s in config["stack"]}

    for name in sorted(on_disk - declared):
        errors.append(f"services/{name} has no [[stack]] entry in komodo.toml")
    for name in sorted(declared - on_disk):
        errors.append(f"stack run_directory services/{name} does not exist")

    workflow = ROOT / ".github/workflows/validate.yml"
    matrix = re.search(r"stack: \[(.*?)\]", workflow.read_text())
    if not matrix:
        return errors + ["cannot find the stack matrix in validate.yml"]

    in_ci = {name.strip() for name in matrix.group(1).split(",")}
    for name in sorted(on_disk - in_ci):
        errors.append(f"services/{name} is missing from the validate.yml matrix")

    return errors


def main() -> int:
    raw = KOMODO_TOML.read_text()
    try:
        config = tomllib.loads(raw)
    except tomllib.TOMLDecodeError as exc:
        print(f"error: komodo.toml is not valid TOML: {exc}")
        return 1

    variables = {v["name"] for v in config.get("variable", [])}
    secrets = documented_secrets()
    referenced = set(PLACEHOLDER.findall(raw))

    errors: list[str] = []

    for name in sorted(referenced - variables - secrets):
        errors.append(
            f"[[{name}]] is referenced but is neither a [[variable]] "
            f"nor a secret documented in README.md"
        )

    for variable in config.get("variable", []):
        if variable.get("is_secret"):
            errors.append(
                f"{variable['name']} is marked is_secret; secrets belong in "
                f"Core config [secrets], not in komodo.toml"
            )

    for name in sorted(variables - referenced):
        errors.append(f"[[{name}]] is defined but never referenced")

    errors.extend(check_stack_coverage(config))

    for error in errors:
        print(f"error: {error}")

    print(
        f"checked {len(referenced)} placeholders, {len(variables)} variables, "
        f"{len(secrets)} documented secrets"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
