# from hapi import Deployer

from hapi.toolbox import app

from hapi.recipe.common import bootstrap

bootstrap(app)

app.put('name', 'Laravel')
app.put('stage', 'dev')
app.put('repository', 'https://github.com/laravel/laravel')

app.start()
