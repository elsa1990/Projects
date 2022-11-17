from flask_restful import reqparse
import pymysql
# from flask import jsonify
from flask_apispec import doc, use_kwargs, MethodResource, marshal_with
from flask_jwt_extended import create_access_token, jwt_required
from datetime import timedelta
import route_model
import utility


# MySql connection
def db_init(): 
    db = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='',
        port=3306,
        db='test'
    )
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return db, cursor


# token*30days
def get_access_token(account):
    token = create_access_token(
        identity={"account": account},
        expires_delta=timedelta(days=30))
    return token 

# Log in
class Login(MethodResource):
    @doc(description='User Login', tags=['Login'])
    @use_kwargs(route_model.LoginSchema, location="json")
    # @marshal_with(user_router_model.UserGetResponse, code=200)
    def post(self, **kwargs):
        db, cursor = db_init()
        account, password = kwargs["account"], kwargs["password"]
        sql_user = f"SELECT * FROM test.user WHERE account = '{account}' AND password = '{password}';"
        cursor.execute(sql_user)
        user = cursor.fetchall() 
        db.close()

        if user != ():
            token = get_access_token(account)
            data = {
                "message": f"Welcome back {user[0]['name']}",
                "token": token}
            return utility.success(data)
        
        return utility.failure({"error message":"Log in failed"})


# account registration
class Registration(MethodResource):
    @doc(description='User Registration', tags=['Registration'])
    @use_kwargs(route_model.RegistrationSchema,location="json")
    @marshal_with(route_model.UserCommonResponse, code=200)
    def post(self, **kwargs):
        db, cursor = db_init()

        user = {
            "name": kwargs["name"],
            "account": kwargs["account"],
            "password": kwargs["password"],
            "gender": kwargs["gender"],
            "birthdate": kwargs["birthdate"]
        }

        sql_account = '''
            SELECT * FROM test.user;
        '''
        cursor.execute(sql_account)
        result_account = cursor.fetchall()
        db.commit()

        list_=[]
        for account in result_account:
            list_.append(account["account"])

        if user["account"] not in list_:
            sql = """
                INSERT INTO `test`.`user` (`name`,`account`,`password`,`gender`,`birthdate`)
                VALUES ('{}','{}','{}','{}','{}');
                """.format(user["name"], user["account"], user["password"], user["gender"], user["birthdate"])
            cursor.execute(sql)
            db.commit()
            db.close()
            return utility.success()
            
        else:
            return utility.failure({"message": "account existed"})


# get info of all products
class Search_all(MethodResource):
    @doc(description="Information of all products.", tags=["Search all"])
    @marshal_with(route_model.UserCommonResponse, code=200)
    # @jwt_required()
    def get(self):
        db, cursor = db_init()

        sql = '''
            SELECT * FROM test.product;
        '''
        cursor.execute(sql)
        users = cursor.fetchall()
        db.close()
        return utility.success(users)


# fuzzy search
class Search(MethodResource):
    @doc(description='Get products information.', tags=['Search'])
    @use_kwargs(route_model.UserGetSchema,location="json")
    @marshal_with(route_model.UserGetResponse, code=200)
    @jwt_required()
    def get(self, **kwargs):
        db, cursor = db_init() 
        user = {
            'name': kwargs.get("name")
        }
        
        sql_fuzzy = '''
            SELECT * FROM test.product where name like '%{}%';
        '''.format(user['name'])

        cursor.execute(sql_fuzzy)
        fuzzy = cursor.fetchall()
        db.commit()
        db.close()
        return utility.success(fuzzy)


# add to the cart    
class Add(MethodResource):
    @doc(description="add products to the cart.", tags=["Shopping Cart"])
    @use_kwargs(route_model.UserPostSchema,location="json")
    @marshal_with(route_model.UserPostResponse, code=201)
    @jwt_required()
    def post(self, **kwargs):
        db, cursor = db_init()

        user = {
            "product_name": kwargs["product_name"],
            "user_id": int(kwargs["user_id"]),
            "amount": int(kwargs["amount"])
        }

        # check stock first
        sql_check_stock = f"SELECT * FROM test.product WHERE name = '{user['product_name']}';"
        cursor.execute(sql_check_stock)
        
        check_stock = cursor.fetchall()
        if check_stock == ():
            db.close()
            return ({"message": "item required doesn't exist"})

        if check_stock[0]['amount'] < user['amount']:
            db.close()
            return ({"message": "understock"})

        sql_buy = '''
            INSERT INTO `test`.`cart` (`product_name`,`user_id`,`amount`)
            VALUES ('{}','{}','{}');
        '''.format(user['product_name'], user['user_id'], user['amount'])

        result = cursor.execute(sql_buy)
        db.commit()

        amount_left =check_stock[0]['amount'] - user['amount']

        sql_stock = '''
            UPDATE test.product
            SET amount = {}
            WHERE name = '{}';
        '''.format(amount_left, user['product_name'])

        cursor.execute(sql_stock)
        db.commit()

        sql_cart = '''
            SELECT * FROM test.cart 
            where cart.user_id = '{}';
        '''.format(user['user_id'])

        cursor.execute(sql_cart)
        db.commit()
        item_list = cursor.fetchall()

        sql_sum = '''
            SELECT sum(cart.amount*product.price) as sum FROM `cart`,`product` 
            where cart.product_name = product.name and cart.user_id = '{}';
        '''.format(user['user_id'])
   
        cursor.execute(sql_sum)
        db.commit()
        total_price = cursor.fetchone()
        db.commit()
        db.close()
        
        if result == 1:
            return utility.total(item_list, total_price)
        else:
            return utility.failure()


