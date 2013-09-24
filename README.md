sup
===

sup is a tool to be used like ping but with more protocol awareness.

Tested on:

    Python 2.6.6
    Python 2.7

    Debian GNU/Linux 6.0.7
    OSX Darwin

<pre><code>
like ping but for higher up the stack

positional arguments:
  site         url or ip of site to manage

optional arguments:
  -h, --help   show this help message and exit
  -p           show popups
  -b           broadcast messages
  -v           verbose
  -vv          very verbose
  -t TIMEOUT   main timeout
  -i INTERVAL  interval between polls
  -m MODE      Check type to use. Available: tcp http smtp ntp tcping
               memcached icmp redis
</code></pre>

TCP Ping (default port is 22):

    sup host.com

    02.10.29 host.com:22 ok 0.0 ms
    02.10.31 host.com:22 ok 0.0 ms
    02.10.33 host.com:22 ok 0.0 ms
    02.10.35 host.com:22 ok 0.0 ms

TCP Ping non-defaul port:

    sup host.com:80

    02.10.29 host.com:80 ok 0.0 ms
    02.10.31 host.com:80 ok 0.0 ms
    02.10.33 host.com:80 ok 0.0 ms
    02.10.35 host.com:80 ok 0.0 ms

Hit 'Enter' to exit with stats at any time:

    avg: 0.0 Max: 0.0 Min: 0.0
    tcping polled 4 times in 8.0 seconds

sup can do 'ping' like behavior for:

    * tcp
    * http
    * smtp
    * ntp
    * memcached
    * icmp
    * redis

'Pinging' Redis:

    sup redis01 -m redis

    02.12.39 redis01:6379 PONG 10.0 ms
    02.12.41 redis01:6379 PONG 0.0 ms

    avg: 5.0 Max: 10.0 Min: 0.0
    redis polled 2 times in 4.0 seconds

'Pinging' memcached:

    /sup.py 10.0.14.41 -m memcached

    02.13.34 10.0.14.41:11211 ok 10.0 ms
    02.13.36 10.0.14.41:11211 ok 0.0 ms
    02.13.38 10.0.14.41:11211 ok 0.0 ms

#### sup can notify you of state changes.

Run sup tcping in background with 'broadcast' enabled:

    ./sup.py host.com -b &
    [1] 25420

Now when that host.com state changes it is broadcast:

    02.14.46 host.com:22 ok 0.0 ms
    02.14.48 host.com:22 ok 0.0 ms
    02.14.50 host.com:22 ok 0.0 ms
    02.14.52 host.com:22 ok 0.0 ms
    Broadcast Message from root@idle34                                             
            (/dev/pts/0) at 14:14 ...                                              
                                                                               
    02.14.54 host.com:22 timeout 0.0 ms

sup can also do a GUI popup if X is installed:
    ./sup.py host.com -p &

#### sup can take configuration directives from an ini file.

Config file location:

    /home/yourname/.sup.ini

default section
localnet  - define ip's to treat as 'local'.  this is pattern matching not IP strict.
remotemon - define the default poller to use for nonlocal resources
localmon - define the default poller to use for local resources

Examples:

    [default]
    localnet = 192.,10. #all 192 and 10 addresses use local monitor
    localmon = tcp #all local use this monitor
    remotemon = http #all non-local use this monitor

substitution section
alias - define an alias to be translated instead of a a full hostname

Example:

    [subs]
    google = www.google.com
    l = localhost

    ./sup.py l
    05.06.58 localhost:22 failed 0.265 ms
    05.06.59 localhost:22 failed 0.792 ms

    ./sup.py google
    05.21.27 www.google.com:80 200 OK 5.664 ms
    05.21.29 www.google.com:80 200 OK 6.117 ms


poller sections
port = 80 #set all tcp polling to port 80 by default

Example:
    [tcp]
    port = 80

#### Flooding

sup can flood as many requests as possible

<pre><code>
./sup.py l:80 -m http -f
04.51.34 localhost:80 200 OK 1.188 ms
04.51.34 localhost:80 200 OK 0.885 ms
04.51.34 localhost:80 200 OK 1.144 ms
...
avg: 0.777363855422 Max: 1.762 Min: 0.601
http polled 415 times in 0.0 seconds
</code></pre>

#### Specify Count

sup allows you to specify a count of attempts (including with -f option)

Limit count to 3 tcping's of localhost port 80 (.ini preference):

<pre><code>
./sup.py l -c 3
04.53.18 localhost:80 ok 0.397 ms
04.53.19 localhost:80 ok 0.463 ms
04.53.20 localhost:80 ok 0.408 ms
avg: 0.422666666667 Max: 0.463 Min: 0.397
tcp polled 3 times in 3.0 seconds
</code></pre>

Limit count to 3 tcping's of localhost port 80 again with flood:

<pre><code>
./sup.py l -c 3 -f
04.53.55 localhost:80 ok 0.347 ms
04.53.55 localhost:80 ok 0.227 ms
04.53.55 localhost:80 ok 0.207 ms
avg: 0.260333333333 Max: 0.347 Min: 0.207
tcp polled 3 times in 0.0 seconds
rush@cair:~/git/github/chasemp/sup$ 
</code></pre>
