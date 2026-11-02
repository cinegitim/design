"""Brandstudio portable contract schema tests (test-first)."""
import json
import sys
import unittest
from pathlib import Path

PRODUCTION = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCTION))
FIXTURES = PRODUCTION / "tests" / "fixtures" / "contracts"


class ContractSchemaTests(unittest.TestCase):
    def test_all_schema_files_conform_to_draft_2020_12(self):
        from contracts import SCHEMA_PATHS
        from jsonschema import Draft202012Validator
        self.assertEqual(set(SCHEMA_PATHS), {
            "task", "capability-report", "task-receipt", "output-manifest"
        })
        for path in SCHEMA_PATHS.values():
            with self.subTest(path=str(path)):
                schema = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertFalse(schema["additionalProperties"])
                Draft202012Validator.check_schema(schema)

    def test_all_fixture_documents_validate(self):
        from contracts import SCHEMA_PATHS
        from jsonschema import Draft202012Validator, FormatChecker
        for filename, kind in (
            ("task-valid.json", "task"),
            ("capability-opencode.json", "capability-report"),
            ("capability-work.json", "capability-report"),
            ("receipt-valid.json", "task-receipt"),
            ("manifest-prepared.json", "output-manifest"),
        ):
            with self.subTest(filename=filename):
                schema = json.loads(SCHEMA_PATHS[kind].read_text(encoding="utf-8"))
                fixture = json.loads((FIXTURES / filename).read_text(encoding="utf-8"))
                Draft202012Validator(schema, format_checker=FormatChecker()).validate(fixture)

    def test_extra_fields_wrong_version_and_missing_evidence_rejected(self):
        from contracts import SCHEMA_PATHS
        from jsonschema import Draft202012Validator, ValidationError
        schema = json.loads(SCHEMA_PATHS["task"].read_text(encoding="utf-8"))
        fixture = json.loads((FIXTURES / "task-valid.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        for mutate in (
            {"schema_version": 99},
            {"sneaky_token": "not-allowed"},
            {"required_capabilities": []},
            {"base_sha": "main"},
        ):
            with self.subTest(mutate=mutate), self.assertRaises(ValidationError):
                validator.validate(fixture | mutate)

    def test_prepared_manifest_requires_render_and_editable_source(self):
        from contracts import SCHEMA_PATHS
        from jsonschema import Draft202012Validator, ValidationError
        schema = json.loads(SCHEMA_PATHS["output-manifest"].read_text(encoding="utf-8"))
        doc = json.loads((FIXTURES / "manifest-prepared.json").read_text(encoding="utf-8"))
        for missing in ("renders", "editable_sources"):
            with self.subTest(missing=missing), self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(doc | {missing: []})

    def test_accepted_manifest_requires_human_reference(self):
        from contracts import SCHEMA_PATHS
        from jsonschema import Draft202012Validator, ValidationError
        schema = json.loads(SCHEMA_PATHS["output-manifest"].read_text(encoding="utf-8"))
        doc = json.loads((FIXTURES / "manifest-prepared.json").read_text(encoding="utf-8"))
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(doc | {"status": "accepted"})
