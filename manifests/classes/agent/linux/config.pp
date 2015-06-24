class vormetric::agent::linux::config() {

  if $vormetric::params::vm_agent_registered {

    exec { "vm_guardpoint_management":
      cwd     => "$vm_management_folder",
      path    => "/bin:/sbin:/usr/bin:/usr/sbin:",
      command => "python vormetric_agent_managenent.py manage $vm_guardpoint_list",
    }
  }   
}
