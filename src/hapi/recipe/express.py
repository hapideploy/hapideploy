from ..core import Provider
from .__node import (
    bin_npm,
    bin_pm2,
    npm_ci,
    pm2_del,
    pm2_process_name,
    pm2_start,
    pm2_stop,
)
from .common import Common


class Express(Provider):
    def register(self):
        self.app.load(Common)

        self.app.put("shared_files", [".env"])

        self.app.put("node_version", "20.19.0")
        self.app.put("pm2_start_script_path", "{{release_path}}/bin/www")

        self.app.bind("bin/npm", bin_npm)
        self.app.bind("bin/pm2", bin_pm2)
        self.app.bind("pm2_process_name", pm2_process_name)

        self._register_tasks()

        self.app.define_group(
            "deploy:main",
            "Deploy main activities",
            [
                "npm:ci",
                "pm2:stop",
                "pm2:del",
                "pm2:start",
            ],
        )

    def _register_tasks(self):
        for name, desc, func in [
            ("npm:ci", "Clean install NPM packages", npm_ci),
            ("pm2:stop", "Stop the current pm2 process", pm2_stop),
            ("pm2:del", "Delete the current pm2 process", pm2_del),
            ("pm2:start", "Start the new pm2 process", pm2_start),
        ]:
            self.app.define_task(name, desc, func)
