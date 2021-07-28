# dag_process_exec

I wrote this to help me setup PostgreSQL instances with docker, to help me with building my customized replication-partition manager as a part of the API, instead of having PostgreSQL do it for me. This acts as a really great tool for setting up my test environment, by launching all the dockerized PostgreSQL instances. 

# Pipe wrapper

This also implements a simple pipe wrapper to interact with (read and write) a running application's STDIN, STDOUT and STDERR without having to wait for the application to finish executing. Python provides a way to use pipes to launch processes, but does not provide us with an easy to use way to process them in separate threads.  

## Future work 

This project might be generalized to help with any devOps pipelining tasks, and even extended it into a complete job scheduling system. As it includes a custom pipelining library built using `subprocess.Popen`. 
