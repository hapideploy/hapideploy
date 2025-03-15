from hapi import RunResult
from hapi.core import CacheInputOutput, Deployer, Remote, Runner
from hapi.log import NoneStyle


class DummyResult(RunResult):
    def __init__(self):
        super().__init__()

    def fetch(self):
        return "+true"


class DummyRunner(Runner):
    def _do_run_command(self, remote: Remote, command: str, **kwargs):
        self.deployer.add("run", command)
        return DummyResult()


def test_run_command():
    deployer = Deployer(CacheInputOutput(), NoneStyle())

    def sample(dep: Deployer):
        dep.run("mkdir -p {{deploy_dir}}/.dep")  # run[0]
        dep.test("[ ! -d {{deploy_dir}}/.dep ]")  # run[1]
        dep.cat("{{deploy_dir}}/.dep/latest_release")  # run[2]

        dep.cd("{{deploy_dir}}")

        dep.run("mkdir -p .dep")  # run[3]
        dep.test("[ ! -d .dep ]")  # run[4]
        dep.cat(".dep/latest_release")  # run[2]

    remote = deployer.add_remote(
        host="127.0.0.1", port=2201, user="vagrant", deploy_dir="~/deploy/{{stage}}"
    )
    deployer.add_task("sample", "This is a sample task", sample)

    deployer.put("current_remote", remote)

    deployer.bootstrap(runner=DummyRunner(deployer))

    deployer.run_task("sample")

    run = deployer.make("run")

    assert run[0] == "mkdir -p ~/deploy/dev/.dep"
    assert run[1] == "if [ ! -d ~/deploy/dev/.dep ]; then echo +true; fi"
    assert run[2] == "cat ~/deploy/dev/.dep/latest_release"

    assert run[3] == "cd ~/deploy/dev && (mkdir -p .dep)"
    assert run[4] == "cd ~/deploy/dev && (if [ ! -d .dep ]; then echo +true; fi)"
    assert run[5] == "cd ~/deploy/dev && (cat .dep/latest_release)"
