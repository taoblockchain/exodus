Settings can be found in exodus.env.

Run once and then configure nginx in ./config
```
docker build . -t exodus:latest 
docker build . -t tao1node:latest -f Dockerfile.tao 
```

# Setup the blockchain data
```
apt-get install unzip
wget http://backchains.s3.amazonaws.com/Tao.zip 
unzip Tao.zip 
mv Tao data
mkdir -p data
cp ./blockchain/tao.conf /data
cp ./blockchain/wallet_notify.sh /data
chmod +x data/wallet_notify.sh
```

# Runnit
```
docker-compose up
```