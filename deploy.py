from hapi.runtime import app

# Config

app.put('repository', 'https://github.com/laravel/laravel.git')

app.add('shared_files', [])
app.add('shared_dirs', [])
app.add('writable_dirs', [])

# Hosts

app.host(name='ubuntu-1', user='vagrant', deploy_dir='~/hapideploy/{{stage}}')
app.host(name='ubuntu-2', user='vagrant', deploy_dir='~/hapideploy/{{stage}}')
app.host(name='ubuntu-3', user='vagrant', deploy_dir='~/hapideploy/{{stage}}')

if __name__ == '__main__':
    app.start()
