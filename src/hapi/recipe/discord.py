import requests

from ..core import Context, Provider


def deploy_discord(c: Context):
    name = c.cook("name")
    release_name = c.cook("release_name")
    current_path = c.cook("current_path")
    commit_hash = c.cat(f" {current_path}/REVISION")
    stage = c.cook("stage")
    url_str = c.cook("url")

    content = (
        f"[{name}] The release **{release_name}** (commit hash: `{commit_hash}`) is deployed to **{c.remote.label}** (stage: `{stage}`).\n"
        f"    -> Please check at {url_str}"
    )

    payload = {"content": content}

    try:
        discord = c.cook("discord")

        response = requests.post(discord["webhook_url"], json=payload)
        response.raise_for_status()  # Check for HTTP errors
        c.info(f"✅ Notification sent to Discord for {release_name}.")

    except requests.exceptions.HTTPError as err:
        # TODO: c.warning()
        c.info(
            f"⚠️ Failed to send Discord notification: HTTP Error {err.response.status_code}"
        )
        # Optional: Print response text to debug (e.g. if Discord rejects format)
        c.info(err.response.text)

    except Exception as e:
        c.info(f"⚠️ An unexpected error occurred sending notification: {e}")


class Discord(Provider):
    def register(self):
        self.app.put("webhook_url", "https://discord.com/api/webhooks/xxx/yyy")

        self.app.define_task(
            "deploy:discord",
            "Send a message to Discord to notify a successful deployment",
            deploy_discord,
        )

        self.app.after("deploy:end", "deploy:discord")
