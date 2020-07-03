#!/usr/bin/env python
#python build_and_store_fingerprints.py fanouroderick1 sxuyw68wEHXq9TEPxrnH

## Description
## This script gets all the possible browsers in browsersStack and use their
## informations to infer their respective HTTP fingerprints

import os, sys, json, psycopg2
from config import *


def build_https_fgp(username, key, cur):

	## fetch infos about all available browsers from browserstack
	command = """curl -u  '""" + username + ':' + key + """' https://api.browserstack.com/automate/browsers.json > browsers_infos.json"""
	print command

	## To enable later
	#os.system(command)

	## Load the json file
	f = open('browsers_infos.json', "r")	
	data = json.load(f)

	## Construct the HTTPS fingerprint
	## <browser_name>:<browser_version>:<os_platform>:<os_name>:<os_version>:<device_type>:|<tls_version>:<cipher_suites>:<extension_names>:
	## :<ec_point_fmts>:<http_headers>:|<mitm_name>:<mitm_type>:<mitm_grade>

	records = []

	k = 1
	for line in data:
		#print line
		## Typical example of line: {u'real_mobile': True, u'os_version': u'4.4', u'browser_version': None, u'device': u'Samsung Galaxy Tab 4', u'os': u'android', u'browser': u'android'}
		
		## Avoid spaces in the device
		device = str(line['device']).replace(' ', '')
		browserv = str(line['browser_version']).replace(' ', '')		
		os_name = str(line['os']).replace(' ', '')

		## Infer HTTPS fingerprints
		if line['real_mobile'] == True:
			https_fgp = str(line['browser']) + ':' + browserv + ':' + 'mobile' + ':' + str(os_name) + ':' +str(line['os_version'])+ ':' + str(device)+ ':|::::::|::'
		else:
			https_fgp = str(line['browser']) + ':' + browserv + ':' + 'desktop' + ':' + str(os_name) + ':' +str(line['os_version'])+ ':' + str(device)+ ':|::::::|::'

		## if needed print HTTPS fingerprint
		#print https_fgp
		records.append((k, https_fgp))
		print 
		k+=1

	store_https_fgp(records, conn)




def store_https_fgp(records, conn):

	#print id, https_fgp

	# Create a cursor object
        ## Potential imporvement: Use executemany
	cur = conn.cursor()

	try:
		postgres_insert_query = """ INSERT INTO http_fgp VALUES (%s,%s) """
   		cur.executemany(postgres_insert_query, records)
		conn.commit()
   		count = cur.rowcount
   		print (count, "Record inserted successfully into table")

	except (Exception, psycopg2.Error) as error:
    		if(conn):
        		print("Failed to insert record into mobile table", error)

	finally:
		pass
    		#closing database connection.
    		#if(conn):
        		#cur.close()
        		#conn.close()
        		#print("PostgreSQL connection is closed")




def build_tls_fingerprints(filename, machine, k,  Dict_https_queries, conn):
	## Dictionary keeping all the infos of the fine necessary to build a TLS fingerprint
	# <tls_version>:<cipher_suites>:<extension_names>:<curves>:<ec_point_fmts>:<http_headers>:<quirks> 
	Dict_Tls_fgp = {}
	Dict_Tls_fgp['cipher_suites'] = ''
        Dict_Tls_fgp['tls_version'] = ''
        Dict_Tls_fgp['quirks'] = ''

	with open(filename) as fg:
		for line in fg:
			#print line
			if 'Protocol  :' in line:
				line = line.strip()
				tab = line.split(':')
				Dict_Tls_fgp['tls_version'] = str(tab[1]).strip() 	

			if 'Cipher    :' in line:
				line = line.strip()
				tab = line.split(':')
				#print tab 
				Dict_Tls_fgp['cipher_suites'] = str(tab[1]).strip()

			if "Peer signature type:" in line:
				line =line.strip()
				tab = line.split(':')
				Dict_Tls_fgp['quirks'] =  str(tab[1]).strip()

	## <browser_name>:<browser_version>:<os_platform>:<os_name>:<os_version>:<device_type>:|<tls_version>:<cipher_suites>:<extension_names>:
        ## :<ec_point_fmts>:<http_headers>:|<mitm_name>:<mitm_type>:<mitm_grade>

	tab1 = machine.split(':')
	tls_fingerprint = tab1[0] + ":" + tab1[1]+ ":" + tab1[2]+ ':' + tab1[3] + ':' + tab1[4] + ':' + tab1[5] + '|' +  Dict_Tls_fgp['tls_version'] + ':' + Dict_Tls_fgp['cipher_suites'] + ':::::' + Dict_Tls_fgp['quirks'] + '|::'
	print tls_fingerprint	
	store_tls_fgp(tls_fingerprint, k,  Dict_https_queries, conn)
	


