# 
# Copyright (C) 2015 British Telecom plc. - All Rights Reserved
# Author: Quang Hieu Vu
# Version: 1.0
# Date: July 15, 2015
#
 
import os, sys, stat
import subprocess
import platform
import logging

if sys.version_info >= (3,):
  import urllib.request as urllib2
  import urllib.parse as urlparse
else:
  import urllib2
  import urlparse

#input parameters
AGENT_DOWNLOAD_URL   = 'NONE'
SERVER_DNS           = 'NONE'
SERVER_IP            = 'NONE'
VM_DNS               = 'NONE'
GUARD_POINT          = 'NONE' 

#other supporting parameters
CONFIG_FOLDER        = 'NONE'
TMP_FOLDER           = 'NONE'
LOG_FILE             = 'NONE'
AGENT_FILE           = 'NONE'
SETUP_FILE           = 'NONE'
HOSTS_FILE           = 'NONE'

#show usage text
#*************************************************
def show_usage():
  print 'Usage: python vormetric_agent_management [install, activate, encrypt, decrypt, uninstall, help]'
#*************************************************

#notify error and show usage after that
#*************************************************
def show_error(error_message):
  print error_message
  show_usage()
  sys.exit(2)
#*************************************************

#parse input parameters to determine running mode
#*************************************************
def parse_parameters(argv):
  global AGENT_DOWNLOAD_URL  
  global SERVER_DNS
  global SERVER_IP
  global GUARD_POINT

  if len(sys.argv) == 1:    
    show_error('Error: parameters are required')
  else:
    if sys.argv[1] == 'install' and len(sys.argv) == 5:
      AGENT_DOWNLOAD_URL = sys.argv[2]
      SERVER_DNS = sys.argv[3]
      SERVER_IP = sys.argv[4]
      return 0
    elif sys.argv[1] == 'register' and len(sys.argv) == 4:
      SERVER_DNS = sys.argv[2]
      VM_DNS = sys.argv[3]
      return 1
    elif sys.argv[1] == 'encrypt' and len(sys.argv) == 3:
      GUARD_POINT = sys.argv[2]
      return 2
    elif sys.argv[1] == 'decrypt' and len(sys.argv) == 3:
      GUARD_POINT = sys.argv[2]
      return 3
    elif sys.argv[1] == 'uninstall' and len(sys.argv) == 2:
      return 4
    elif sys.argv[1] == 'help':
      show_usage()
      sys.exit(0)
    elif sys.argv[1] == 'test':
      if len(sys.argv) > 2:
        AGENT_DOWNLOAD_URL = sys.argv[2]
      if len(sys.argv) > 3:
        SERVER_DNS = sys.argv[3]
      if len(sys.argv) > 4:
        SERVER_IP = sys.argv[4]	
      return 5	
    else:
      show_error('Incorrect parameters')
#*************************************************

#*************************************************
def update_linux_lib():
  distribution = platform.linux_distribution()[0]
  if 'Ubuntu' in distribution:
    os.system('apt-get install -y python-pexpect')
  elif 'SUSE' in distribution:
    os.system('zypper install -y python-pexpect')
  elif 'Red Hat' in distribution:
    os.system('yum install -y pexpect')
  elif 'CentOS' in distribution:
    os.system('yum install -y pexpect')
#*************************************************

#*************************************************
#read general information	
def set_variables():
  global CONFIG_FOLDER
  global AGENT_FILE
  global TMP_FOLDER
  global LOG_FILE
  global SETUP_FILE
  global HOSTS_FILE

  if platform.system() == 'Windows':
    CONFIG_FOLDER = 'C:\\btconfig'
    LOG_FILE = CONFIG_FOLDER + '\\btconfig.log'
    AGENT_FILE = 'C:\\Program Files\\Vormetric\\DataSecurityExpert\\agent\\vmd\\bin\\vmd.exe'
    HOSTS_FILE = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
    TMP_FOLDER = 'C:\\tmpdir'
    SETUP_FILE = TMP_FOLDER + '\\fsagent.msi'
    if not (os.path.exists(TMP_FOLDER)):
      os.mkdir(TMP_FOLDER)    
  else:
    CONFIG_FOLDER = '/btconfig'
    LOG_FILE = CONFIG_FOLDER + '/btconfig.log'
    AGENT_FILE = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/vmd'
    SETUP_FILE = CONFIG_FOLDER + '/veefs.bin'
    HOSTS_FILE = '/etc/hosts'
    props_filename = CONFIG_FOLDER + '/general.properties'
#*************************************************

#*************************************************
#check if there is a mapping to Vormetric Server
def check_hosts(host_file, server_dns):
  if server_dns != 'None':
    hosts = open(host_file, 'r')
    for line in hosts:
      if not line.startswith('#'):     
        try:
          if line.split()[1:] == [server_dns]:
            return True
        except:
          pass
    return False
  else:
    return True
#*************************************************

