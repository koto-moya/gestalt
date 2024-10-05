## How to set up a database server


- stand up postgres database on the server (basically just download postgres)

- edit postgresql.conf and pg_hba.conf to add work box to the allowed connections (listen_addresses and ipv4 entry respectively)
    - listening addresses are the local (from the servers perspective) addresses
    - pg_hba is where you put the external ips


- need to enable ssl in the postgresql.conf file
    - ssl = on
- need to change the hba file: host -> hostssl

