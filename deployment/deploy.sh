#!/bin/bash -e

# Generate a password for service account
ADMIN_PASS=$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c10)
sed -i "s/adminpassword/$ADMIN_PASS/g" catalog-ci-jenkins/modules/catalog_ci/manifests/init.pp

sudo apt-get update
sudo apt-get install git puppet -y

# Using custom (forked) puppet-jenkins module
# due to critical problem in the upstream one
git clone https://github.com/skolekonov/puppet-jenkins.git
tar czf rtyler-jenkins-1.3.0.tar.gz puppet-jenkins/*
sudo puppet module install rtyler-jenkins-1.3.0.tar.gz

sudo puppet apply -vd --modulepath catalog-ci-jenkins/modules:/etc/puppet/modules catalog-ci-jenkins/manifests/site.pp

echo "Deployment completed"
echo "WARNING. Please open Jenkins WebUI and setup user access matrix"
