# defiscan

## docker
### for start

$ docker-compose up -d

### for access to shell in the container

$ docker-compose exec defiscan sh

### for end

$ docker-compose down

## how to user
### kavascan
in the container

```
# cd app/kava
# python kavascan.py your_kava_address  (ex. # python kavascan.py kava12dyshua9nkvx9w8ywp72wdnzrc4t4mnnycz0dl
```


### kava for cryptact customefile

in the container

```
# cd app/kava
# python kava_cryptact.py your_kava_address  (ex. # python kavascan.py kava12dyshua9nkvx9w8ywp72wdnzrc4t4mnnycz0dl
# cat kava_cryptact.csv 
```


