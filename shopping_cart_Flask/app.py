from flask import Flask
from flask_restful import Api
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from flask_jwt_extended import JWTManager
from user import Add, Cart, Search, Login, Registration, Delete, Search_all

app = Flask(__name__)
api = Api(app)

# 像操作字典dict一樣的設定方式
app.config["DEBUG"] = True
app.config["JWT_SECRET_KEY"] = "secret_key"
# Swagger 
# 透過字典dict的update方法設定資料的內容
app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Shopping Cart Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)


api.add_resource(Login, '/login')
docs.register(Login)
api.add_resource(Registration, '/reg')
docs.register(Registration)
api.add_resource(Add, '/user')
docs.register(Add)
api.add_resource(Cart, '/user/<int:id>')
docs.register(Cart)
api.add_resource(Delete, '/user/<int:user_id>/<int:order_number>')
docs.register(Delete)
api.add_resource(Search_all, '/search_all')
docs.register(Search_all)
api.add_resource(Search, '/search')
docs.register(Search)


if __name__ == '__main__':
    JWTManager().init_app(app)
    app.run()