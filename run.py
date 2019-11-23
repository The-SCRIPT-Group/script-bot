from os.path import join

from waitress import serve

from web_app import app

if __name__ == '__main__':
    app.template_folder = join('web_app', app.template_folder)
    serve(app=app)
