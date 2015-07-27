class vormetric::agent::linux::install() {

  #if $vormetric::params::vm_agent_registered {

    notice("assign default parameters")  
    $vm_management_folder = "/btconfig"
    $agent_download_url = "ec2-54-161-187-162.compute-1.amazonaws.com"
	
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

	#install vormetric agent
    exec { "vormetric_agent_installation":
      cwd     => "$vm_management_folder",
      path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
      creates => "/opt/vormetric/DataSecurityExpert/agent/vmd/bin/vmd",         
      command => "python vormetric_agent_management.py install $agent_download_url $vormetric::params::host_ip $vormetric::params::host_dns",
	  #command => "python vormetric_agent_management.py test ${agent_download_url} ${host_ip} ${host_dns}",
      require => [File["${vm_management_folder}/vormetric_agent_management.py"]],
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