def store_tls_fgp(tls_fingerprint, k,  list_https, conn):
        # Insert tls_fgp
        cur = conn.cursor()

        try:
                postgres_insert_query = """ INSERT INTO tls_fgp VALUES (%s,%s) """
                cur.execute(postgres_insert_query, (k, tls_fingerprint))
                #conn.commit()
                #count = cur.rowcount
                #print (count, "Record inserted successfully into table tls_fgp")

        except (Exception, psycopg2.Error) as error:
                if(conn):
                        print("Failed to insert record into mobile table", error)

        finally:
                pass

	## Match TLS samples
	Max_match = 0
	Match_http_k = 0
	keep = ""

	for https_fgp in  list_https:
		#print https_fgp, tls_fingerprint

		#(1855, 'android:None:mobile:android:6.0:SamsungGalaxyS7:|::::::|::') firefox::desktop:Linux:Oberon:4.15.0|TLSv1.3:TLS_AES_256_GCM_SHA384:::::RSA-PSS|::
		https_fgp_tab = https_fgp[1].split('|')
		https_fgp_tab1 = https_fgp_tab[0].split(':')

		tls_fingerprint_tab = tls_fingerprint.split('|')
	 	tls_fingerprint_tab1 = tls_fingerprint_tab[0].split(':')

		id = 0
		value = 0
		while id < len(https_fgp_tab1)-1:
			
			if https_fgp_tab1[id] == tls_fingerprint_tab1[id] and https_fgp_tab1[id] != '':
				value += 1
			else:
				value -= 1
			id += 1

		if value > Max_match:
			Match_http_k = https_fgp[0]
			keep = https_fgp_tab

	print 'RESULT', 'Match_id', Match_http_k, keep,  tls_fingerprint_tab

	## store the match in table 3 (cross_fgp)
	if Match_http_k>0:
	   try:
		 postgres_insert_query = """ INSERT INTO cross_fgp (http_id, tls_id) VALUES (%s,%s) """
		 cur.execute(postgres_insert_query, (Match_http_k, k))
		 #conn.commit()
                 #count = cur.rowcount
                 #print (count, "Record inserted successfully into table cross_fgp")

	   except (Exception, psycopg2.Error) as error:
                if(conn):
                        print("Failed to insert record into mobile table", error)

           finally:
                pass

	#closing database connection.
                #if(conn):
                        #cur.close()
                        #conn.close()
                        #print("PostgreSQL connection is closed")




if __name__ == "__main__":
	username = sys.argv[1]
	key = sys.argv[2]


	## connexion to the posgresql  database
	## Fetch credentials for database
	print
	print "1- Fetch credentials for database"
	db= config(filename='db.ini', section='postgresql')


	## Connexion to database
	conn = psycopg2.connect(host=db["host"],  database=db["database"], user=db["user"], password = db["password"])	
	# Create a cursor object
	cur = conn.cursor()


	## Build HTTPS fingerprints
	build_and_store = 0
	if build_and_store:
		print
		print "2- Build HTTPS fingerprints"
		build_https_fgp(username, key, conn)


	## Fetching HTTP fingerprints
	print
	print "3- Fetch inserted HTTPS fingerprints"
	cur.execute("select * from http_fgp")
        list_https = cur.fetchall()
        #print out1


	## Build TLS fingerprints from samples
	print
	print "4- Fetch TLS fingerprints"
	TLS_samples = [('sample_tls_fgp_mac0S.txt','safari:13.1.1:desktop:OSX:Mojave:10.14.5'), ('sample_tls_fgp_ubuntu.txt','firefox::desktop:Linux:Oberon:4.15.0')]
	build_and_store = 1
        if build_and_store:
		ind = 0
		for elmt in TLS_samples:
			ind+=1
			build_tls_fingerprints(elmt[0], elmt[1], ind, list_https, conn)


	#Get list of TLS fgp 
	print
	print "5- list TLS fingerprints "
	cur.execute("select * from tls_fgp")
        out2 = cur.fetchall()
        print "Generated TLS fingerprints = ",  out2


	#Get list of TLS fgp 
        print
        print "6- Matches"
        cur.execute("select * from cross_fgp")
        out2 = cur.fetchall()
        print "Generated TLS fingerprints = ",  out2

