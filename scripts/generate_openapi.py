#!/usr/bin/env python3
"""Generate an OpenAPI 3.0.3 spec for the PurpleAir API from its apiDoc data.

PurpleAir does not publish an OpenAPI/Swagger document. Its docs at
https://api.purpleair.com/ are generated with apiDoc (https://apidocjs.com/),
which serves machine-readable data at ``/api_data.js`` and ``/api_project.js``.
This script fetches those files and reconstructs an OpenAPI spec, so the
reference can be regenerated whenever the API changes with no browser step.

The apiDoc build version (``api_project.js`` ``version``, repeated on every
entry) lags the real REST API version, which is published only as a changelog
in the ``welcome`` doc-block. This script takes the real version as the highest
semver found in that changelog and records the build version separately.

Usage::

    python scripts/generate_openapi.py [--host https://api.purpleair.com]
        [--out docs/purpleair-openapi.yaml]
        [--data path/to/api_data.js] [--project path/to/api_project.js]

``--data``/``--project`` read cached local files instead of fetching, for CI
or offline runs.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request

BASE_URL = "https://api.purpleair.com/v1"

TYPE_MAP = {
    "string": "string",
    "number": "number",
    "integer": "integer",
    "int": "integer",
    "long": "integer",
    "boolean": "boolean",
    "bool": "boolean",
    "object": "object",
    "array": "array",
}


def fetch(url: str) -> str:
    """Fetch a URL and return its text body."""
    req = urllib.request.Request(url, headers={"User-Agent": "aiopurpleair-openapi-generator"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8")


def read_text(path: str) -> str:
    """Read a local file's text."""
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def parse_apidoc(text: str) -> object:
    """Parse an apiDoc ``define(<json>);`` file into a Python object."""
    body = re.sub(r"^\s*define\(", "", text.strip())
    body = re.sub(r"\)\s*;?\s*$", "", body)
    return json.loads(body)


def clean(value: str | None) -> str:
    """Strip HTML tags and unescape entities (``&#46;`` -> ``.``)."""
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", "", value)
    return " ".join(html.unescape(text).split()).strip()


def schema_type(apidoc_type: str | None) -> str:
    """Map an apiDoc type string to an OpenAPI schema type."""
    if not apidoc_type:
        return "string"
    return TYPE_MAP.get(apidoc_type.strip().lower().split("[")[0], "string")


def extract_versions(api: list[dict], project: object) -> tuple[str, str]:
    """Return ``(api_version, build_version)``.

    ``api_version`` is the highest semver in the ``welcome`` changelog;
    ``build_version`` is the (lagging) apiDoc metadata version.
    """
    build_version = ""
    if isinstance(project, dict):
        build_version = str(project.get("version", ""))
    found: set[tuple[int, ...]] = set()
    for entry in api:
        group = (entry.get("group", "") + entry.get("name", "")).lower()
        if "welcome" in group:
            for match in re.findall(r"\b(\d+\.\d+\.\d+)\b", json.dumps(entry)):
                found.add(tuple(int(part) for part in match.split(".")))
    api_version = ".".join(map(str, max(found))) if found else (build_version or "0.0.0")
    return api_version, build_version


