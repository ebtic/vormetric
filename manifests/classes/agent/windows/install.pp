class vormetric::agent::windows::install (
) {

  #if $vormetric::params::vm_agent_registered {
	
	#install python
	case $architecture {
      i386, i686: {
		package { "python":
          ensure   => installed,
          provider => 'msi', 
          source   => 'http://www.python.org/ftp/python/2.7.5/python-2.7.5.msi',
          install_options => [{'ALLUSERS' => '1'}],
        }
		file { "C:/i386":
	      ensure => directory, 
          mode   => '0777',
          owner  => 'Administrator',
          group  => 'Administrators',
        }
	  }
      x86_64: { 
	    package { "python":
          ensure   => installed,
          provider => 'msi', 
          source   => 'http://www.python.org/ftp/python/2.7.5/python-2.7.5.amd64.msi',
		  install_options => [{'ALLUSERS' => '1'}],
        }    
		file { "C:/x8664":
	      ensure => directory, 
          mode   => '0777',
          owner  => 'Administrator',
          group  => 'Administrators',
        }
	  }
	  default: {
	    file { "C:/default":
	      ensure => directory, 
          mode   => '0777',
          owner  => 'Administrator',
          group  => 'Administrators',
        }
	  }  
    }

    #create management folder
	$vm_management_folder = "C:/btconfig"
	
	file { "$vm_management_folder":
	  ensure => directory, 
      mode   => '0777',
      owner  => 'Administrator',
      group  => 'Administrators',
    }	
  
    #download python code
    file { "$vm_management_folder/vormetric_agent_management.py":
	  ensure  => file,
      mode    => '0777',
      owner   => 'Administrator',
      group   => 'Administrators',      
      source  => "puppet:///modules/vormetric/vormetric_agent_management.py",
      require => File["$vm_management_folder"],
    }
  #}
}
