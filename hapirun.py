from hapi.core import Deployer

from hapi.toolbox import app

from hapi.recipe.laravel import Laravel

# Providers

app.load(Laravel)

# Configuration

app.put('name', 'Laravel')
app.put('stage', 'dev')
app.put('repository', 'https://github.com/laravel/laravel')

app.put('log_style', 'file') # none or buffer
app.put('log_file', 'hapirun.log')

app.add('languages', ['JavaScript', 'PHP', "Python"])
app.add('languages', ['Java', 'Go', 'Rust'])
app.add('languages', 'Bash')

app.add('shared_dirs', [])
app.add('shared_files', [])
app.add('writable_dirs', [])

app.put('writable_use_sudo', True)
app.put('writable_mode', 'chmod')
app.put('writable_chmod_mode', '0755')
# app.put('writable_mode', 'user')
# app.put('writable_user', 'www-data')
# app.put('writable_mode', 'group')
# app.put('writable_group', 'www-data')
# app.put('writable_mode', 'user:group')
# app.put('writable_user', 'vagrant')
# app.put('writable_group', 'vagrant')

app.put('use_atomic_symlink', True)

@app.resolve(key='colors')
def resolve_colors(dep: Deployer):
    dep.info('Resolving "colors"')
    return ['Red', 'Green', 'Blue']

# Tasks or Commands

@app.command(name='config:list', desc='List defined configuration items')
def config_list(dep: Deployer):
    print(dep.parse('name is {{name}}'))

@app.task(name='deploy:sample', desc='This is a sample task')
def deploy_sample(dep: Deployer):
    if not dep.test('[ -d {{deploy_dir}}/shared/storage ]'):
        dep.info('{{deploy_dir}}/shared/storage does not exist or is not a directory')

    dep.cd('{{deploy_dir}}')
    dep.run('ls -lah')

    dep.info('languages:')
    print(dep.make('languages'))
    print(dep.make('colors'))


app.group('ship', 'We must ship', [
    'deploy'
])

# Hooks

# app.before('deploy:code', 'composer:install')

# app.after('composer:install', 'npm:install')

# Start the Hapi program
if __name__ == '__main__':
    app.start()
