class vormetric::agent::windows::config (
) {

  if $vormetric::params::vm_agent_registered {
    exec { "vm_guardpoint_management":
      cwd     => "$vm_management_folder",
      path    => "C:/Python27",
      command => "python vormetric_agent_managenent.py",
    }
  }   
}
