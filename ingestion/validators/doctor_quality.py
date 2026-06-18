from __future__ import annotations

from collections import defaultdict
from typing import Iterable


def cross_country_pcode_collisions(rows: Iterable[dict[str, object]]) -> dict[str, list[str]]:
    countries_by_pcode: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        pcode = row.get("pcode_normalized")
        country = row.get("country")
        if pcode and country:
            countries_by_pcode[str(pcode)].add(str(country))
    return {
        pcode: sorted(countries)
        for pcode, countries in countries_by_pcode.items()
        if len(countries) > 1
    }


def same_country_doctor_conflicts(rows: Iterable[dict[str, object]]) -> dict[tuple[str, str], list[str]]:
    names_by_key: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        pcode = row.get("pcode_normalized")
        country = row.get("country")
        name = row.get("doctor_name")
        if pcode and country and name:
            names_by_key[(str(country), str(pcode))].add(str(name).strip())
    return {
        key: sorted(names)
        for key, names in names_by_key.items()
        if len(names) > 1
    }
