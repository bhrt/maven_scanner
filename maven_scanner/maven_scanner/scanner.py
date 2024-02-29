"""Main module."""
import re
from datetime import datetime
import os
import xml.etree.ElementTree as ET


class MavenScanner:
    def __init__(self, debug='True'):
        self.debug = debug
        self.error_counter = 0
        self.jar_dir_dict = {}
        self.maven_repo_path = os.path.join(os.path.expanduser("~"), ".m2", "repository")

    def get_maven_repo_path(self):
        return self.maven_repo_path

    def scan_maven_repo_for_dependencies(self, maven_repo_path):
        """
        Scan the Maven local repository and initialize jar_dir_list with directories where JAR files are stored.
        """
        self.error_counter = 0

        if not os.path.exists(maven_repo_path):
            self.error_counter += 1
            raise FileNotFoundError("Maven repository path does not exist.")

        # Traverse the Maven repository directory
        for root, dirs, files in os.walk(maven_repo_path):
            for jar_dir in dirs:
                dir_full_path = os.path.join(root, jar_dir)
                for file in os.listdir(dir_full_path):
                    if file.endswith('.jar') or file.endswith('.zip'):
                        self.jar_dir_dict[file] = dir_full_path

    def parse_pom_file(self, dir_path):
        """
        Parse the <dependencyname>.pom file in the given directory and retrieve groupId, artifactId, and version.
        """
        pom_file_path = None
        # Find the .pom file corresponding to the JAR or ZIP
        for file in os.listdir(dir_path):
            if file.endswith('.pom'):
                pom_file_path = os.path.join(dir_path, file)
                break

        if not pom_file_path:
            self.error_counter += 1
            if self.debug:
                print(f"No .pom file found in directory: {dir_path}")
            return None

        try:
            tree = ET.parse(pom_file_path)
            root = tree.getroot()

            # Extracting groupId, artifactId, and version from the pom file
            namespaces = {
                '': '',
                'ns': 'http://maven.apache.org/POM/4.0.0'
            }

            ns_prefix = "ns:" if root.tag.split('}')[0][1:] == 'http://maven.apache.org/POM/4.0.0' else ""

            project_group_id_element = root.findall('./{ns}groupId'.format(ns=ns_prefix), namespaces)
            project_artifact_id_element = root.findall('./{ns}artifactId'.format(ns=ns_prefix), namespaces)
            project_version_element = root.findall('./{ns}version'.format(ns=ns_prefix), namespaces)

            parent_group_id_element = root.findall('.//{ns}parent/{ns}groupId'.format(ns=ns_prefix), namespaces)
            parent_artifact_id_element = root.findall('.//{ns}parent/{ns}artifactId'.format(ns=ns_prefix), namespaces)
            parent_version_element = root.findall('.//{ns}parent/{ns}version'.format(ns=ns_prefix), namespaces)

            group_id = project_group_id_element.pop().text if len(
                project_group_id_element) != 0 else parent_group_id_element.pop().text
            artifact_id = project_artifact_id_element.pop().text if len(
                project_artifact_id_element) != 0 else parent_artifact_id_element.pop().text
            version = project_version_element.pop().text if len(
                project_version_element) != 0 else parent_version_element.pop().text

            return {
                'groupId': group_id,
                'artifactId': artifact_id,
                'version': version
            }
        except Exception as e:
            self.error_counter += 1
            if self.debug:
                print(f"Error parsing pom file {pom_file_path}: {e}")
            return None

    def parse_last_updated_file(self, dir_path):
        """
        Parse the <artefactName>.lastUpdated file in the given directory and extract repository URL
        of the latest successful update along with its timestamp/date.
        """
        last_updated_file_path = None
        filename = ""
        # Find the .pom file corresponding to the JAR
        for file in os.listdir(dir_path):
            if file.endswith('.lastUpdated'):
                filename = file
                last_updated_file_path = os.path.join(dir_path, file)
                break

        if not last_updated_file_path:
            self.error_counter += 1
            if self.debug:
                print(f"No .lastUpdated file found in directory: {dir_path}")
            return None

        try:
            with open(last_updated_file_path, 'r') as file:
                content = file.read()

            # Extracting repository URL and timestamp/date using named groups
            pattern = r'(?P<repo_url>.+?).lastUpdated=(?P<last_updated>\d+)'
            matches = re.finditer(pattern, content)

            latest_update = max(matches, key=lambda match: int(match.group('last_updated')))

            repository_url = latest_update.group('repo_url')
            timestamp = int(latest_update.group('last_updated')) // 1000  # Convert milliseconds to seconds
            update_date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

            return {
                'repository_url': repository_url,
                'update_date': update_date
            }
        except Exception as e:
            if self.debug:
                print(f"Error parsing lastUpdated file {last_updated_file_path}: {e}")
            return None


# Example usage:
if __name__ == "__main__":
    scanner = MavenScanner()
    scanner.scan_maven_repo_for_dependencies(scanner.get_maven_repo_path())

    incomplete_data_count = 0  # Initialize counter for incomplete data
    jars_with_problems = []  # Initialize list to store paths of JAR files with problems

    empty_entries_count = 0

    for dir_path in scanner.jar_dir_list:
        pom_data = scanner.parse_pom_file(dir_path)
        if pom_data:
            print("Directory:", dir_path)
            print("POM Data:", pom_data)
            print()
            if None in pom_data.values():
                empty_entries_count += 1

    print(f"Various parse errors: {scanner.error_counter}: empty entries: {empty_entries_count}")
