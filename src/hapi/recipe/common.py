import json

from ..core import Deployer, Program


def bootstrap(app: Program):
    return CommonProvider(app)


class CommonProvider:
    def __init__(self, app: Program):
        self.app = app

        self.boot()

    def boot(self):
        self.app.deployer.bind('bin/symlink', self.bin_symlink)
        self.app.deployer.bind('releases_log', self.releases_log)
        self.app.deployer.bind('release_list', self.release_list)

        self.app.deployer.add_task("deploy", "Run deployment tasks", self.deploy)
        self.app.deployer.add_task(
            "deploy:start", "Start the deployment process", self.deploy_start
        )
        self.app.deployer.add_task(
            "deploy:setup", "Prepare the deployment directory", self.deploy_setup
        )

        self.app.deployer.add_task('deploy:release', 'Prepare the release candidate', self.deploy_release)

        self.app.deployer.add_task(
            "deploy:lock", "Lock the deployment process", self.deploy_lock
        )
        self.app.deployer.add_task(
            "deploy:unlock", "Unlock the deployment process", self.deploy_unlock
        )

    def bin_symlink(self, _: Deployer):
        # return 'ln -nfs --relative' if dep.make('use_relative_symlink') else 'ln -nfs'
        return 'ln -nfs'


    def releases_log(self, dep: Deployer):
        import json

        dep.cd('{{deploy_dir}}')

        if dep.test('[ -f .dep/releases_log ]') is False:
            return []

        lines = dep.run('tail -n 300 .dep/releases_log').fetch().split('\n')
        releases = []
        for line in lines:
            releases.insert(0, json.loads(line))
        return releases

    def release_list(dep: Deployer):
        dep.cd('{{deploy_dir}}')

        if dep.test('[ -d releases ] && [ "$(ls -A releases)" ]') is False:
            return []

        ll = dep.run('cd releases && ls -t -1 -d */').fetch().split('\n')
        ll = list(map(lambda x: x.strip('/'), ll))

        releases_log = dep.make('releases_log')

        releases = []

        for candidate in releases_log:
            if candidate['release_name'] in ll:
                releases.append(candidate['release_name'])

        return releases

    def deploy(self, dep: Deployer):
        dep.put("current_file", "{{deploy_dir}}/current")

        dep.run_tasks(
            [
                "deploy:start",
                "deploy:setup",
                "deploy:lock",
                "deploy:release",
                "deploy:unlock",
            ]
        )

    def deploy_start(self, dep: Deployer):
        release_name = (
            int(dep.cat("{{deploy_dir}}/.dep/latest_release")) + 1
            if dep.test("[ -f {{deploy_dir}}/.dep/latest_release ]")
            else 1
        )

        dep.put("release_name", release_name)

        dep.info("Deploying {{name}} to {{stage}} (release {{release_name}})")

    def deploy_setup(self, dep: Deployer):
        command = """[ -d {{deploy_dir}} ] || mkdir -p {{deploy_dir}};
cd {{deploy_dir}};
[ -d .dep ] || mkdir .dep;
[ -d releases ] || mkdir releases;
[ -d shared ] || mkdir shared;"""

        dep.run(command)

        if dep.test("[ ! -L {{current_file}} ] && [ -d {{current_file}} ]"):
            dep.stop(
                "There is a directory (not symlink) at {{current_file}}.\n Remove this directory so it can be replaced with a symlink for atomic deployments."
            )

        dep.info("The {{deploy_dir}} is ready for deployment")

    def deploy_release(self, dep: Deployer):
        dep.cd('{{deploy_dir}}')

        if dep.test('[ -h release ]'):
            dep.run('rm release')

        release_list = dep.make('release_list')
        release_name = dep.make('release_name')
        release_dir = f"releases/{release_name}"

        if dep.test(f"[ -d {release_dir} ]"):
            dep.stop(f"Release name \"{release_name}\" already exists.\nIt can be overridden via:\n -o release_name={release_name}")

        dep.run("echo {{release_name}} > {{deploy_dir}}/.dep/latest_release")

        import time
        timestamp = time.time()
        import getpass

        user = getpass.getuser()
        candidate = {
            'created_at': timestamp,
            'release_name': release_name,
            'user': user,
            'target': dep.make('branch')
        }

        candidate_json = json.dumps(candidate)

        dep.run(f"echo '{candidate_json}' >> .dep/releases_log");

        dep.run(f"mkdir -p {release_dir}");

        dep.run("{{bin/symlink}} " + release_dir + " {{deploy_dir}}/release");

        release_list.insert(0, release_name)
        dep.bind('release_list', release_list)

        if len(release_list) >= 2:
            dep.bind('previous_release', "{{deploy_dir}}/releases/" + release_list[1])

    def deploy_lock(self, dep: Deployer):
        import getpass

        user = getpass.getuser()
        locked = dep.run(
            "[ -f {{deploy_dir}}/.dep/deploy.lock ] && echo +locked || echo "
            + user
            + " > {{deploy_dir}}/.dep/deploy.lock"
        ).fetch()

        if locked == "+locked":
            locked_user = dep.run("cat {{deploy_dir}}/.dep/deploy.lock").fetch()
            dep.stop(
                "Deployment process is locked by "
                + locked_user
                + ".\n"
                + 'Execute "deploy:unlock" task to unlock.'
            )

        dep.info(
            "Deployment process is locked by "
            + user
            + " (release_name: {{release_name}})"
        )

    def deploy_unlock(self, dep: Deployer):
        dep.run("rm -f {{deploy_dir}}/.dep/deploy.lock")

        dep.info("Deployment process is unlocked.")
