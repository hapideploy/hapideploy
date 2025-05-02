A remote is a server in general, but can be any kind of device that you can SSH into it.

## Defining a remote

In the `inventory.yml` file, you can define remotes like this.

```yaml
remotes:
  a.hapideploy.com:
  b.hapideploy.com:
  c.hapideploy.com:
```

This case, `a.hapideploy.com` will be the hostname for SSH connections. It's also the label displayed whenever a task is executed against the remote. It's similar to `b.hapideploy.com` and `c.hapideploy.com`. E.g., Running "hapi whoami" will print these three lines.

```plain
[a.hapideploy.com] TASK whoami
[b.hapideploy.com] TASK whoami
[c.hapideploy.com] TASK whoami
```

Above, I assume each `*.hapideploy.com` is a host alias in `~/.ssh/config` file. But, you can explicitly define a remote with a list of key-value pairs.

```yaml
remotes:
  # "hapideploy.com" is the remote label.
  hapideploy.com:
    # SSH host(name)
    host: 192.68.33.10
    # SSH port
    port: 22
    # SSH user
    user: vagrant
    # The private key path
    identity_file: ~/.ssh/id_ed25519
```

## Overriding configurations

Imagine, you've already defined `deploy_path` configuration in the `deploy.py` file.

```python
from hapi.cli import app

app.put('deploy_path', '~/deploy')

```

You can override it using the `with` section under a remote item.

```yaml
remotes:
  hapideploy.com:
    with:
      deploy_path: "/path/to/somewhere"
```

## List remotes

You can list all defined remotes using the `remote:list` command

```bash
hapi remote:list
```
