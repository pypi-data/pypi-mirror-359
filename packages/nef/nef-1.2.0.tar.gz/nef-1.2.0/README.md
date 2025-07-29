# nef  
  
simple command line client for aws cloudwatch logs.  
  
in the search for a cloudwatch CLI, you will find several other (3 as of writing this) tools:  
https://github.com/jorgebastida/awslogs  
https://github.com/winebarrel/cwli  
https://github.com/knqyf263/utern  
  
while these tools are great, they all have more features than i needed, and those i've tried are kind of complicated to figure out.  
  
my goal in writing `nef` was to have a command line tool that lets me view logs and log groups easily and quickly without logging into the aws web console. it amounts to a thin wrapper for the aws cli log command, which simplifies both the input and the output.  
  
see below for installation and usage info. see the project homepage for more info: https://gitlab.com/shindagger/nef  
  
# installation  
  
`pip install nef`  
   
# dependencies  
  
- aws cli
- python 3.6
  
# flags  
  
```
positional arguments:
  log            Which log group to view

optional arguments:
  -h, --help     show this help message and exit
  --start START  optional. give a start date and time.
                 format: YYYY-MM-DD HH:MM:SS
                 example: nef /path/to/log-group --start 2019-11-25
                 example 2: nef /path/to/log-group --start "2019-11-25 10:24"
                 example 3: nef /path/to/log-group --start "2019-11-25 10:24:32"
                 default (if arg not given): 2019-11-25 15:26:50
  --end END      optional. define an end date/time.
                 see --start for formatting info
  -c, --columns  show log groups in columns
  -j, --json     display output as json
  -v, --version  show program's version number and exit
  ```  

# usage   
  
`$ nef -h`  
  
show help message and exit.  
  
`$ nef`  
   
print out all log groups.   
  
`$ nef -c`  
  
print log groups in concise columnar format.  
   
`$ nef /path/to/log_group`   
   
show info (the last 24 hours) of the log group `/path/to/log_group`  
  
`$ nef /path/to/log_group --start 2019-11-25`   
  
show logs since the 25th of Nov 2019.  
  
`$ nef /path/to/log_group --start "2019-11-25 10:30"`  
  
optionally include a time part (be sure to wrap the string in quotes for the space).  

### example    

![Usage example][example]

[example]: https://believe-it-or-not-im-walking-on-air.s3.amazonaws.com/nef.gif "Usage example"  
