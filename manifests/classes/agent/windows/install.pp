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
	  }
      x64, x86_64, amd64: { 
	    package { "python":
          ensure   => installed,
          provider => 'msi', 
          source   => 'http://www.python.org/ftp/python/2.7.5/python-2.7.5.amd64.msi',
		  install_options => [{'ALLUSERS' => '1'}],
        }    		
	  }
	  default: {
	    file { "C:/$architecture":
	      ensure => directory, 
          mode   => '0777',
          owner  => 'Administrator',
          group  => 'Administrators',
        }
	  }  
    }

    #create management folder
	$vm_management_folder = "C:/btconfig"
	$agent_download_url = "ec2-54-161-187-162.compute-1.amazonaws.com"
	
	if $vormetric::params::files_existed == "true" {
	
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
	  	  
	  file { "$vm_management_folder/$::domain":
	    ensure  => file,
        mode    => '0777',
        owner   => 'Administrator',
        group   => 'Administrators',      
        source  => "puppet:///modules/vormetric/vormetric_agent_management.py",
        require => File["$vm_management_folder"],
      }
	  
	  file { "$vm_management_folder/$::appstack_server_identifier":
	    ensure  => file,
        mode    => '0777',
        owner   => 'Administrator',
        group   => 'Administrators',      
        source  => "puppet:///modules/vormetric/vormetric_agent_management.py",
        require => File["$vm_management_folder"],
      }
	  
	  #exec { 'vm-dns-retrieval':
      #  command => 'echo "appstack:extsvc:quang:agent_status=" | out-file -append -encoding ASCII "C:/ProgramData/PuppetLabs/facter/facts.d/trendmicro_dsm_pending_sync_agent_status.txt"',
      #  provider    => powershell,
      #  logoutput   => true,
      #  subscribe   => Exec['activate-trendmicro-deepsecurity-agent'],
      #  refreshonly => true
      #}
	  
	  case $vormetric::params::vm_state{      
	    'subscribed':{
	      exec { "vormetric_service_subscription":
		    cwd     => "$vm_management_folder",
            path    => "C:/Python27",
            creates => "C:/Program Files/Vormetric/DataSecurityExpert/agent/vmd/bin/vmd.exe",
	        command => "python vormetric_agent_management.py subscribe",
            require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
	      }
	    }
	
	    'registered':{
	      exec { "vormetric_agent_installation":
		    cwd     => "$vm_management_folder",
            path    => "C:/Python27",
		    creates => "C:/Program Files/Vormetric/DataSecurityExpert/agent/vmd/bin/vmd.exe",
	        command => "python vormetric_agent_management.py install $agent_download_url $vormetric::params::host_ip $vormetric::params::host_dns",
            require => [Package["python"], [File["${vm_management_folder}/vormetric_agent_management.py"]]],
	      }
		  
		  exec { "vormetric_agent_configuration":
		    cwd     => "$vm_management_folder",
		    path    => "C:/Python27",
		    creates => "C:/ProgramData/Vormetric/DataSecurityExpert/agent/vmd/pem/agent.pem",
		    command => "python vormetric_agent_management.py register $vormetric::params::host_dns",
		    require => [Exec["vormetric_agent_installation"]],
          }
        }	
      }
	}
	else{
	  #TODO for service un-subscription
	}	  
  #}
}
