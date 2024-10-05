## How to set up a database server

- on the linux server need to set ufw (uncomplicated firewall) 
    - sudo ufw allow from [work box ip] to any port [port] (5432 for postgresql, 22 for ssh)
    - be sure to enable the ssh port because it will kill your ability to ssh if you enable ufw and do not allow port 22
        - I know have to go into the server physically to fix this lol


- stand up postgres database on the server (basically just download postgres)

- edit postgresql.conf and pg_hba.conf to add work box to the allowed connections (listen_addresses and ipv4 entry respectively)
    - listening addresses are the local (from the servers perspective) addresses
    - pg_hba is where you put the external ips


- need to enable ssl in the postgresql.conf file
    - ssl = on
- need to change the hba file: host -> hostssl