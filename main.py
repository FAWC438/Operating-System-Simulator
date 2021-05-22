from flask import Flask


# 标记网页页面返回位置templates文件夹, 静态文件访问母路径static
app = Flask(__name__, template_folder='templates', static_url_path='/', static_folder='static')
# 配置文件silent
app.config.from_pyfile('config.py', silent=True)

if __name__ == '__main__':
    # 注册蓝图，使用controller
    from controller.index import *

    app.register_blueprint(index)

    from controller.FileSystem import *

    app.register_blueprint(file)
    from controller.Process import *

    app.register_blueprint(process)
    from controller.Memory import *

    app.register_blueprint(memory)
    from controller.IOSystem import *

    app.register_blueprint(io)
    app.run(debug=True)
