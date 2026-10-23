"""Patch a fair2.json of the newer FAIR² export structure into valid Croissant: a stopgap for the
notebooks, demos and tests.

In a notebook, instead of `mlc.Dataset(croissant_url)`:

    from patch_fair2 import load_dataset
    dataset = load_dataset(croissant_url)

load_dataset() reads the fair2.json as published, and patches it only if mlcroissant can't read it.
From the command line, to write a patched copy:

    python tools/patch_fair2.py <fair2.json URL or path> <output path>

The newer export can't be read by mlcroissant.
The patch only adds or corrects, it removes nothing:

- `@context`: a list holding one map becomes that map, with `@language` (required by mlcroissant,
  mlcommons/croissant#950) and the schema.org data types it doesn't define (e.g. DateTime; String,
  which isn't one, as Text).
- `id` becomes `@id` on record sets and fields, which get their `@type` (RecordSet, Field).
- `encodingFormat`: a charset ("utf-8") is replaced by the MIME type of the file's extension, or
  text/csv for a file without an extension based on a spreadsheet: the export writes each sheet as
  a CSV file. Other files without an extension keep their charset: their format isn't known.
- `source`: each field gets the file of its record set and its column. The file is the FileObject
  with the record set's name, or else the one whose path ends with it (in this export, the name is
  the file's path; a sheet of a spreadsheet can have the file name of another file): of an
  upload and its processed copy at the same URL, the copy (isBasedOn the upload). The column is
  the field's name. Names are compared and used decoded: they are written with %2F or +
  in some places ('First+cancer' is the column 'First cancer').

The fix belongs to the export itself; this is a stopgap until it is fixed.
"""

import json
import sys
import urllib.parse
import urllib.request

MIME_TYPES = {
    ".parquet": "application/x-parquet",
    ".csv": "text/csv",
    ".tsv": "text/tab-separated-values",
    ".json": "application/json",
    ".jsonl": "application/jsonl",
    ".ndjson": "application/jsonl",
}
SPREADSHEETS = (".xlsx", ".xls", ".ods")
SCHEMA_TYPES = ["Boolean", "Date", "DateTime", "Float", "Integer", "Text", "Time", "URL"]
# Data types of the export that aren't schema.org ones -> the schema.org type
OTHER_TYPES = {"String": "Text"}


def load(source):
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source) as response:
            return json.load(response)
    with open(source, encoding="utf-8") as f:
        return json.load(f)


def decoded(name):
    """A name or path as written, decoded: '%2F' and '+' become '/' and ' '."""
    return urllib.parse.unquote_plus(name or "")


def patch_context(metadata, changes):
    context = metadata["@context"]
    if isinstance(context, list):
        merged = {}
        for part in context:
            if not isinstance(part, dict):
                raise ValueError(f"remote contexts aren't supported: {part!r}")
            merged.update(part)
        context = merged
        changes.append(f"@context: list of {len(metadata['@context'])} map(s) merged into one map")
    if "@language" not in context:
        context["@language"] = "en"
        changes.append("@context: @language 'en' added")
    prefix = "schema" if "schema" in context else "sc"
    for type_ in SCHEMA_TYPES:
        if type_ not in context:
            context[type_] = {"@id": f"{prefix}:{type_}"}
            changes.append(f"@context: data type {type_} added")
    for type_, schema_type in OTHER_TYPES.items():
        if type_ not in context:
            context[type_] = {"@id": f"{prefix}:{schema_type}"}
            changes.append(f"@context: data type {type_} added, as {schema_type}")
    metadata["@context"] = context


def path_of(content_url):
    """The decoded path of a file URL, e.g. 'data/parquet/bp_visits.parquet'."""
    return decoded(urllib.parse.urlparse(content_url).path)


def patch_files(metadata, changes):
    files = {fo["@id"]: fo for fo in metadata.get("distribution", []) if "@id" in fo}
    for file_object in metadata.get("distribution", []):
        encoding_format = file_object.get("encodingFormat", "")
        if "/" not in encoding_format and file_object.get("contentUrl"):
            path = path_of(file_object["contentUrl"]).lower()
            mime = next((m for ext, m in MIME_TYPES.items() if path.endswith(ext)), None)
            # No extension, based on a spreadsheet: a sheet, which the export writes as CSV
            based_on = files.get((file_object.get("isBasedOn") or {}).get("@id"), {})
            if mime is None and decoded(based_on.get("name")).lower().endswith(SPREADSHEETS):
                mime = "text/csv"
            if mime:
                file_object["encodingFormat"] = mime
                changes.append(f"file {path.rsplit('/', 1)[-1]}: encodingFormat"
                               f" {encoding_format!r} -> {mime!r}")


def rename_id(node):
    if "id" in node and "@id" not in node:
        node["@id"] = node.pop("id")


def patch_record_sets(metadata, changes):
    files = [fo for fo in metadata.get("distribution", []) if fo.get("contentUrl")]
    for record_set in metadata.get("recordSet", []):
        rename_id(record_set)
        record_set.setdefault("@type", "RecordSet")
        name = record_set.get("name", "")
        # The file with the record set's name, or else the one whose path ends with it
        matches = [fo for fo in files if decoded(fo.get("name")) == decoded(name)] or [
            fo for fo in files
            if path_of(fo["contentUrl"]).endswith("/" + decoded(name).lstrip("/"))
        ]
        if len(matches) > 1:
            # The upload and its processed copy (isBasedOn the upload), at the same URL: the copy
            matches = [fo for fo in matches if "isBasedOn" in fo] or matches
        for field in record_set.get("field", []):
            rename_id(field)
            field.setdefault("@type", "Field")
            if "source" not in field and len(matches) == 1:
                field["source"] = {"fileObject": {"@id": matches[0]["@id"]},
                                   "extract": {"column": decoded(field["name"])}}
        changes.append(f"record set {name!r}: @id, @type and"
                       + (f" source of its {len(record_set.get('field', []))} fields"
                          if len(matches) == 1 else f" no source ({len(matches)} matching files)"))


def patch(metadata):
    """Patches the metadata in place, and returns the list of the changes."""
    changes = []
    patch_context(metadata, changes)
    patch_files(metadata, changes)
    patch_record_sets(metadata, changes)
    return changes


def load_dataset(source):
    """The mlcroissant dataset of a fair2.json (URL or path), patched only if it can't be read."""
    import mlcroissant as mlc

    try:
        return mlc.Dataset(source)
    except Exception as e:
        print(f"mlcroissant can't read the fair2.json as published ({type(e).__name__}):"
              " patching it")
    metadata = load(source)
    patch(metadata)
    return mlc.Dataset(jsonld=metadata)


def main():
    source, output = sys.argv[1:3]
    metadata = load(source)
    changes = patch(metadata)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"{output}: {len(changes)} changes")
    for change in changes:
        print("  -", change)


if __name__ == "__main__":
    main()
