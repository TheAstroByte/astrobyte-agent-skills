from __future__ import annotations

import copy
import unittest

from scripts import install
from scripts.profile import find_machine, load_operator, validate_operator


class OperatorProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = install.load_json(install.CATALOG_PATH)
        self.profile, self.registry, self.directory = load_operator(install.REPO_ROOT, "astrobyte")

    def test_astrobyte_profile_is_valid(self) -> None:
        self.assertEqual(validate_operator(self.profile, self.registry, self.directory, self.catalog), [])

    def test_machine_lookup_uses_the_supplied_registry(self) -> None:
        registry = {
            "machines": [
                {"alias": "development", "default_delivery_mode": "durable"},
                {"alias": "release", "production_capable": True},
            ]
        }

        self.assertEqual(find_machine(registry, "development")["default_delivery_mode"], "durable")
        self.assertTrue(find_machine(registry, "release")["production_capable"])
        self.assertIsNone(find_machine(registry, "missing"))

    def test_required_production_machine_is_enforced(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["machine_policy"]["require_production_capable"] = True
        registry = copy.deepcopy(self.registry)
        for machine in registry["machines"]:
            machine["production_capable"] = False

        errors = validate_operator(profile, registry, self.directory, self.catalog)

        self.assertIn("machine policy requires at least one production-capable machine", errors)

    def test_profile_file_references_cannot_escape_profile_directory(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["working_agreement"] = "../../README.md"

        errors = validate_operator(profile, self.registry, self.directory, self.catalog)

        self.assertIn("working_agreement must name a file in the operator profile directory", errors)


if __name__ == "__main__":
    unittest.main()
