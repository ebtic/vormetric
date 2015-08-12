class vormetric::agent::linux::install() {

  $vm_management_folder = "/btconfig"
  $agent_download_url = "ec2-54-161-187-162.compute-1.amazonaws.com"
  $vm_dns = "$::appstack_server_identifier.$::domain"
  
  file { "/bttest_vmstate_${vormetric::params::vm_state}":
      ensure => directory, 
  }
    
  if $vormetric::params::files_existed == "true" {
    
	#create management folder
    file { "$vm_management_folder":
      ensure => directory, 
    }  
  
    #download python code
    file { "${vm_management_folder}/vormetric_agent_management.py":
      ensure  => file,
      mode    => "0700",
      owner   => 'root',
      group   => 'root',
      source  => "puppet:///modules/vormetric/vormetric_agent_management.py",
      require => File["$vm_management_folder"],
    }
	
	case $vormetric::params::vm_state{      
	  'subscribed':{
	    exec { "vormetric_service_subscription":
		  cwd     => "$vm_management_folder",
          path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
          creates => "/opt/vormetric/DataSecurityExpert/agent/vmd/bin/vmd",         
	      command => "python vormetric_agent_management.py subscribe $vm_dns",
          require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
	    }
	  }
	
	  'registered':{
	    exec { "vormetric_agent_installation":
		  cwd     => "$vm_management_folder",
          path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
          creates => "/opt/vormetric/DataSecurityExpert/agent/vmd/bin/vmd",         
	      command => "python vormetric_agent_management.py install $agent_download_url $vormetric::params::host_ip $vormetric::params::host_dns $vm_dns",
          require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
	    }
      }	
    }
  }
  else{
    #TODO for service un-subscription 
  } 
}
