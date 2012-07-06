def create_git_repo(remote_path):
    # create a "remote" repo
    subprocess.check_call(["git", "init"], cwd=remote_path)
    subprocess.check_call(["touch", "fixed.txt"], cwd=remote_path)
    subprocess.check_call(["touch", "modified.txt"], cwd=remote_path)
    subprocess.check_call(["touch", "modified-fs.txt"], cwd=remote_path)
    subprocess.check_call(["touch", "deleted.txt"], cwd=remote_path)
    subprocess.check_call(["touch", "deleted-fs.txt"], cwd=remote_path)
    subprocess.check_call(["git", "add", "*"], cwd=remote_path)
    subprocess.check_call(["git", "commit", "-m", "modified"], cwd=remote_path)

def modify_git_repo(clone_path):
    # make local modifications
    subprocess.check_call(["rm", "deleted-fs.txt"], cwd=clone_path)
    subprocess.check_call(["git", "rm", "deleted.txt"], cwd=clone_path)
    _add_to_file(os.path.join(clone_path, "modified-fs.txt"), u"foo\n")
    _add_to_file(os.path.join(clone_path, "modified.txt"), u"foo\n")
    subprocess.check_call(["git", "add", "modified.txt"], cwd=clone_path)
    _add_to_file(os.path.join(clone_path, "added-fs.txt"), u"tada\n")
    _add_to_file(os.path.join(clone_path, "added.txt"), u"flam\n")
    subprocess.check_call(["git", "add", "added.txt"], cwd=clone_path)
    
        create_git_repo(remote_path)
        modify_git_repo(clone_path)
        self.assertEqual(0 ,cli.cmd_diff(os.path.join(self.test_root_path, 'ws'), []))
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n', output)
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n', output)
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n', output)
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n', output)
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n??      clone/added-fs.txt\n', output)
        self.assertEqual('A       clone/added.txt\n D      clone/deleted-fs.txt\nD       clone/deleted.txt\n M      clone/modified-fs.txt\nM       clone/modified.txt\n??      clone/added-fs.txt\n', output)
        AbstractSCMTest.setUp(self)
        remote_path = os.path.join(self.test_root_path, "remote")
        os.makedirs(remote_path)

        # create a "remote" repo
        subprocess.check_call(["git", "init"], cwd=remote_path)
        subprocess.check_call(["touch", "test.txt"], cwd=remote_path)
        subprocess.check_call(["git", "add", "*"], cwd=remote_path)
        subprocess.check_call(["git", "commit", "-m", "modified"], cwd=remote_path)
        po = subprocess.Popen(["git", "log", "-n", "1", "--pretty=format:\"%H\""], cwd=remote_path, stdout=subprocess.PIPE)
        self.version_init = po.stdout.read().rstrip('"').lstrip('"')[0:12]
        subprocess.check_call(["git", "tag", "footag"], cwd=remote_path)
        subprocess.check_call(["touch", "test2.txt"], cwd=remote_path)
        subprocess.check_call(["git", "add", "*"], cwd=remote_path)
        subprocess.check_call(["git", "commit", "-m", "modified"], cwd=remote_path)
        po = subprocess.Popen(["git", "log", "-n", "1", "--pretty=format:\"%H\""], cwd=remote_path, stdout=subprocess.PIPE)
        self.version_end = po.stdout.read().rstrip('"').lstrip('"')[0:12]

        # rosinstall the remote repo and fake ros
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- git: {local-name: clone, uri: ../remote}")

        cmd = ["rosws", "update"]
        sys.stdout = sys.__stdout__
        cmd = ["rosws", "info", "-t", "ws"]