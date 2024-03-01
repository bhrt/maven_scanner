# Nexus installation:
## [Official nexus installation](https://hub.docker.com/r/sonatype/nexus3) 

### create persistance directory.

`mkdir /some/dir/nexus-data && chown -R 200 /some/dir/nexus-data`

### start dockerized nexus server on port `8081`

`docker run -d -p 8081:8081 --name nexus -v /some/dir/nexus-data:/nexus-data -e I0NSTALL4J_ADD_VM_PARAMS="-Xms2703m -Xmx2703m -XX:MaxDirectMemorySize=2703m" sonatype/nexus3`

## Access docker persistance directory to get temporary generated admin password

### Log into 'admin' account

`cat /some/dir/nexus-data/admin.password`

### Create role to allow user to deploy artefacts to:

eg. name `nx-deploy-artefact` add Privilages like:

`nx-repository-view-maven2-maven-releases-add`, `nx-repository-view-maven2-maven-releases-edit`,  `nx-repository-view-maven2-maven-releases-read`.

`nx-repository-view-maven2-maven-snapshots-add`, `nx-repository-view-maven2-maven-snapshots-edit`, `nx-repository-view-maven2-maven-snapshots-read`

### Create service account to use (eg. `nexus_user`) as deployment user. And add `nx-deploy-artefact` role to it.

### Configure local maven to access new server.

Add repository to ~/.m2/settings.xml file
```
(...)
<servers xmlns="http://maven.apache.org/SETTINGS/1.1.0">
  <server>
    <username>nexus_user</username>
    <password>hard_pasword</password>
    <id>local_snapshots</id>
  </server>
  <server>
    <username>nexus_user</username>
    <password>hard_pasword</password>
    <id>local_releases</id>
  </server>
</servers>
(...)
<repositories>
  <repository>
    <!-- releases local repository -->
    <id>local_releases</id>
    <url>http://localhost:8081/repository/maven-releases</url>
    <name>local release repository</name>
    <releases>
      <enabled>true</enabled>
      <updatePolicy>daily</updatePolicy>
    </releases>
  </repository>
  <repository>
    <!-- snapshots local repository -->
    <id>local_snapshots</id>
    <name>local snapshot repository</name>
    <url>http://localhost:8081/repository/maven-snapshots</url>
    <snapshots>
      <enabled>true</enabled>
      <updatePolicy>daily</updatePolicy>
    </snapshots>
  </repository>
</repositories>
(...)
```




deploy artefact to the server "by hand"

`mvn deploy:deploy-file -DrepositoryId="local_snapshots" -Durl="http://localhost:8081/repository/maven-snapshots" -Dfile="xom-1.0.jar" -DgroupId="org.nanohttpd" -DartifactId="nanohttpd" -Dversion="2.3.2-SNAPSHOT" -Dpackaging="jar" -DgeneratePom=true`