def build_spec(api: list[dict], project: object) -> dict:
    """Reconstruct an OpenAPI 3.0.3 spec dict from apiDoc entries."""
    api_version, build_version = extract_versions(api, project)
    field_catalog: dict[str, str] = {}
    error_codes: dict[str, str] = {}
    paths: dict[str, dict] = {}

    for entry in api:
        method = (entry.get("type") or "").strip().lower()
        url = (entry.get("url") or "").strip()
        # Skip doc-block artifacts (no method/url) and the welcome group's
        # duplicate example endpoints (real endpoints live in their own groups).
        if not method or not url or entry.get("group") == "welcome":
            continue

        oa_path = re.sub(r":(\w+)", r"{\1}", url)
        path_params = set(re.findall(r"\{(\w+)\}", oa_path))

        parameters: list[dict] = []
        body_props: dict[str, dict] = {}
        # apiDoc repeats shared params (e.g. the path id) across a POST's
        # mutually-exclusive body variants, so dedupe by (location, name).
        seen: set[tuple[str, str]] = set()
        for fields in (entry.get("parameter") or {}).get("fields", {}).values():
            for field in fields:
                name = clean(field.get("field"))
                if not name or name == "-":
                    continue
                desc = clean(field.get("description"))
                typ = schema_type(field.get("type"))
                required = not field.get("optional", False)
                if name in path_params:
                    if ("path", name) in seen:
                        continue
                    seen.add(("path", name))
                    parameters.append(
                        {"name": name, "in": "path", "required": True, "description": desc, "schema": {"type": typ}}
                    )
                elif method == "get":
                    if ("query", name) in seen:
                        continue
                    seen.add(("query", name))
                    param = {"name": name, "in": "query", "description": desc, "schema": {"type": typ}}
                    if required:
                        param["required"] = True
                    parameters.append(param)
                elif name not in body_props:
                    body_props[name] = {"type": typ, "description": desc}

        responses: dict[str, dict] = {}
        for group, fields in (entry.get("success") or {}).get("fields", {}).items():
            if "sensor data field" in group.lower():
                for field in fields:
                    field_catalog.setdefault(clean(field.get("field")), clean(field.get("description")))
                continue
            code_match = re.search(r"(\d{3})", group)
            code = code_match.group(1) if code_match else "200"
            schema = responses.setdefault(
                code,
                {
                    "description": clean(group) or "Success",
                    "content": {"application/json": {"schema": {"type": "object", "properties": {}}}},
                },
            )["content"]["application/json"]["schema"]["properties"]
            for field in fields:
                name = clean(field.get("field"))
                if name and name != "-":
                    schema[name] = {
                        "type": schema_type(field.get("type")),
                        "description": clean(field.get("description")),
                    }

        for fields in (entry.get("error") or {}).get("fields", {}).values():
            for field in fields:
                name = clean(field.get("field"))
                if name and name != "-":
                    error_codes.setdefault(name, clean(field.get("description")))

        if not responses:
            responses["200"] = {"description": "Success"}
        responses["4XX"] = {
            "description": "Error response with a PurpleAir error code",
            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}},
        }

        operation: dict = {
            "operationId": clean(entry.get("name")),
            "summary": clean(entry.get("title")),
            "description": clean(entry.get("description")),
            "tags": [entry.get("group", "")],
        }
        if parameters:
            operation["parameters"] = parameters
        if body_props:
            operation["requestBody"] = {
                "content": {"application/json": {"schema": {"type": "object", "properties": body_props}}}
            }
        operation["responses"] = {key: responses[key] for key in sorted(responses)}
        operation = {key: value for key, value in operation.items() if value not in (None, "", [])}
        paths.setdefault(oa_path, {})[method] = operation

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "PurpleAir API (Unofficial OpenAPI Reconstruction)",
            "version": api_version,
            "description": (
                "Unofficial OpenAPI spec reconstructed from PurpleAir's apiDoc data at /api_data.js. "
                f"REST API changelog version {api_version}; apiDoc build-metadata version "
                f"{build_version or 'unknown'} lags and is not used. Generated by "
                "scripts/generate_openapi.py."
            ),
        },
        "servers": [{"url": BASE_URL}],
        "security": [{"ApiKeyHeader": []}],
        "paths": dict(sorted(paths.items())),
        "components": {
            "securitySchemes": {"ApiKeyHeader": {"type": "apiKey", "in": "header", "name": "X-API-Key"}},
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "enum": sorted(error_codes)},
                        "description": {"type": "string"},
                    },
                },
                "SensorDataFields": {
                    "type": "object",
                    "description": "Catalog of PurpleAir sensor data fields (the `fields` query parameter values).",
                    "properties": {
                        name: {"type": "string", "description": desc}
                        for name, desc in sorted(field_catalog.items())
                        if name
                    },
                },
            },
        },
    }


def main() -> int:
    """Fetch/parse apiDoc data, build the spec, write it, and validate."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="https://api.purpleair.com", help="docs host serving api_data.js")
    parser.add_argument("--out", default="docs/purpleair-openapi.yaml", help="output spec path")
    parser.add_argument("--data", help="cached api_data.js path (skip fetch)")
    parser.add_argument("--project", help="cached api_project.js path (skip fetch)")
    args = parser.parse_args()

    data_text = read_text(args.data) if args.data else fetch(f"{args.host}/api_data.js")
    project_text = read_text(args.project) if args.project else fetch(f"{args.host}/api_project.js")
    api = parse_apidoc(data_text)["api"]
    project = parse_apidoc(project_text)

    spec = build_spec(api, project)

    out_path = args.out
    try:
        import yaml

        rendered = yaml.safe_dump(spec, sort_keys=False, width=100, allow_unicode=True)
    except ImportError:
        out_path = out_path.rsplit(".", 1)[0] + ".json"
        rendered = json.dumps(spec, indent=2)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write(rendered)

    print(
        f"Wrote {out_path}: version={spec['info']['version']} "
        f"paths={len(spec['paths'])} "
        f"errors={len(spec['components']['schemas']['Error']['properties']['error']['enum'])} "
        f"fields={len(spec['components']['schemas']['SensorDataFields']['properties'])}"
    )

    try:
        from openapi_spec_validator import validate

        validate(spec)
        print("OpenAPI spec is valid.")
    except ImportError:
        print("(openapi-spec-validator not installed; skipped validation)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
