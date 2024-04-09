from core import app_config

isDev = True

app = app_config.app(debug=True)

from route.router import router as rootRouter
app.include_router(rootRouter)

from route.api import router as apirouter
app.include_router(apirouter.apiRootRouter, prefix="/api")

