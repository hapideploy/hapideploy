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

app.load('inventory.yml')

# Tasks

# Hooks

# ========== #

if __name__ == '__main__':
    app.start()
