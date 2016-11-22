from fabric.context_managers import cd, settings
from fabric.exceptions import CommandTimeout
from fabric.network import disconnect_all
from fabric.operations import run, get, put, local
from fabric.state import env
import StringIO

env.shell = "/bin/ksh"
env.warn_only = True


class SSHHelper(object):

    def __init__(self, key_location=None, user=None):
        self.ssh_key = key_location
        self.user = user

    def get_ssh_key(self):
        return self.ssh_key

    def get_ssh_user(self):
        return self.user

    @staticmethod
    def execute_loacl_command(command):
        response_dict = dict()
        with settings(warn_only=True):
            response = local(command, capture=True, shell=None)
        if response.failed:
            response_dict['status'] = '1'
            response_dict['output'] = response
            response_dict['message'] = response.stderr
        else:
            response_dict['status'] = '0'
            response_dict['message'] = response.stdout
            response_dict['output'] = response
        response_dict['return_code'] = response.return_code
        return response_dict

    def execute_remote_command(self, hostname, command, shell=True, pty=True, timeout=180):
        response_dict = dict()
        stdout_msg = StringIO.StringIO()
        stderr_msg = StringIO.StringIO()
        try:
            ssh_user = self.get_ssh_user()
            if ssh_user:
                print 'Running ssh command {0} on host {1} using user:{2}'.format(command, hostname, ssh_user)

                with settings(host_string=hostname, user=ssh_user,
                              key_filename=self.ssh_key, warn_only=True):
                    response = run(
                        command, shell=shell, pty=pty,
                        combine_stderr=None, quiet=False,
                        warn_only=False, stdout=stdout_msg,
                        stderr=stderr_msg, timeout=timeout,
                        shell_escape=None)

                    print 'Response: {0}, return code: {1}, stdout: {2} stderror:{3}'.format(
                        str(response), response.return_code, stdout_msg.getvalue(), stderr_msg.getvalue()
                    )
                if response.failed:
                    response_dict['status'] = '1'
                    response_dict['output'] = response
                    response_dict['message'] = stderr_msg.getvalue()
                else:
                    response_dict['status'] = '0'
                    response_dict['message'] = stdout_msg.getvalue()
                    response_dict['output'] = response
                response_dict['return_code'] = response.return_code
        except CommandTimeout as e:
            response_dict['status'] = '1'
            response_dict['message'] = ('Command execution time out '
                                        'after 180 seconds')
            print 'Command execution time out after 180 seconds'
        except Exception as e:
            response_dict['status'] = '1'
            response_dict['message'] = 'Exception occurred - {0}'.format(e.message)
            print 'Exception occurred in execute_remote_command'

        finally:
            disconnect_all()
        return response_dict

    def execute_by_location(self, directory, hostname, command):
        response_dict = dict()
        stdout_msg = StringIO.StringIO()
        stderr_msg = StringIO.StringIO()
        try:
            ssh_user = self.get_ssh_user()
            if ssh_user:
                with settings(host_string=hostname, user=ssh_user,
                              key_filename=self.ssh_key, warn_only=True):
                    with cd(directory):
                        response = run(
                            command, shell=True, pty=True,
                            combine_stderr=None, quiet=False,
                            warn_only=False, stdout=stdout_msg,
                            stderr=stderr_msg, timeout=180,
                            shell_escape=None)

                if response.failed:
                    response_dict['status'] = '1'
                    response_dict['message'] = stderr_msg.getvalue()
                else:
                    response_dict['status'] = '0'
                    response_dict['message'] = stdout_msg.getvalue()
                    response_dict['output'] = response
                response_dict['return_code'] = response.return_code

                print 'Response: {0}, return code: {1}, stdout: {2}, stderror: {3}'.format(
                    str(response), response.return_code, stdout_msg.getvalue(), stderr_msg.getvalue()
                )

        except CommandTimeout as e:
            response_dict['status'] = '1'
            response_dict['message'] = ('Command execution time out after '
                                        '180 seconds')
            print 'Command execution time out after 180 seconds'
        except Exception as e:
            response_dict['status'] = '1'
            response_dict['message'] = 'Exception occurred -' + e.message
            print 'Exception message: {0}'.format(e.message)
        finally:
            disconnect_all()
        return response_dict

    def get_file_contents(self, hostname, host_type, filename):
        response_dict = dict()
        fd = StringIO.StringIO()
        try:
            ssh_user = self.get_ssh_user()
            if ssh_user:
                with settings(host_string=hostname, user=ssh_user,
                              key_filename=self.ssh_key, warn_only=False):
                    status = get(filename, fd)
                if status.failed:
                    response_dict['status'] = '1'
                    response_dict['output'] = status
                else:
                    response_dict['status'] = '0'
                    response_dict['output'] = fd.getvalue()
        except Exception as e:
            response_dict['status'] = '1'
            response_dict['output'] = e.message
        finally:
            disconnect_all()
        return response_dict

    def get_remote_file(self, hostname, remote_file, local_path):
        response_dict = dict()
        try:
            ssh_user = self.get_ssh_user()
            if ssh_user:
                with settings(host_string=hostname, user=ssh_user,
                              key_filename=self.ssh_key, warn_only=False,
                              timeout=180):
                    status = get(remote_file, local_path)
                if status.failed:
                    response_dict['status'] = '1'
                    response_dict['output'] = status
                    response_dict['return_code'] = 1
                else:
                    response_dict['status'] = '0'
                    response_dict['output'] = status
                    response_dict['return_code'] = 0

                print 'Response: {0}, Return code: {1}'.format(
                    str(status), response_dict['return_code']
                )

        except Exception as e:
            print 'failed to get file content.'
            response_dict['status'] = '1'
            response_dict['output'] = e.message
        finally:
            disconnect_all()
        return response_dict

    def send_file(self, hostname, local_file, remote_path):
        response_dict = dict()
        try:
            ssh_user = self.get_ssh_user()
            if ssh_user:
                with settings(host_string=hostname, user=ssh_user,
                              key_filename=self.ssh_key, warn_only=False,
                              timeout=180):
                    status = put(local_file, remote_path)
                if status.failed:
                    response_dict['status'] = '1'
                    response_dict['output'] = status
                    response_dict['return_code'] = 1
                else:
                    response_dict['status'] = '0'
                    response_dict['output'] = status
                    response_dict['return_code'] = 0

                print 'Response: {0}, Return code: {1}'.format(
                    str(status), response_dict['return_code']
                )

        except Exception as e:
            response_dict['status'] = '1'
            response_dict['output'] = e.message
        finally:
            disconnect_all()
        return response_dict
