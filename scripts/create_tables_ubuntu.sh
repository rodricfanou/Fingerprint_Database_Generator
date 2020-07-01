#!/bin/bash
USER='roderick'

# install postgre sql
#sudo apt-get install postgresql postgresql-contrib

## Design a Postgres database schema for storing browser fingerprints
sudo -u postgres createuser $USER

createdb browsersfgp -U postgres;
#createdb -U postgres(db user) dbname


## HTTP fingerprints table
psql  -d browsersfgp -c """CREATE TABLE IF NOT EXISTS http_fgp (http_id INT NOT NULL, http_fgp VARCHAR(500) NOT NULL, PRIMARY KEY (http_id));"""
## Add infos about the browser?



## TLS fingerprints table
psql  -d browsersfgp -c """CREATE TABLE IF NOT EXISTS tls_fgp (tls_id INT NOT NULL, tls_fgp VARCHAR(500) NOT NULL, PRIMARY KEY (tls_id));"""



## cross-reference table
## Matches the id of a line in http_fgp to the corresponding id in tls_fgp
psql  -d browsersfgp -c """CREATE TABLE IF NOT EXISTS cross_fgp (http_id INT NOT NULL, tls_id INT NOT NULL, PRIMARY KEY  (http_id, tls_id));"""
