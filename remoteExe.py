import platform
from paramiko import SSHClient
from scp import SCPClient

if platform.platform().find("Linux") == 0:
    import pexpect as exp
else:
    import wexpect as exp


class SshConn:
    def __init__(self, hostname="", username="", password="", prompt_string="#"):

        self.hostname = hostname
        self.username = username
        self.password = password
        self.prompt_string = prompt_string
        self.status = "not connected"

        # Open Connection
        if platform.platform().find("Linux") == 0:
            ssh_cmd = "ssh -l " + self.username + " " + self.hostname
        else:
            # ssh_cmd = "\"C:\\Program Files\\Git\\usr\\bin\\ssh.exe\" " + self.username + "@" + self.hostname
            # ssh_cmd = "ssh.exe " + self.username + "@" + self.hostname
            ssh_cmd = "ssh.exe -l " + self.username + " " + self.hostname

        print("\n\nCmd", ssh_cmd)
        self.conn = exp.spawn(ssh_cmd)

        # Wait for password prompt
        # expect_prompt = [f"{username}@{hostname}\'s password:"]
        expect_prompt = ["password:"]
        try:
            self.conn.expect(expect_prompt)
            self.conn.sendline(self.password)
        except Exception as e:
            print("SSH Failed: ", e)
            self.status = "connection failed"
            return

        self.status = "connected"

        if platform.platform().find("Linux") == 0:
            self.conn.setecho(False)

        pass

    # Exits the ssh connection
    def ssh_exit(self):
        print(f"Running: ssh exit...")

        if platform.platform().find("Linux") == 0:
            self.conn.sendline("exit")
            print(self.conn.after.decode('utf-8'))
        else:
            self.conn.sendline("exit")
            print(self.conn.after)

        self.conn.close()

    def run_cmd(self, cmd, timeout=5, prompt_string=None):
        if prompt_string is None:
            prompt_string = self.prompt_string

        print("Running: ", cmd)
        if platform.platform().find("Linux") == 0:
            self.conn.sendline(cmd)
            self.conn.expect([prompt_string.encode('utf-8')], timeout=timeout)
            self.conn.sendline("")
            self.conn.expect([prompt_string.encode('utf-8')], timeout=timeout)
            ret_val = self.conn.before.decode('utf-8')

        else:
            self.conn.sendline(cmd)
            self.conn.expect(prompt_string, timeout=timeout)
            ret_val = self.conn.before

        return ret_val

    '''
    src_file_list: mandatory
    if dst_location is not present:
        dst_file_list is mandatory.
    '''
    def scp_put(self, src_location="", src_file_list=(), dst_location="", dst_file_list=()):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(self.hostname, username=self.username, password=self.password)

        with SCPClient(ssh.get_transport()) as scp:
            for idx, file in enumerate(src_file_list):
                src_file = src_location + file

                if 0 == len(dst_file_list):
                    dst_file = dst_location + src_file.split("/")[-1]
                else:
                    if 0 == len(dst_location):
                        dst_file = dst_file_list[idx]
                    else:
                        dst_file = dst_location + dst_file_list[idx].split("/")[-1]

                scp.put(src_file, dst_file)
                print(f"Copying: local:{src_file} to Hostname({self.hostname}):{dst_file}")

    '''
    src_file_list: mandatory
    if dst_location is not present:
        dst_file_list is mandatory.
    '''
    def scp_get(self, src_location="", src_file_list=(), dst_location="", dst_file_list=()):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(self.hostname, username=self.username, password=self.password)

        with SCPClient(ssh.get_transport()) as scp:
            for idx, file in enumerate(src_file_list):
                src_file = src_location + file

                if 0 == len(dst_file_list):
                    dst_file = dst_location + src_file.split("/")[-1]
                else:
                    if 0 == len(dst_location):
                        dst_file = dst_file_list[idx]
                    else:
                        dst_file = dst_location + dst_file_list[idx].split("/")[-1]

                scp.get(src_file, dst_file)
                print(f"Copying:  Hostname({self.hostname}):{src_file} to local:{dst_file}")


if __name__ == "__main__":
    conn = SshConn("ral-abroyvm", username="abroy", password="Root@123", prompt_string="abroy@ral-abroyvm:")
    # conn = SshConn("10.0.0.2", username="root", password="itron")

    if conn.status == "connected":
        ret = conn.run_cmd("ifconfig")
        print(ret)

        # Copy src files to remote server
        # conn.scp_put(src_file_list=["common.c", "common.h", "mtfRelay.c", "mtfApp.c"],
        #              dst_location="/home/abroy/itronGit/CustomApp/")

        # conn.scp_put(src_file_list=["common.c", "common.h", "mtfRelay.c", "mtfApp.c"],
        #              dst_file_list=["/home/abroy/itronGit/CustomApp/common.c",
        #                             "/home/abroy/itronGit/CustomApp/common.h",
        #                             "/home/abroy/itronGit/CustomApp/mtfRelay.c",
        #                             "/home/abroy/itronGit/CustomApp/mtfApp.c"])

        conn.scp_put(src_location="./",
                     src_file_list=["common.c", "common.h", "mtfRelay.c", "mtfApp.c"],
                     dst_location="/home/abroy/itronGit/CustomApp/",
                     dst_file_list=["common.c", "common.h", "mtfRelay.c", "mtfApp.c"])

        # conn.scp_put(src_file_list=["bin/mtfApp", "bin/mtfRelay"],
        #              dst_location="/mnt/common/lkmtestfw/")

        conn.ssh_exit()


# That's all
