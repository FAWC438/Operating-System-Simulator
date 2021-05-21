from flask import Flask


app = Flask(__name__, template_folder='templates', static_url_path='/', static_folder='static')
app.config.from_pyfile('config.py', silent=True)

if __name__ == '__main__':

    from controller.index import *

    app.register_blueprint(index)

    from controller.FileSystem import *

    app.register_blueprint(file)
    from controller.Process import *

    app.register_blueprint(process)
    from controller.Memory import *

    app.register_blueprint(memory)

    app.run(debug=True)
