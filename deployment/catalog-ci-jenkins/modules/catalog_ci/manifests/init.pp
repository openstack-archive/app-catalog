class catalog_ci {

  $user           = 'admin'
  $password       = 'adminpassword'
  $jenkins_config = '/var/lib/jenkins/config.xml'
  $gerrit_config  = '/var/lib/jenkins/gerrit-trigger.xml'

  class{ 'jenkins':
    lts          => true,
    install_java => true,
    plugin_hash  => {
      'git' => {},
      'parameterized-trigger' => {},
      'token-macro' => {},
      'mailer' => {},
      'scm-api' => {},
      'promoted-builds' => {},
      'matrix-project' => {},
      'git-client' => {},
      'ssh-credentials' => {},
      'credentials' => {},
      'gerrit-trigger' => {},
      'rebuild' => {},
      'git-client' => {},
      'rabbitmq-consumer' => {},
      'openid' => {},
      'openid4java' => {},
    }
  }

  jenkins::user { "$user":
    email    => 'admin@example.com',
    password => "$password",
  }

  class{ 'jenkins::security':
    security_model => 'full_control',
  }

  Class['jenkins'] -> Jenkins::User["$user"] -> Class['jenkins::security']
  ->  Exec['create_jobs'] -> File["$jenkins_config"]

  package {'python-pip':
    ensure => present,
  }

  package {'deepdiff':
    ensure   => present,
    provider => 'pip',
  }

  package {'pyyaml':
    ensure   => present,
    provider => 'pip',
  }

  package {'jenkins-job-builder':
    ensure   => present,
    provider => 'pip',
  }

  file {'/var/lib/jenkins/scripts':
    owner   => 'root',
    group   => 'root',
    ensure  => directory,
    source  => 'puppet:///modules/catalog_ci/scripts',
    recurse => true,
    require => File['/etc/jenkins_jobs'],
  }

  file {'/etc/jenkins_jobs':
    owner   => 'root',
    group   => 'root',
    ensure  => directory,
    require => Package['jenkins-job-builder'],
  }

  file {'/etc/jenkins_jobs/jenkins_jobs.ini':
    owner   => 'root',
    group   => 'root',
    content => template('catalog_ci/jenkins_jobs.ini.erb'),
    require => File['/etc/jenkins_jobs'],
  }

  file {'/etc/jenkins_jobs/jobs':
    owner   => 'root',
    group   => 'root',
    ensure  => directory,
    source  => 'puppet:///modules/catalog_ci/jobs',
    recurse => true,
    require => File['/etc/jenkins_jobs'],
  }

  file {"$jenkins_config":
    owner   => 'jenkins',
    group   => 'jenkins',
    ensure  => present,
    source  => 'puppet:///modules/catalog_ci/config.xml',
  }

  file {"$gerrit_config":
    owner   => 'jenkins',
    group   => 'jenkins',
    ensure  => present,
    source  => 'puppet:///modules/catalog_ci/gerrit-trigger.xml',
    require => File["$jenkins_config"],
  }

  exec {'create_jobs':
    command  => 'jenkins-jobs update /etc/jenkins_jobs/jobs',
    path     => '/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin',
    require  => File['/etc/jenkins_jobs/jobs'],
  }

  exec{'restart_jenkins':
    command   => 'service jenkins restart',
    path      => '/bin:/sbin:/usr/bin:/usr/sbin',
    subscribe => [ File["$jenkins_config"], File["$gerrit_config"] ],
  }

  Package['python-pip'] -> Package['deepdiff'] ->
  Package['pyyaml']     -> Package['jenkins-job-builder']
}
