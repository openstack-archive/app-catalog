apps-catalog-ci
========
Description
----------------------
This is a collection of deployment scripts for apps-catalog CI project.
It consists of Puppet module catalog_ci and an additional shell script.
The scripts allow to setup Jenkins with access to Gerrit to trigger
appropriate jobs on a commit to the apps-catalog project.

Deployment
----------------------
Execute deploy.sh script to begin deployment:
(some operations require superuser access rights)

./deploy.sh

The script will install necessary packages and deploy/configure Jenkins.
You will be able to access it at http://server_ip:8080
The following steps are required after deployment:
- Setup access rights. By default Jenkins uses Launchpad OpenID and all users
  have full access to Jenkins.
  Proceed to Manage Jenkins -> Configure Global Security and setup security.
- Finish Gerrit auth setup:
  Add a private key file (id_rsa) to Jenkins ssh directory:
  * sudo mkdir -p /var/lib/jenkins/.ssh
  * sudo cp id_rsa /var/lib/jenkins/.ssh
  * sudo chown -R jenkins:jenkins /var/lib/jenkins/.ssh
  * sudo chmod 600 /var/lib/jenkins/.ssh/id_rsa
  Then proceed to Manage Jenkins -> Gerrit Trigger and press the button
  in 'Status' column. If button will change its color to green, your connection
  to Gerrit works OK and Jenkins is receiving Gerrit events. Otherwise please
  check Gerrit server parameters.
- rclone (http://rclone.org/) is used to upload images to CDN.
  Please install and configure it manually, if it's required.
  'jenkins' user should be able to access default rclone configuration file
  in order to use it.

Jenkins Jobs
----------------------
Jenkins Job Builder is used to configure Jenkins jobs. It will be automatically
installed by deployment scripts. Jobs configuration files will be placed to
/etc/jenkins_jobs/jobs. You can use the following command to apply your changes

jenkins-jobs update /etc/jenkins_jobs/jobs
