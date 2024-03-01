#!/usr/bin/env python

"""Tests for `maven_scanner` package."""

import unittest
import os
import tempfile
from maven_scanner.scanner import MavenScanner
from unittest.mock import patch


class TestMavenScanner(unittest.TestCase):
    """Tests for `maven_scanner` package."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def setUp(self):
        self.scanner = MavenScanner()

    def test_get_maven_repo_path(self):
        self.assertEqual(self.scanner.get_maven_repo_path(), os.path.join(os.path.expanduser("~"), ".m2", "repository"))

    def test_scan_maven_repo_for_jar_zip(self):
        # Test scan_maven_repo method
        self.scanner.scan_maven_repo_for_dependencies('dir/')
        print(self.scanner.jar_dir_dict)
        self.assertTrue(self.scanner.jar_dir_dict)  # Ensure jar_dir_dict is not empty

    def test_parse_pom_file(self):
        result = self.scanner.parse_pom_file('dir/test-jar')
        print(result)
        # Ensure the result dictionary contains expected keys and values
        self.assertEqual(result['groupId'], 'xom')
        self.assertEqual(result['artifactId'], 'xom.project')
        self.assertEqual(result['version'], '1.3.7')

    def test_parse_pom_file_exception(self):
        # Test parse_pom_file method when an exception occurs
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('maven_scanner.scanner.ET.parse') as mock_parse:
                mock_parse.side_effect = Exception('Test exception')
                result = self.scanner.parse_pom_file(temp_dir)
            self.assertIsNone(result)  # Ensure None is returned when an exception occurs

    def test_parse_pom_file_no_file(self):
        result = self.scanner.parse_pom_file('dir/test-no-pom')
        self.assertIsNone(result)

    def test_parse_lastUpdate_file(self):
        result = self.scanner.parse_last_updated_file('dir/test-lastUpdated')
        print(result)
        # Ensure the result dictionary contains expected keys and values
        self.assertEqual(result['repository_url'], 'https\\://example2.com/repository/Public_Repositories_Releases/')
        self.assertEqual(result['update_date'], '2023-11-30 16:19:49')

    def test_parse_lastUpdate_file_no_file(self):
        result = self.scanner.parse_last_updated_file('dir/test-no-pom')
        self.assertIsNone(result)

    def test_parse_lastUpdate_file_exception(self):
        # Test parse_pom_file method when an exception occurs
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('maven_scanner.scanner.re.finditer') as mock_finditer:
                mock_finditer.side_effect = Exception('Test exception')
                result = self.scanner.parse_last_updated_file(temp_dir)
            self.assertIsNone(result)  # Ensure None is returned when an exception occurs

    def test_deploy_to_server(self):
        pass
