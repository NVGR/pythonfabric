from fabric_util import SSHHelper


def invoke_local_call(command):
    ssh_obj = SSHHelper()
    resp = ssh_obj.execute_loacl_command(command)
    print resp


def invoke_remote_call(hostname, command):
    ssh_obj = SSHHelper()
    resp = ssh_obj.execute_remote_command(hostname, command)
    print resp

if __name__ == '__main__':
    invoke_local_call('ls -lrt')
    invoke_remote_call(hostname='', command='')
