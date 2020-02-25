# elasticsearch plugin

To use with:
cd .../nih; mkdir ansible-elasticsearch; cd ansible-elasticsearch; git clone https://github.com/elastic/ansible-elasticsearch.git


tested with the following commit:

```
commit 5924b0d3b2269ac8a2e1c311c6574017b84a86ab
Merge: 0e1a723 e299582
Author: Julien Mailleret <julien.mailleret@elastic.co>
Date:   Tue Jan 21 21:06:16 2020 +0100

    Merge pull request #667 from elastic/dependabot/bundler/rubyzip-2.0.0
    
    Bump rubyzip from 1.2.2 to 2.0.0

```


##Notes :
* Starting with ansible-elasticsearch:7.1.1, installing more than one instance of Elasticsearch on the same host is no longer supported --> This plugin require ansible-elasticsearch with versions >= 7.1.1.