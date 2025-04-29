A remote is a server or device that you can SSH into it.

## Defining a remote

In the `inventory.yml` file, you can define remotes like this.

```yaml
hosts:
  a.hapideploy.com:
  b.hapideploy.com:
  c.hapideploy.com:
```

`a.hapideploy.com` will be the host for SSH connections and also be the label displayed whenever a task is executed against it. It's similar to `b.hapideploy.com` and `c.hapideploy.com`.

Each remote contains a list of key-value items, you can also explicitly define all of them.

```yaml
hosts:
  hapideploy.com:
    host: 192.68.33.10
    port: 22
    user: vagrant
    identity_file: ~/.ssh/id_ed25519
```

## Overriding configurations

Imagine, you've already defined `deploy_path` configuration in the `deploy.py` file.

```python
from hapi.cli import app

app.put('deploy_path', '~/deploy')

```

You can override it using the `with` section under a host item.

```yaml
hosts:
  hapideploy.com:
    with:
      deploy_path: "/path/to/somewhere"
```

## Full configurations

These are all available configurations for a remote.

```yaml
hosts:
  hapideploy.com:

    # SSH host(name)
    host: 192.68.33.10
    
    # SSH port
    port: 22
    
    # SSH user
    user: vagrant
    
    # The identity file location 
    identity_file: ~/.ssh/id_ed25519

    # If the label key does not exist, "hapideploy.com" will be trust as the remote label.
    # label: 'server-1'
```

## List remotes

You can list all defined remotes using the `remote:list` command

```bash
hapi remote:list
```
