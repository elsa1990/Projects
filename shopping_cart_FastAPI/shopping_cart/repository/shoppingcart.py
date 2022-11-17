from sqlalchemy.orm import Session
from shopping_cart import models, schemas
from fastapi import HTTPException, status

# get all products info
def get_all_products(db: Session):
    get_all = db.query(models.Product).all()
    return get_all

# fuzzy search for producst
def fuzzy(request: schemas.Fuzzy, db: Session):
    fuzzy = db.query(models.Product).filter(models.Product.name.like('%' + request.name +'%')).all()
    if not fuzzy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product {request.name} not existed")
    return fuzzy
    
# add to cart
def create(request: schemas.Addtocart, db: Session):
    check_product = db.query(models.Product).filter(models.Product.name == request.name).first()
    if not check_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product {request.name} not existed")

    if check_product.amount < request.amount:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product {request.name} understock")

    total_price = check_product.price * request.amount
    new_order = models.Orders(name=request.name, amount=request.amount, price=check_product.price, total=total_price, user_id=request.user_id)
    db.add(new_order)

    stock_left = check_product.amount - request.amount
    check_product.amount= stock_left
    db.commit()
    db.refresh(new_order)
    return new_order

# delete order
def destroy(id: int, db: Session):
    order = db.query(models.Orders).filter(models.Orders.id == id)
    if not order.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {id} not found")

    product_name = order.first().name
    check_product = db.query(models.Product).filter(models.Product.name == product_name).first()
    check_product.amount += order.first().amount

    order.delete(synchronize_session=False)
    db.commit()
    return 'deletion done'

# use patch to modify an order
def update(id: int, request: schemas.Modify, db: Session):
    order = db.query(models.Orders).filter(models.Orders.id == id)
    product_check = db.query(models.Product).filter(models.Product.name == request["name"]).first()

    if not order.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with id {id} not found")
    if order.first().name != request["name"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product name not found in this order")

    amount_changed = request["amount"] - order.first().amount

    if amount_changed > 0:
        if product_check.amount >= amount_changed:
            product_check.amount -= amount_changed
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Product {product_check.name} understock")
    
    elif amount_changed < 0:
        product_check.amount -= amount_changed

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Nothing changed")
    
    order.first().total = order.first().price * request["amount"]
    order.update(request)
    db.commit()
    return 'updated'


# show order by id
def show(id: int, db: Session):
    showorder = db.query(models.Orders).filter(models.Orders.id == id).first()
    if not showorder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Order with the id {id} is not available")
    return showorder
