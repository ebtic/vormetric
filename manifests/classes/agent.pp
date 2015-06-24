# Class:vormetric::agent
#
# This module manages TrendMicro DeepSecurity Agent 9.0
#
# Parameters:
#
# Actions:
#
# Requires:
#
# Sample Usage:
#   (See test/init.pp)
class vormetric::agent(
) inherits vormetric::params {

  # perform this only when node tagging is completed
  #if $appcara::params::server {

    case $::operatingsystem {
        # Linux-based computers
        'debian','ubuntu','redhat','centos','Amazon': {
            class { 'vormetric::agent::linux::install': }
            class { 'vormetric::agent::linux::config': }
            Class['vormetric::agent::linux::install']
              -> Class['vormetric::agent::linux::config']
        }
		'windows': {
            class { 'vormetric::agent::windows::install': }
            class { 'vormetric::agent::windows::config': }
            Class['vormetric::agent::windows::install']
              -> Class['vormetric::agent::windows::config']
	    }
        # Other OS
        default: {
            notice("Unsupported OS: $::operatingsystem")
        }
    } # end case
    
  #} # end if $appcara::params::server

} # end of class
