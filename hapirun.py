from hapi.core import Context

from hapi.toolbox import app

from hapi.recipe.laravel import Laravel

# Providers

app.load(Laravel)

# Configuration

app.put('name', 'Laravel')
app.put('stage', 'dev')
app.put('repository', 'https://github.com/laravel/laravel')
app.put('branch', '9.x')

# app.put('log_style', 'file') # none or buffer
# app.put('log_file', 'hapirun.log')

app.add('shared_dirs', [])
app.add('shared_files', [])
app.add('writable_dirs', [])

app.put('writable_use_sudo', True)
# app.put('writable_mode', 'chmod')
# app.put('writable_chmod_mode', '0755')
# app.put('writable_mode', 'user')
# app.put('writable_user', 'www-data')
app.put('writable_mode', 'group')
app.put('writable_group', 'www-data')
# app.put('writable_mode', 'user:group')
# app.put('writable_user', 'vagrant')
# app.put('writable_group', 'vagrant')

# Commands
@app.command(name='config:show', desc='Show a configuration key')
def command_config_show(c: Context):
    c.io().writeln('Hello World')

# Tasks

@app.task(name='composer:install', desc='Install Composer packages')
def composer_install(c: Context):
    c.info('composer install')

@app.task(name='npm:install', desc='Install NPM packages')
def npm_install(c: Context):
    c.info('npm install')

@app.task(name='npm:build', desc='Build frontend assets')
def npm_install(c: Context):
    c.info('npm run build')


# Hooks

# app.before('deploy:symlink', [
#     'composer:install',
#     'npm:install',
#     'npm:build'
# ])

app.after('deploy:writable', [
    'composer:install',
    'npm:install',
    'npm:build'
])

# app.before('deploy:code', 'composer:install')

# app.after('composer:install', 'npm:install')

# Start the Hapi program
if __name__ == '__main__':
    app.start()
