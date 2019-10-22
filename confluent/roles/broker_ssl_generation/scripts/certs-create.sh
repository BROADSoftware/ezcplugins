#!/bin/bash

set -o nounset \
    -o errexit \
    -o verbose
#    -o xtrace

# Cleanup files
rm -f *.crt *.csr *_creds *.jks *.srl *.key *.pem *.der *.p12

i=$(hostname -f)
ca_key_pass=$1
key_password=$2
keystore_password=$3
truststore_password=$4
echo "------------------------------- $i -------------------------------"

# Create host keystore with private key
keytool -genkey -noprompt \
       -alias $i \
       -dname "CN=$i" \
       -ext san=dns:$i \
       -keystore server.keystore.jks \
       -keyalg RSA \
       -storepass $keystore_password \
       -keypass $key_password

# Create the certificate signing request (CSR)
keytool -keystore server.keystore.jks -alias $i -certreq -file server.csr -storepass $keystore_password -keypass $key_password

      # Sign the host certificate with the certificate authority (CA)
openssl x509 -req -CA /var/private/ssl/ca/CARoot.crt -CAkey /var/private/ssl/ca/CARoot.key -in server.csr -out server-ca1-signed.crt -days 9999 -CAcreateserial -passin pass:$ca_key_pass

      # Import the CA cert into the keystore
keytool -noprompt -keystore server.keystore.jks -alias CARoot -import -file /var/private/ssl/ca/CARoot.crt -storepass $keystore_password -keypass $key_password

      # Import the host certificate into the keystore
keytool -noprompt -keystore server.keystore.jks -alias $i -import -file server-ca1-signed.crt -storepass $keystore_password -keypass $key_password

# Create truststore and import the CA cert
keytool -noprompt -keystore server.truststore.jks -alias CARoot -import -file /var/private/ssl/ca/CARoot.crt -storepass $truststore_password -keypass $key_password




