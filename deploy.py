from hapi.runtime import app

from hapi.recipe.common import bootstrap

bootstrap(app)

# ========== #

# Config

app.put('repository', 'https://github.com/laravel/laravel.git')

app.add('shared_files', [])
app.add('shared_dirs', [])
app.add('writable_dirs', [])

# Hosts

app.host(name='ubuntu-1', user='vagrant', deploy_dir='~/hapideploy/{{stage}}')

# ========== #

if __name__ == '__main__':
    app.start()
