import click
from maven_scanner.scanner import MavenScanner
from tabulate import tabulate
import os
import csv


@click.group()
def cli():
    pass


@cli.command()
@click.option('-r', '--repo-path', help='Path to Maven repository, default: ~/.m2/repository')
@click.option('-d', '--debug', is_flag=True, help='Enable debug mode to suppress exceptions and error messages.')
def scan(repo_path, debug):
    scanner = scan_repo(repo_path, debug)
    if debug:
        # print(scanner.jar_dir_dict)
        click.echo(f"Number of JAR and ZIP directories found: {len(scanner.jar_dir_dict)}")
        click.echo(f"Number of errors encountered: {scanner.error_counter}")


@cli.command()
@click.option('-r', '--repo-path', help='Path to Maven repository, default: ~/.m2/repository')
@click.option('-t', '--output-type', default='stdout', help='Output type: stdout, csv')
@click.option('-o', '--output-file', default='.', help='Path to output file. by default, current directory.')
@click.option('-d', '--debug', is_flag=True, help='Enable debug mode to suppress exceptions and error messages.')
@click.option('-f', '--filter-repo', default='all', help='Include only dependencies from this repo. Can be set with '
                                                         'wildcard.')
def list_dependencies(repo_path, output_type, output_file, filter_repo, debug):
    scanner = scan_repo(repo_path, debug)

    if output_type == 'stdout':
        table = []
        for filename, dir_path in scanner.jar_dir_dict.items():
            pom_data = scanner.parse_pom_file(dir_path)
            if pom_data:
                last_update_data = scanner.parse_last_updated_file(dir_path)
                repo_url = last_update_data['repository_url'] if last_update_data else None
                update_date = last_update_data['update_date'] if last_update_data else None
                if filter_repo == 'all' or filter_repo in repo_url:
                    table.append([
                        pom_data['groupId'],
                        pom_data['artifactId'],
                        pom_data['version'],
                        repo_url,
                        update_date,
                        filename,
                        os.path.join(dir_path, filename)
                    ])
        if table:
            headers = ['GroupID', 'ArtifactID', 'Version', 'RepositoryURL', 'LastUpdate', 'FileName', 'FilePath']
            click.echo(tabulate(table, headers=headers, tablefmt="plain"))
        else:
            click.echo("No dependencies found.")

    elif output_type == 'csv':
        output_file_path = os.path.join(output_file, 'dependencies.csv')
        try:
            with open(output_file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Sep=,'])
                writer.writerow(['GroupID', 'ArtifactID', 'Version', 'RepositoryURL', 'LastUpdate', 'FileName', 'FilePath'])
                for filename, dir_path in scanner.jar_dir_dict.items():
                    pom_data = scanner.parse_pom_file(dir_path)
                    if pom_data:
                        last_update_data = scanner.parse_last_updated_file(dir_path)
                        repo_url = last_update_data['repository_url'] if last_update_data else ""
                        update_date = last_update_data['update_date'] if last_update_data else ""
                        if filter_repo == 'all' or filter_repo in repo_url:
                            writer.writerow([pom_data['groupId'], pom_data['artifactId'], pom_data['version'],
                                             repo_url, update_date, filename, os.path.join(dir_path, filename)])
            click.echo(f"Dependencies list exported to {output_file_path}")
        except Exception as e:
            print(f"Error saving file {output_file_path}: {e}")


def scan_repo(repo_path, debug):
    scanner = MavenScanner(debug)
    if repo_path:
        scanner.scan_maven_repo_for_dependencies(repo_path)
    else:
        scanner.scan_maven_repo_for_dependencies(os.path.join(os.path.expanduser("~"), ".m2", "repository"))

    return scanner

if __name__ == '__main__':
    cli()
