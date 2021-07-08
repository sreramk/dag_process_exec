FROM ubuntu:20.04

RUN apt-get update  &&                      \
    apt-get upgrade -y &&                   \
    apt-get install -y vim &&               \
    apt-get install -y lsb-release &&       \
    apt-get install -y wget &&              \
    apt-get install -y gnupg2 &&            \
    apt-get clean all
    
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | tee /etc/apt/sources.list.d/pgdg.list &&  \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - &&                                     \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone &&                                               \
    apt-get update &&                                                                                                           \
    apt-get -y install postgresql postgresql-contrib postgresql-common


RUN printf "# TEST ENVIRONMENT: ACCEPTS CONNECTIONS FROM ANY CLIENTS\nhost    all             all             0.0.0.0/0               md5\nhost    all             all             ::/0                    md5\n" >> "/etc/postgresql/13/main/pg_hba.conf" && \
    pg_ctlcluster 13 main start &&                                                                                      \
    su - postgres -c " psql -c \"ALTER SYSTEM SET listen_addresses TO '*';\"" &&                                        \
    pg_ctlcluster 13 main restart

COPY . .

# this must also keep the process alive idefinitely.
CMD ["/bin/bash", "startup.sh"]




# CMD ["pg_ctlcluster", "13", "main", "start" ] 

# ALTER SYSTEM SET listen_addresses TO '*';

# by default associates the 

# sudo docker run --name store_p1_r1 --rm psql_ubuntu:0.3 &
# sudo docker build . --tag psql_ubuntu:0.3
# 
