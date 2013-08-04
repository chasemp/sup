sup
===

sup is a tool to be used like ping but with more protocol awareness.

<pre><code>
like ping but for protocols

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

    sup webdos

    02.10.29 webdos:22 ok 0.0 ms
    02.10.31 webdos:22 ok 0.0 ms
    02.10.33 webdos:22 ok 0.0 ms
    02.10.35 webdos:22 ok 0.0 ms

TCP Ping non-defaul port:

    sup webdos:80

    02.10.29 webdos:80 ok 0.0 ms
    02.10.31 webdos:80 ok 0.0 ms
    02.10.33 webdos:80 ok 0.0 ms
    02.10.35 webdos:80 ok 0.0 ms

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

sup is really useful for ongoing 'pinging' while doing mainenance in the background.

sup can notify you of state changes.

Run sup tcping in background with 'broadcast' enabled:

    ./sup.py webdos -b &
    [1] 25420

Now when that host state changes it is broadcast:

    02.14.46 webdos:22 ok 0.0 ms
    02.14.48 webdos:22 ok 0.0 ms
    02.14.50 webdos:22 ok 0.0 ms
    02.14.52 webdos:22 ok 0.0 ms
    Broadcast Message from root@idle34                                             
            (/dev/pts/0) at 14:14 ...                                              
                                                                               
    02.14.54 webdos:22 timeout 0.0 ms

sup can also do a GUI popup if X is installed:
    ./sup.py webdos -p &
