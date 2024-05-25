from core.config import app_config

isDev = True

app = app_config.app(debug=True)

from route._router import router as rootRouter
app.include_router(rootRouter)
# app.mount("/static", StaticFiles(directory="site", html = True), name="site")

