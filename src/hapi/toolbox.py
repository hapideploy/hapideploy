from .core.program import Program

app = Program()

app.set_instance(app)

# Public API methods

# Group 1: Load service providers
# app.load(SampleProvider) -> from Program
# app.discover('/path/to/inventory.yml') -> from Program
# app.remote(host='127.0.0.1', port=2200, user=vagrant, pemfile='/path/to/pemfile', deploy_dir='~/deploy/{{stage}}') -> from Program

# Group 2:
# app.put(key, value) -> from Container
# app.add(key, value) -> from Container
# app.make(key, fallback, throw=True) -> from Container
# app.parse('{{release_name}}') -> from Container
# @app.resolve(key, resolve_func) -> from Container

# Group 3:
# @app.command(name, desc) -> from Deployer
# @app.task(name, desc) -> from Program
# app.group(name, desc, do) -> from Program
# TODO: app.before(name, do)
# TODO: app.after(name, do)

# Group 4:
# app.run(command, **kwargs) -> from Deployer
# app.cat(command, **kwargs) -> from Deployer
# app.test(command) -> from Deployer
# app.cd(location) -> from Deployer
# app.info('Display an info message.') -> from Deployer
# app.warn('Display a warn message.') -> from Deployer
# app.stop('Something went wrong.') -> from Deployer
# app.current_route() -> from Deployer

# app.start()
