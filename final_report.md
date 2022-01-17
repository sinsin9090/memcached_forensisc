# Live Response tool for Memcached DBMS

## Introduction

Memcached is known as second famous key based Non-R RDBMS, following redis. 

not have persistence feature so should rely on memory forensic technique.

only use string data type, not support shadding, clone, etc

very lightweight DBMS.

## Previous works

- peep: https://github.com/evan/peep, only support for x86 linux, old version memcached(1.12)

live heap inspector for memcached live instace, not forensic purpose

require debug option when compile memcache binary => not fully support for every memcached environment

with peep, get data about memcached instance (time, exptime, nbytes, nsuffix, it_f, clsid, nkey ,key, exprd ,flushd)

ex)
![peep](peep.png)

- KDFS winter academic session: Research on Digital Forensic Investigation Method for memcached Non-RDBMS

For forensics purpose, introduce what artifact can we got from memcached. 

And suggest process about memcached investigation.

ex) memcached.conf(configuration file), /var/log/syslog(memcached log, require -vv option), procdump

![memcachedprocess](memcachedprocess.png)

### limitation of previous works
Didn`t conduct structure analysis only rely on string search
![capture](capture.png)


## Dataset & Experiments

### 0. Experiment Environments
- OS: Linux kali 5.10.0-kali9-amd64 #1 SMP Debian 5.10.46-4kali1 (2021-08-09) x86_64 GNU/Linux
- memcached: 1.6.10
- procdump: 1.2
- python: 3.9.2
- dataset: https://drive.google.com/drive/folders/1mz3gkMHzHjAhSyfYo0bgHluH4ZAG_oNS?usp=sharing

### 1. Variable size Data (Normal 10, length 1-10)
- find binary pattern based on signature 'sin90', 'sin91',..., 'sin99'
- 0xOD 0xOA 0x00 or 0x0D 0x0A 0x0A is a footer of the memcached key-value instance 
- find seperator between key and value as 0x00
- based on key length, value length, data index guess some field in sturcture
- some structure rely on guessing like time, expiretime which previously defined peep
- some sturuture in peep cannot found on this analysis (ex. flushd)

https://drive.google.com/file/d/1LqRmT67eYKHluPiphAoq5_GZeEUUpI_7/view?usp=sharing
![dataset1](dataset1.png)

### 2. Deleted Data (Normal 5, Deleted 5)
- use delete command to delete memcached key-value instance
- find binary pattern based on signature 'sin91', 'sin91',..., 'sin900'
- when compare with normal key-value instance, deleted instance have '00 00 04 00' flag instead of '01 00 03 00' in normal
https://drive.google.com/file/d/149hEsJfSzIDY-NUeuNYnYoXgnn9Y866q/view?usp=sharing
![dataset2](dataset2.png)

### 3. Modified Data (Normal 7, Modified 4)
- use set command to delete memcached key-value instance
- find binary pattern based on signature 'sin91', 'sin91',..., 'sin900'
- when compare with normal key-value instance,**expired** instance have '00 00 04 00' flag instead of '01 00 03 00' 
https://drive.google.com/file/d/1GMN0ounWqwNm2zMq-f99PVGYEv_z2yr3/view?usp=sharing
![dataset3](dataset3.png)

- only little part of modified data can be retrieved through index sequences
- modified data shown not consecutive order in index 
![modi](modirule.png)


### 4. Test set (Normal 5, Deleted 5, Modified 5)
- use delete command to delete memcached key-value instance 
- use set command to delete memcached key-value instance
- set binary pattern based on signature 'cos0', 'cos1',..., 'cos20'
- use for tool tesing
https://drive.google.com/file/d/1mjGN-mo2Gu7L7AxL70usDC6nlSbF6cuj/view?usp=sharing


## Tool Development & Usage

### 1. Prerequisites
- require python3, procdump in linux distribution OS
- run "ps -ed | grep 'memcached'" and find out pid of memcached 
- use procdump to dump process memory about memcached
- check whether process dump had been made. 
![filecheck](filecheck.png)

- run "memcached_inspector.py" with parameter -f as filepath

![python](python.png)

### 2. Used Rule 

![python](rule.png)

### 3. Tool execution results

Checking whether **working perfectly on** Modified Data set, Deleted Data set, Origianl Data set 

Execute on Test set which made above 

![final](final.png)

- even if some of the trace had been recovered, but not all trace had been recovered.
- limitation 1: if some of the data had been overwritten a little , the tool cannot recover the trace 
- limitation 2: if modifiying the consecutive index data, modifier detecting rule can not be adopted 



## Future works
- update rule based on 'peep' ruby source code, more pattern, change time blob data to readable
- reverse enginering memcached binary
- integrate with memcahced system log (/var/syslog)
- more various environments (Windows OS, Mac os X, etc... )
- Develop Volatility Plugin
- More memcached usage scenario (append,prepend, incr, decr, flush_all, etc)

## Reference 
https://blog.evanweaver.com/2009/04/20/peeping-into-memcached/


https://blog.johngoulah.com/2009/06/investigating-memcached/

KDFS winter academic session: Research on Digital Forensic Investigation Method for memcached Non-RDBMS

https://lzone.de/cheat-sheet/memcached