# Fingerprint_Database_Generator
The MITMEngine project (https://github.com/cloudflare/mitmengine) detects HTTPS interception and user agent spoofing by checking if the TLS fingerprint of an incoming connection corresponds to the expected fingerprint for the connection’s user agent. MITMEngine powers the MALCOLM dashboard (https://malcolm.cloudflare.com). The goal of this project is to use BrowserStack to generate TLS client hello fingerprints and user agents for a selection of recent browsers and store them in a Postgres database.


## Steps

#### 1- On MacOS Mojave 

a- Install version 12.3 postgresql on Mac using: https://www.robinwieruch.de/postgres-sql-macos-setup;  you can run "brew install postgresql"

b- Create postgresql database with a table listing the http fingerprints, a table listing the tls fingerprints and a third table storing the matching of their respective ids (run script ). 
 
  
#### 1- On Ubuntu
 
a- Install version 12.3 postgresql on Ubuntu using: https://www.postgresql.org/docs/9.0/tutorial-install.html
  * In case you get the error `createdb: could not connect to database template1: FATAL:  Peer authentication failed for user "postgres"`,  
     * run `sudo nano /etc/postgresql/10/main/pg_hba.conf` and 
     * replace `local   all             postgres                                peer` by `local   all             postgres                                trust`
     * `sudo /etc/init.d/postgresql reload 

2- Create an account on BrowserStack (a free account would be enough for this project); automate browserstack for python using https://www.browserstack.com/automate/python. 
  * install behave-browserstack (https://github.com/browserstack/behave-browserstack.git) -- not sure this is compulsory
  
3- Download and install mitmengine (Not necessary for the project) 
  * setup Go (https://golang.org/dl/go1.14.4.linux-amd64.tar.gz) using https://golang.org/doc/install
  * install and run vendering or gomo logic using https://gocodecloud.com/blog/2016/03/29/go-vendoring-beginner-tutorial/ 
  * Use Go 1.14.1 (go version go1.14.4 linux/amd64 for linux and go1.14.4 darwin/amd64 for macOS). In case you needed to uninstall Go, use https://stackoverflow.com/questions/42186003/how-to-uninstall-golang
  * set GOPATH to /home/username/go/
  * run ``make test`` and ``make cover`` in ```/home/username/go/src/github.com/cloudflare/mitmengine```
 
4- Tried to run Browserstack in a local setting and combine with Wireshark to infer TLS header. Issues while running ```paver run local```. 

5- 



## Writeup on design choices

1- Design of the Postgresql database.
We created 3 tables with the primary keys (PK) and informations below. Table 3 links the HTTPS fingerprints to the TLS fingerprints using their respective IDs (http_is and tls_id). 

```
          Table1: "http_fgps"
  Column   |     Type      | Modifiers
-----------+---------------+-----------
 http_id   | integer (PF)  | not null
 http_fgp  | character(500) |


          Table2: "tls_fgps"
  Column   |     Type      | Modifiers
-----------+---------------+-----------
 tls_id   | integer (PF)   | not null
 tls_fgp  | character(500) | 


                Table3: "cross_fgps"
  Column   |     Type                   | Modifiers
-----------+----------------------------+-----------
 http_id   | integer (FK from Table 1)  | not null
 tls_id    | integer (FK from Table 2)  | not null
 
```

2- By running the command,  `curl -u "username:key" https://api.browserstack.com/automate/browsers.json > browsers_infos.json`, we get a list of desired capabilities for both desktop and mobile browsers of Browserstack. The command returns a flat hash in the format [:os, :os_version, :browser, :browser_version, :device, :real_mobile]. We chose to use the outputs to build the HTTPS fingerprints of all available devices. We adopted the following format for HTTPS fingerprints; non available informations are ommitted.

```<browser_name>:<browser_version>:<os_platform>:<os_name>:<os_version>:<device_type>:<quirks>|<tls_version>:<cipher_suites>:<extension_names>:<curves>:<ec_point_fmts>:<http_headers>:<quirks>|<mitm_name>:<mitm_type>:<mitm_grade>```


3- 



