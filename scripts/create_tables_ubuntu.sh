#!/bin/bash

## adding an error if there is no input to the script
if [ $# -ne 3 ]; then
echo $0: usage: myscript name $user $pass $db
exit 1
fi

userimp=$1
passimp=$2
db=$3

#install postgresql
#apt-get install postgresql
#sudo apt-get install postgresql-8.4 postgresql-contrib-8.4 postgresql-doc-8.4
#sudo apt-get install postgresql postgresql-contrib

## Design a Postgres database schema for storing browser fingerprints
sudo -u postgres createuser "$userimp"

ALTER USER "$userimp" with password '"$passimp"';

#createdb -h localhost -p 5432 -U postgres -W ‘new-password’ browsersfgp

createdb -h localhost -p 5432 -U "$userimp"  -W `"$passimp"` "$db" 
#createdb -U postgres(db user) dbname

## HTTP fingerprints table
psql  -d browsersfgp -c """CREATE TABLE IF NOT EXISTS http_fgp (http_id INT NOT NULL, http_fgp VARCHAR(500) NOT NULL, PRIMARY KEY (http_id));"""
## Add infos about the browser?


## TLS fingerprints table
psql  -d browsersfgp -c """CREATE TABLE IF NOT EXISTS tls_fgp (tls_id INT NOT NULL, tls_fgp VARCHAR(500) NOT NULL, PRIMARY KEY (tls_id));"""


## cross-reference table
## Matches the id of a line in http_fgp to the corresponding id in tls_fgp
psql  -d browsersfgp -c """CREATE TABLE IF NOT EXISTS cross_fgp (http_id INT NOT NULL, tls_id INT NOT NULL, PRIMARY KEY  (http_id, tls_id));"""


#https://stackoverflow.com/questions/2748607/how-to-thoroughly-purge-and-reinstall-postgresql-on-ubuntu
