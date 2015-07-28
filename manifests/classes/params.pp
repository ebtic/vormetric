class vormetric::params {

  # these are parameters to be retrieved from hiera
  if $appcara::params::site {
    $site_extsvc_option = $appcara::params::site["extension_service_option"]
    if $site_extsvc_option {
      $site_vormetric_option = $site_extsvc_option["vormetric"]
      if $site_vormetric_option {        
		#$host_ip = "217.33.61.85"
		#$host_dns = "DSM"
        $host_ip = $site_vormetric_option["host_ip"]		
        $host_dns = $site_vormetric_option["host_dns"]        
      }	  
    }	    
  }  
  
  if $appcara::params::server {
    $svr_extsvc_option = $appcara::params::server["extension_service_option"]
    if $svr_extsvc_option {
      $svr_vormetric_option = $svr_extsvc_option['vormetric']
      if $svr_vormetric_option {
	    $vm_state = "vormetric_service_subscription"
        #$vm_state = $svr_vormetric_option["vm_state"]
      }
    }
  }
}
