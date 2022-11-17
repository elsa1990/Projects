from sqlalchemy import Column, Integer, String, ForeignKey
from shopping_cart.database import Base
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    amount = Column(Integer)
    price = Column(Integer)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100),unique=True)
    password = Column(String(100))

    orders = relationship('Orders', back_populates="creator")


class Orders(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    amount = Column(Integer)
    price = Column(Integer)
    total = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship("User", back_populates="orders")


# class Blog(Base):
#     __tablename__ = 'blogs'

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(100))
#     body = Column(String(100))
#     user_id = Column(Integer, ForeignKey('users.id'))

#     creator = relationship("User", back_populates="blogs")


# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100))
#     email = Column(String(100))
#     password = Column(String(100))

#     blogs = relationship('Blog', back_populates="creator")
