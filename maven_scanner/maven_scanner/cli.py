import click
from maven_scanner.scanner import MavenScanner
from tabulate import tabulate
import os
import csv
import subprocess

@click.group()
def cli():
    pass


@cli.command()
@click.option('-r', '--repo-local-path', help='Path to Maven repository, default: ~/.m2/repository')
@click.option('-d', '--debug', is_flag=True, help='Enable debug mode to suppress exceptions and error messages.')
def scan(local_repo_dir, debug):
    scanner = scan_repo(local_repo_dir, debug)
    click.echo(f"Number of JAR and ZIP directories found: {len(scanner.jar_dir_dict)}")
    click.echo(f"Number of errors encountered: {scanner.error_counter}")


@cli.command()
@click.option('-r', '--local-repo-dir', help='Path to Maven repository, default: ~/.m2/repository')
@click.option('-t', '--output-type', default='stdout', help='Output type: stdout, csv')
@click.option('-o', '--output-file', default='.', help='Path to output file. by default, current directory.')
@click.option('-f', '--filter-repo', default='all', help='Include only dependencies from this repo. Can be set with '
                                                         'wildcard.')
@click.option('-fn', '--filter-filename', default='all', help='Include only dependencies with this filename. '
                                                              'Can be set with wildcard.')
@click.option('-d', '--deploy', default=None, help='Deploy listed dependencies to the specified repository: '
                                                   'You need to pass info in the form of: "repositoryId,repositoryUrl"')
@click.option('--debug', is_flag=True, help='Enable debug mode to suppress exceptions and error messages.')
def list_dependencies(local_repo_dir, output_type, output_file, filter_repo, filter_filename, debug, deploy):
    scanner = scan_repo(local_repo_dir, debug)

    dependencies = filter_dependencies(scanner, filter_repo, filter_filename)

    if deploy:
        dst_repo_id, dst_repo_url = deploy.split(',')
        deploy_dependencies(dependencies, dst_repo_id, dst_repo_url)
    elif output_type == 'stdout':
        print_dependencies(dependencies)
    elif output_type == 'csv':
        save_to_csv(dependencies, output_file)


def scan_repo(local_repo_dir, debug):
    scanner = MavenScanner(debug)
    if local_repo_dir:
        scanner.scan_maven_repo_for_dependencies(local_repo_dir)
    else:
        scanner.scan_maven_repo_for_dependencies(os.path.join(os.path.expanduser("~"), ".m2", "repository"))
    return scanner


def filter_dependencies(scanner, filter_repo, filter_filename):
    dependencies = []
    for filename, dir_path in scanner.jar_dir_dict.items():
        pom_data = scanner.parse_pom_file(dir_path)
        if pom_data:
            last_update_data = scanner.parse_last_updated_file(dir_path)
            repo_url = last_update_data['repository_url'] if last_update_data else ""
            update_date = last_update_data['update_date'] if last_update_data else ""
            if (filter_repo == 'all' or filter_repo in repo_url) and (filter_filename == 'all' or filter_filename in filename):
                dependencies.append({
                    'groupId': pom_data['groupId'],
                    'artifactId': pom_data['artifactId'],
                    'version': pom_data['version'],
                    'repository_url': repo_url,
                    'last_update': update_date,
                    'filename': filename,
                    'file_path': os.path.join(dir_path, filename)
                })
    return dependencies


def print_dependencies(dependencies):
    if dependencies:
        headers = ['GroupID', 'ArtifactID', 'Version', 'RepositoryURL', 'LastUpdate', 'FileName', 'FilePath']
        table = [[d['groupId'], d['artifactId'], d['version'], d['repository_url'], d['last_update'], d['filename'], d['file_path']] for d in dependencies]
        print(tabulate(table, headers=headers, tablefmt="plain"))
    else:
        print("No dependencies found.")


def save_to_csv(dependencies, output_file):
    if dependencies:
        output_file_path = os.path.join(output_file, 'dependencies.csv')
        try:
            with open(output_file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Sep=,'])
                writer.writerow(['GroupID', 'ArtifactID', 'Version', 'RepositoryURL', 'LastUpdate', 'FileName', 'FilePath'])
                for dependency in dependencies:
                    writer.writerow([dependency['groupId'], dependency['artifactId'], dependency['version'],
                                     dependency['repository_url'], dependency['last_update'],
                                     dependency['filename'], dependency['file_path']])
            print(f"Dependencies list exported to {output_file_path}")
        except Exception as e:
            print(f"Error saving file {output_file_path}: {e}")
    else:
        print("No dependencies found.")


def deploy_dependencies(dependencies, dst_repository_id, dst_repository_url):

    # Check if Maven is installed
    result = os.system(f"mvn --version")
    if result != 0:
        print("Maven is not installed or not available in the system.")
        return

    if dependencies:
        print("The following dependencies will be deployed:")
        print_dependencies(dependencies)
        if input("Do you want to deploy these dependencies? (y/n): ").lower() == 'y':
            for dependency in dependencies:
                group_id = dependency['groupId']
                artifact_id = dependency['artifactId']
                version = dependency['version']
                file_path = dependency['file_path']
                print(f"\nDeploying {dependency['filename']} to repository ID: {dst_repository_id}\n")
                # Execute deployment command using os.system
                deploy_command = f"mvn deploy:deploy-file -DgroupId={group_id} -DartifactId={artifact_id} " \
                                 f"-Dversion={version} -Dpackaging=jar -Dfile={file_path} " \
                                 f"-DrepositoryId={dst_repository_id} -Durl={dst_repository_url} " \
                                 f"-DgeneratePom=true"
                print(deploy_command)
                # Execute deployment command using os.system
                result = os.system(deploy_command)
                if result != 0:
                    print(f"\nError deploying {dependency['filename']}. Command exited with status {result}\n")
                else:
                    print(f"\nDeployed {dependency['filename']} to repository ID: {dst_repository_id}\n")
    else:
        print("No dependencies found to deploy.")


if __name__ == '__main__':
    cli()
