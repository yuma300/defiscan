# defiscan

## docker
### for start

$ docker-compose up -d

### for access to shell in the container

$ docker-compose exec defiscan bash

### for end

$ docker-compose down

### for remove

$ docker-compose down --rmi all --volumes --remove-orphans

## how to user
### kavascan
in the container

```
#cd app/kava
#python kavascan.py your_kava_address  (ex. # python kavascan.py kava12dyshua9nkvx9w8ywp72wdnzrc4t4mnnycz0dl
#cat transactions.txt
```


### kava for cryptact customfile

in the container

*NOTICE!!!!!!*
Since **transactions.txt** is required which is generated by kavascan.py, execute kavascan.py before.

```
#cd app/kava
#python kava_cryptact.py your_kava_address  (ex. # python kavascan.py kava12dyshua9nkvx9w8ywp72wdnzrc4t4mnnycz0dl
#cat kava_cryptact.csv 
```

### cosmosscan

in the container

```
#cd app/cosmos
#python cosmosscan.py your_cosmos_address  (ex. # python cosmosscan.py cosmos1t5u0jfg3ljsjrh2m9e47d4ny2hea7eehxrzdgd
#cat transactions.txt
```


### cosmos_to_caaj

in the container

```
#cd app/cosmos_to_caaj
#python src/main.py your_cosmos_address
#cat output/cosmos_caaj_your_cosmos_address
```


