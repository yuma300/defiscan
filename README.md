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
#cat output/cosmos_caaj_your_cosmos_address.csv
```


### stellarscan
in the container
*NOTICE!!!!!!*
This script is *not* get Full AirDrop History
```
#bash
#cd app/stellar
#python stellarscan.py your_stellar_address  (ex. # python stellarscan.py GAYOLLLUIZE4DZMBB2ZBKGBUBZLIOYU6XFLW37GBP2VZD3ABNXCW4BVA
#cat transactions.txt
```


### stellar for cryptact customfile

in the container

*NOTICE!!!!!!*
Since **transactions.txt** is required which is generated by stellarscan.py, execute stellarscan.py before.

```
#bash
#cd app/stellar
#python stellar_cryptact.py your_stellar_address  (ex. # python stellarscan.py GAYOLLLUIZE4DZMBB2ZBKGBUBZLIOYU6XFLW37GBP2VZD3ABNXCW4BVA
#cat stellar_cryptact.csv
```

### symbolscan
in the container
*NOTICE!!!!!!*
This script is *not* get Full AirDrop History
```
#bash
#cd app/symbol
#python symbolscan.py your_symbol_address  (ex. # python symbolscan.py NCTOGU4INIO7DXLGWXBXBQHE3T6C6WBQNFUKY6A
#cat transactions.txt
```

If you want to use DHC, comment out line 58 of symbolscan.py and run line 60.

### symbol for cryptact customfile

in the container

*NOTICE!!!!!!*
Since **transactions.txt** is required which is generated by symbolscan.py, execute symbolscan.py before.
The money transfer is also an **BONUS**, so be careful.
You'll have to clear your own money transfer history.

```
#bash
#cd app/symbol
#python symbol_cryptact.py your_symbol_address  (ex. # python symbolscan.py NCTOGU4INIO7DXLGWXBXBQHE3T6C6WBQNFUKY6A
#cat symbol_cryptact.csv
```

If you want to use DHC, comment out lines 16-18 of symbol_cryptact.py and run lines 20-22.
