from __future__ import print_function
import os
import shutil
import datetime

import vcstools
from vcstools import VcsClient

from common import MultiProjectException

class ConfigElement:
  """ Base class for Config provides methods with not implemented
  exceptions.  Also a few shared methods."""
  def __init__(self, path, local_name):
    self.path = path
    self.setup_file = None
    self.local_name = local_name
  def get_path(self):
    """where the config element is w.r.t. current dir or absolute"""
    return self.path
  def get_local_name(self):
    """where the config element is w.r.t. the Config base path (or absolute)"""
    return self.local_name
  def install(self, backup_path, mode, robust):
    raise NotImplementedError, "ConfigElement install unimplemented"
  def get_yaml(self):
    """yaml with values as specified in file"""
    raise NotImplementedError, "ConfigElement get_versioned_yaml unimplemented"
  def get_versioned_yaml(self):
    """yaml where VCS elements have the version looked up"""
    raise NotImplementedError, "ConfigElement get_versioned_yaml unimplemented"
  def is_vcs_element(self):
    # subclasses to override when appropriate
    return False
  def get_diff(self, basepath = None):
    raise NotImplementedError, "ConfigElement get_diff unimplemented"
  def get_status(self, basepath = None, untracked = False):
    raise NotImplementedError, "ConfigElement get_status unimplemented"
  def backup(self, backup_path):
    if not backup_path:
      raise MultiProjectException("Cannot install %s.  backup disabled."%self.path)
    backup_path = os.path.join(backup_path, os.path.basename(self.path)+"_%s"%datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    print("Backing up %s to %s"%(self.path, backup_path))
    shutil.move(self.path, backup_path)
  def __str__(self):
    return str(self.get_yaml());



class OtherConfigElement(ConfigElement):
  def install(self, backup_path, mode, robust=False):
    return True

  def get_versioned_yaml(self):
    raise MultiProjectException("Cannot generate versioned outputs with non source types")

  def get_yaml(self):
    return [{"other": {"local-name": self.get_local_name()} }]


class SetupConfigElement(ConfigElement):
  """A setup config element specifies a single file containing configuration data for a config."""

  def install(self, backup_path, mode, robust=False):
    return True

  def get_versioned_yaml(self):
    raise MultiProjectException("Cannot generate versioned outputs with non source types")
  
  def get_yaml(self):
    return [{"setup-file": {"local-name": self.get_local_name()} }]


class VCSConfigElement(ConfigElement):
  
  def __init__(self, path, vcs_client, local_name, uri, version=''):
    """
    Creates a config element for a VCS repository.
    :param path: absolute or relative path, str
    :param vcs_client: Object compatible with vcstools.VcsClientBase
    :param local_name: display name for the element, str
    :param uri: VCS uri to checkout/pull from, str
    :param version: optional revision spec (tagname, SHAID, ..., str)
    """
    ConfigElement.__init__(self, path, local_name)
    if path is None:
      raise MultiProjectException("Invalid empty path")
    if uri is None:
      raise MultiProjectException("Invalid scm entry having no uri attribute for path %s"%path)
    self.uri = uri.rstrip('/') # strip trailing slashes if defined to not be too strict #3061
    self.version = version
    if vcs_client is None:
      raise MultiProjectException("Vcs Config element can only be constructed by providing a VCS client instance")
    self.vcsc = vcs_client

  def is_vcs_element(self):
    return True
    
  def install(self, backup_path = None, arg_mode = 'abort', robust = False):
    """
    Attempt to make it so that self.path is the result of checking out / updating from remote repo
    :param arg_mode: one of prompt, backup, delete, skip. Determins how to handle error cases
    :param backup_path: if arg_mode==backup, determines where to backup to
    :param robust: if true, operation will be aborted without changes to the filesystem and without user interaction
    """
    print("Installing %s (%s) to %s"%(self.uri, self.version, self.path))

    if not self.vcsc.path_exists():
      if not self.vcsc.checkout(self.uri, self.version):
        raise MultiProjectException("Checkout of %s version %s into %s failed."%(self.uri, self.version, self.path))
    else:
      # Directory exists see what we need to do
      error_message = None
      if not self.vcsc.detect_presence():
        error_message = "Failed to detect %s presence at %s."%(self.vcsc.get_vcs_type_name(), self.path)
      elif not self.vcsc.get_url() or self.vcsc.get_url().rstrip('/') != self.uri:  #strip trailing slashes for #3269
        error_message = "url %s does not match %s requested."%(self.vcsc.get_url(), self.uri)
        
      # If robust ala continue-on-error, just error now and it will be continued at a higher level
      if robust and error_message:
          raise MultiProjectException(error_message)

      if error_message is None:
        if not self.vcsc.update(self.version):
          raise MultiProjectException("Update Failed of %s"%self.path)
      else:
        # prompt the user based on the error code
        if arg_mode == 'prompt':
          mode = prompt_del_abort_retry(error_message, allow_skip = True)
          if mode == 'backup': # you can only backup if in prompt mode
            backup_path = get_backup_path()
        else:
          mode = arg_mode
          
        if mode == 'abort':
          raise MultiProjectException(error_message)
        elif mode == 'backup':
          self.backup(backup_path)
        elif mode == 'delete':
          shutil.rmtree(self.path)
        elif mode == 'skip':
          return
      
        # If the directory now does not exist checkout
        if self.vcsc.path_exists():
          raise MultiProjectException("Bug: directory %s should not exist anymore"%(self.path))
        else:
          if not self.vcsc.checkout(self.uri, self.version):
            raise MultiProjectException("Checkout of %s version %s into %s failed."%(self.uri, self.version, self.path))
  
  def get_yaml(self):
    "yaml as from source"
    result = {self.vcsc.get_vcs_type_name(): {"local-name": self.get_local_name(), "uri": self.uri} }
    if self.version != None and self.version != '':
      result[self.vcsc.get_vcs_type_name()]["version"] = self.version
    return [result]

  def get_versioned_yaml(self):
    "yaml looking up current version"
    result = {self.vcsc.get_vcs_type_name(): {"local-name": self.get_local_name(), "uri": self.uri, "version": self.vcsc.get_version(), "revision":""} }
    if self.version != None and self.version.strip() != '':
      # revision is where local repo should be, version where it actually is
      result[self.vcsc.get_vcs_type_name()]["revision"] = self.vcsc.get_version(self.version)
    return [result]

  def get_diff(self, basepath=None):
    return self.vcsc.get_diff(basepath)
  
  def get_status(self, basepath=None, untracked=False):
    return self.vcsc.get_status(basepath, untracked)
  

  
class AVCSConfigElement(VCSConfigElement):
  """
  Implementation using vcstools vcsclient, works for types svn, git, hg, bzr, tar
  :raises: Lookup Exception for unknown types
  """
  def __init__(self, scmtype, path, local_name, uri, version = ''):
    VCSConfigElement.__init__(self, path, VcsClient(scmtype, path), local_name, uri, version)