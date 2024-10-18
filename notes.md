## How to set up a database server

- on the linux server need to set ufw (uncomplicated firewall) 
    - sudo ufw allow from [work box ip] to any port [port] (5432 for postgresql, 22 for ssh)
    - be sure to enable the ssh port because it will kill your ability to ssh if you enable ufw and do not allow port 22
        - I know have to go into the server physically to fix this lol
    - also need to allow for web traffic (port 80 for http or port 443 for https when cert enabled)
    - Overall I am much more at ease with the security of the server.  


- stand up postgres database on the server (basically just download postgres)

- edit postgresql.conf and pg_hba.conf to add work box to the allowed connections (listen_addresses and ipv4 entry respectively)
    - listening addresses are the local (from the servers perspective) addresses
    - Make sure there is no space between the addresses in the listen address line
    - pg_hba is where you put the external ips


- need to enable ssl in the postgresql.conf file
    - ssl = on
- need to change the hba file: host -> hostssl  

- make sure to restart postgres on server startup to listen on the right port. ( add to bashrc file for automation.)


podcast test names

podtest, podtest2
