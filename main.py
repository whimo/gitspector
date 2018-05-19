from app import app

app.run(app.config['HOST'], app.config['PORT'], app.config['DEBUG'])