#*************************************************
#update hosts to include a mapping to SCM3
def update_hosts(server_ip, server_dns, host_file):
  with open(host_file, "a") as hosts:
    hosts.write(os.linesep)
    hosts.write(server_ip + ' ' + server_dns)
#*************************************************

#*************************************************
#generate URL for downloading SecureCloud agent
def generate_download_URL():
  download_URL = 'http://' + AGENT_DOWNLOAD_URL
  download_URL = download_URL + ':8080/BTSecureCloudServer/BTSecureCloud/downloadVor?'
  download_URL = download_URL + '&operatingSystem=' + platform.system()
  	
  if platform.system() == 'Windows':
    download_URL = download_URL + '&distribution=N/A' 
    #platform.architecture()[0] == '64bit' does not work if python 32bit is used
    if '(x86)' in os.environ['PROGRAMFILES']: 
      download_URL = download_URL + '&architecture=64bit'
    else:
      download_URL = download_URL + '&architecture=32bit'
  else:
    distribution = platform.linux_distribution()[0]
    if 'Ubuntu' in distribution:
      download_URL = download_URL + '&distribution=Ubuntu'
    elif 'SUSE' in distribution:
      download_URL = download_URL + '&distribution=Suse'
    elif 'Red Hat' in distribution:
      download_URL = download_URL + '&distribution=Red%20hat6'
    elif 'CentOS' in distribution:
      download_URL = download_URL + '&distribution=CentOS'
    download_URL = download_URL + '&architecture=' + platform.architecture()[0] #platform.machine()
  
  #download_URL = download_URL + '&kernelversion=' + platform.platform()
  #download_URL = download_URL + '&agentversion=' + agent_version
  return download_URL
#*************************************************

#*************************************************
#download SecureCloud agent
def download_file(download_url, filename):
  #if the file has already been existed, delete it
  if os.path.exists(filename):
    os.remove(filename)
    
  u = urllib2.urlopen(download_url)

  with open(filename, 'wb') as f:
    meta = u.info()
    meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
    meta_length = meta_func("Content-Length")
    file_size = None
    if meta_length:
      file_size = int(meta_length[0])
    print("Downloading File: {0} (bytes)".format(file_size))

    file_size_dl = 0
    block_sz = 8192
    while True:
      buffer = u.read(block_sz)
      if not buffer:
        break

      file_size_dl += len(buffer)
      f.write(buffer)

      status = "{0:16}".format(file_size_dl)
      if file_size:
         status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
      status += chr(13)
      sys.stdout.write(status)
    print('')

  #make sure that the file is executable
  file_mode = os.stat(filename).st_mode | stat.S_IXUSR
  os.chmod(filename, file_mode)
#*************************************************

#*************************************************
def generate_installation_command(operating_system):
  execution_command = SETUP_FILE

  if operating_system == 'Windows':
    os.chdir(TMP_FOLDER)
    execution_command = 'C:\\Windows\\System32\\msiexec /i '
    execution_command = execution_command + TMP_FOLDER + '\\fsagent.msi '
    execution_command = execution_command + '/qn /l*v C:\\btconfig\\installationlog.txt'
    #execution_command = 'veefs.exe'
    #execution_command = execution_command + ' /s'
    #execution_command = execution_command + ' /v'
    #execution_command = execution_command + '"/qn'
    #execution_command = execution_command + ' REGISTERHOSTOPTS=\\"' + SERVER_DNS + ' -agent=' + VM_DNS + ' -log=c:\\btconfig\\vmlog.txt\\""'
  else:
    os.chdir(CONFIG_FOLDER)
    execution_command = execution_command + ' -s'
    execution_command = execution_command + ' unattended.txt'
    uafile = open('unattended.txt', 'w')
    uafile.write('SERVER_HOSTNAME=' + SERVER_DNS + '\n')
    uafile.write('AGENT_HOST_NAME=' + VM_DNS + '\n')
    uafile.close()
  return execution_command
#*************************************************

#*************************************************
def get_VM_DNS(operating_system):
  global VM_DNS
  if operating_system == 'Windows':
    pass
  else: 
    vm_id_params = os.system('facter -p | grep -w appstack_server_identifier').split('=>')  
    vm_id = vm_id_params[1].trim()
    domain_params = os.system('facter -p | grep -w domain').split('=>')
    domain = domain_params[1].trim()
    VM_DNS = '%s.%s' %(vm_id, domain)
      
#*************************************************

