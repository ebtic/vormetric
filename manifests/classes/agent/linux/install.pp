class vormetric::agent::linux::install() {

  #if $vormetric::params::vm_agent_registered {
	
	$vm_management_folder = "/btconfig"
	
	#create management folder
	file { "$vm_management_folder":
	  ensure => directory, 
    }  
  
    #download python code
    file { "$vm_management_folder/vormetric_agent_management.py":
      ensure  => file,
      mode    => "0700",
      owner   => 'root',
      group   => 'root',
      source  => "puppet:///modules/vormetric/vormetric_agent_management.py",
      require => File["$vm_management_folder"],
    }

	#install vormetric agent
    exec { "vormetric_agent_installation":
      cwd     => "$vm_management_folder",
      path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
      creates => "/opt/vormetric/DataSecurityExpert/agent/vmd/bin/vmd",         
      command => "python vormetric_agent_managenent.py install $agent_download_url $vormetric_server_ip $vormetric_server_dns",
      require => [File["$vm_management_folder/vormetric_agent_management.py"]],
    }
	
	#register vormetric agent
	#exec { "vormetric_agent_registration":
    #  cwd     => "$vm_management_folder",
    #  path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
    #  creates => "/opt/vormetric/DataSecurityExpert/agent/vmd/pem/agent.pem",
    #  command => "python vormetric_agent_management.py register $server_dns $agent_dns",
    #  require => [Exec["vormetric_agent_installation"]],
    #}	
  #}
}