# use patch to change the amount
class Cart(MethodResource):
    @doc(description='change product amount in cart.', tags=['Shopping Cart'])
    @use_kwargs(route_model.UserPatchSchema,location="json")
    # @marshal_with(route_model.UserPostResponse, code=201)
    # @jwt_required()
    def patch(self, id, **kwargs):
        db, cursor = db_init()
        
        user = {
            'order_number': kwargs.get('order_number'),
            'product_name': kwargs.get('product_name'),
            'amount': int(kwargs.get('amount'))
        }

        # check the product_name first
        sql_name_check = '''
            SELECT * FROM test.cart 
            where cart.order_number = '{}';
        '''.format(user["order_number"])
        cursor.execute(sql_name_check)
        db.commit()

        search_name = cursor.fetchall()
        if search_name[0]["product_name"] != user["product_name"]:
            return ({"message": "wrong product_name"})

        # then check the stock
        sql_amount_check = '''
        SELECT test.cart.amount orin_amount, test.product.amount stock_amount FROM 
        `test`.`cart`, `test`.`product` WHERE cart.product_name = product.name;
        '''
        cursor.execute(sql_amount_check)
        db.commit()

        amount_check = cursor.fetchall()
        if user["amount"] > amount_check[0]["orin_amount"]:
            if user["amount"] - amount_check[0]["orin_amount"] > amount_check[0]["stock_amount"]:
                return ({"message": "understock"})
        
        amount_changed = amount_check[0]["orin_amount"] - user["amount"]

        sql_stock = '''
            UPDATE test.product
            SET amount = amount + {}
            WHERE name = '{}';
        '''.format(amount_changed, user['product_name'])

        cursor.execute(sql_stock)
        db.commit()

        query = []
        for key, value in user.items():
            if value is not None and key != 'order_number':
                query.append(f"{key} = '{value}'")
        query = ",".join(query)
       
        sql = '''
            UPDATE test.cart
            SET {}
            WHERE cart.order_number = {} and cart.user_id = {} ;
        '''.format(query, user['order_number'], id)

        result = cursor.execute(sql)
        db.commit()

        sql_items = '''
            SELECT * FROM test.cart 
            where cart.user_id = '{}';
        '''.format(id)

        cursor.execute(sql_items)
        db.commit()
        item_list = cursor.fetchall()

        sql_sum = '''
            SELECT sum(cart.amount*product.price) as sum FROM `cart`,`product` 
            where cart.product_name = product.name and cart.user_id = '{}';
        '''.format(id)
   
        cursor.execute(sql_sum)
        db.commit()
        total_price = cursor.fetchone()
        db.close()
        
        if result == 1:
            return utility.total(item_list, total_price)
        else:
            return utility.failure()

class Delete(MethodResource):   
    @doc(description='Delete item from cart .', tags=['Shopping Cart - delete'])
    @marshal_with(route_model.UserCommonResponse, code=201)
    @jwt_required()
    def delete(self, user_id, order_number):
        db, cursor = db_init()

        sql_cart_product = f'SELECT * FROM `test`.`cart` WHERE order_number = {order_number};'
        cursor.execute(sql_cart_product)
        db.commit()
        result_cart_product = cursor.fetchall()

        sql_delete = '''
            UPDATE test.product
            SET amount = amount + {}
            WHERE name = '{}';
        '''.format(result_cart_product[0]['amount'], result_cart_product[0]['product_name'])

        cursor.execute(sql_delete)
        db.commit()

        sql = f'DELETE FROM `test`.`cart` WHERE user_id = {user_id} and order_number = {order_number};'
        result = cursor.execute(sql)

        sql_items = '''
            SELECT * FROM test.cart 
            where cart.user_id = '{}';
        '''.format(user_id)

        cursor.execute(sql_items)
        db.commit()
        item_list = cursor.fetchall()

        sql_sum = '''
            SELECT sum(cart.amount*product.price) as sum FROM `cart`,`product` 
            where cart.product_name = product.name and cart.user_id = '{}';
        '''.format(user_id)
   
        cursor.execute(sql_sum)
        db.commit()
        total_price = cursor.fetchone()

        db.close()

        if result == 1:
            return utility.total(item_list, total_price)
        else:
            return utility.failure()