#*************************************************
#main program
if __name__ == "__main__":
  running_mode = parse_parameters(sys.argv[1:])
  get_VM_DNS(platform.system())  
  set_variables()  
  
  #open log file
  logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='[%m/%d/%y, %H:%M:%S]',)  
  logging.info('Parameters: ' + AGENT_DOWNLOAD_URL + ',' + SERVER_DNS + ',' + SERVER_IP + ',' + VM_DNS)

  if running_mode == 0:        
    #make sure that DSM mapping exists in the hosts file
    if not check_hosts(HOSTS_FILE, SERVER_DNS): 
      logging.info('Adding server DNS-IP mapping to hosts file') 
      update_hosts(SERVER_IP, SERVER_DNS, HOSTS_FILE)

    #download installation file
    if not os.path.exists(SETUP_FILE):
      if AGENT_DOWNLOAD_URL != 'NONE':
        download_url = generate_download_URL()
        logging.info('Download Vormetric Agent: ' + download_url)
        download_file(download_url, SETUP_FILE)

    #install Vormetric agent
    if os.path.exists(SETUP_FILE):
      execution_command = generate_installation_command(platform.system())
      logging.info('Install Vormetric Agent: ' + execution_command)
      if platform.system() == 'Windows':
        open(CONFIG_FOLDER + '\\waitforrestart', 'w').close()
        os.system(execution_command)
      else:
        #not registered: /opt/vormetric/DataSecurityExpert/agent/vmd/pem/agent.pem does not exist		
        update_linux_lib()
        import pexpect
        try:
          cont = True
          child = pexpect.spawn(execution_command, timeout=None)
          while cont:
            i = child.expect(['Do you want to continue with agent registration\? \(Y/N\)'], timeout=None)
            if i == 0:
              child.sendline('Y')
              cont = False
            else:
              child.sendline('')
          child.expect(pexpect.EOF)
        except pexpect.EOF:
          pass 
    else:
      logging.info('Failed to get the agent installer')

  elif running_mode == 4:
    logging.info('Uninstall Vormetric Agent')
    if platform.system() == 'Windows':
      os.system('C:\Windows\System32\msiexec.exe /x {EDAA46C4-E8FD-417D-ADB9-7E250D45F7C9} /quiet')
    else:
      execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/uninstall'
      import pexpect	  
      try:
        cont = True
        child = pexpect.spawn(execution_command, timeout=None)
        while cont:
          i = child.expect(['Would you like to uninstall the vee-fs package\? \(Y/N\)'], timeout=None)
          if i == 0:
            child.sendline('Y')
            cont = False
          else:
            child.sendline('')
        child.expect(pexpect.EOF)
      except pexpect.EOF:
        pass

  elif running_mode == 1:
    if os.path.exists(CONFIG_FOLDER + '\\waitforrestart'):
      os.remove(CONFIG_FOLDER + '\\waitforrestart')
    else:
      if not os.path.exists(AGENT_FILE):
        logging.info('Vormetric agent has not been installed')
      else: 
        if not os.path.exists('C:\\ProgramData\\Vormetric\\DataSecurityExpert\\agent\\vmd\\pem\\agent.pem'):	  
          os.chdir('C:\\Program Files\\Vormetric\\DataSecurityExpert\\agent\\shared\\bin')
          execution_command = 'register_host.exe -vmd -agent=' + VM_DNS + ' ' + SERVER_DNS + ' -silent'
          logging.info('Register Vormetric Agent: ' + execution_command)
          os.system(execution_command)
        else:
          logging.info('Vormetric Agent has been previously registered')	

  elif running_mode == 2:
    logging.info('Run dataxform to encrypt data')
    if platform.system() == 'Windows':
      os.chdir('C:\\Program Files\\Vormetric\\DataSecurityExpert\\agent\\vmd\\bin')        
      execution_command = 'dataxform --rekey --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      os.system(execution_command)
      process = subprocess.Popen(['dataxform', '--rekey', '--nq', '--gp', GUARD_POINT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = process.communicate()
      if stdout is not None:
        lines = stdout.split('\r\n')
        for line in lines:
          if line != '':
            logging.info(line)       
      execution_command = 'dataxform --cleanup --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      process = subprocess.Popen(['dataxform', '--cleanup', '--nq', '--gp', GUARD_POINT], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = process.communicate()
      if stdout is not None:
        lines = stdout.split('\r\n')
        for line in lines:
          if line != '':
            logging.info(line) 
    else:
      execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/dataxform --rekey --nq --gp ' + GUARD_POINT      
      logging.info('Command: ' + execution_command)
      os.system(execution_command)
      execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/dataxform --cleanup --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      os.system(execution_command)
    #TODO: update facter
    #call_ws(AGENT_DOWNLOAD_URL)

  elif running_mode == 3:
    logging.info('Run dataxform to decrypt data')
    if platform.system() == 'Windows':
      os.chdir('C:\\Program Files\\Vormetric\\DataSecurityExpert\\agent\\vmd\\bin')
      execution_command = 'dataxform --rekey --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      os.system(execution_command)
      execution_command = 'dataxform --cleanup --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      os.system(execution_command)
    else:
      execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/dataxform/dataxform --rekey --nq --gp ' + GUARD_POINT      
      logging.info('Command: ' + execution_command)
      os.system(execution_command)
      execution_command = '/opt/vormetric/DataSecurityExpert/agent/vmd/bin/dataxform/dataxform --cleanup --nq --gp ' + GUARD_POINT
      logging.info('Command: ' + execution_command)
      os.system(execution_command)
    #TODO: update facter
    #call_ws(AGENT_DOWNLOAD_URL) 
#*************************************************