class vormetric::params {

  #default values of parameters for testing purpose
  #$host_ip = "none"
  #$host_dns = "none"
  #$agent_download_url = "ec2-54-161-187-162.compute-1.amazonaws.com"
  #$vm_dns = "none"
  #$guardpoint_list = "none"  
  #$status = "initial"
  info("come here")
  
  # these are parameters to be retrieved from hiera
  if $appcara::params::site {
    $site_extsvc_option = $appcara::params::site["extension_service_option"]
    if $site_extsvc_option {
      $site_vormetric_option = $site_extsvc_option["vormetric"]
      if $site_vormetric_option {
        info("site_vormetric_option exists")	  
        $host_ip = "xx_${site_vormetric_option["host_ip"]}_xx"
        $host_dns = "yy_${site_vormetric_option["host_dns"]}_yy"
      }
	  else{
	    $host_ip = "site_vormetric_option_false"
        $host_dns = "site_vormetric_option_false"		
      }	  
    }	
    else{
      $host_ip = "site_extsvc_option_false"
      $host_dns = "site_extsrv_option_false"	  
    }
  }
  else{
    $host_ip = "appcara_params_site_false"
	$host_dns = "appcara_params_site_false"
  }
  
  if $appcara::params::server {
    $svr_extsvc_option = $appcara::params::server["extension_service_option"]
    if $svr_extsvc_option {
      $svr_vormetric_option = $svr_extsvc_option['vormetric']
      if $svr_vormetric_option {
        $vm_dns = $svr_vormetric_option["vm_dns"]
        $guardpoint_list = $svr_vormetric_option["guardpoint_list"]
      }
    }
  }
}
