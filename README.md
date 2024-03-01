# Scan local maven repository and list all cached dependencies

## Installation
clone repository:
execute:
`pip install -e ./maven_scanner/`

run tool:

`mvn-scn list-dependencies --help`
eg. 
`mvn-scn list-dependencies -t csv -f example.com`
list dependencies downloaded from server example.com and place it in a csv file.

`mvn-scn list-dependencies`
list all local dependencies and print them to stdout

credentials and repository local_snapshots have to be configured in settings.xml 

`mvn-scn list-dependencies -fn "example-SNAPSHOT.jar" --deploy "local_snapshots,http://localhost:8081/repository/maven-snapshots"`
