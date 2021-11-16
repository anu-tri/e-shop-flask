from app import db
from datetime import datetime as dt, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login
import secrets


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(200), unique=True, index=True)
    password = db.Column(db.String(200))
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    token = db.Column(db.String, index=True, unique=True)
    token_exp = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=True)
    cart = db.relationship('Item', backref='purchaser', lazy='dynamic')
    
    
    def get_token(self, exp=86400):
        current_time = dt.utcnow()
        # give the user their token if the token is not expired
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        # if not a token create a token and exp date
        self.token = secrets.token_urlsafe(32)
        self.token_exp = current_time + timedelta(seconds=exp)
        self.save()
        return self.token


    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=61)


    @staticmethod
    def check_token(token):
        u = User.query.filter_by(token=token).first()
        if not u or u.token_exp < dt.utcnow():
            return None
        return u


    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data["email"]
        self.is_admin = data["is_admin"]
        # self.icon = data['icon']
        self.password = self.hash_password(data['password'])


    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    
    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    
    def save(self):
        db.session.add(self) 
        db.session.commit()
        

    def make_self_admin(self):
        self.is_admin=True
        db.session.commit()
    

    def __repr__(self):
        return f'<User: {self.id} | {self.email}>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    img = db.Column(db.String)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    category_id = db.Column(db.Integer())
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    created_on = db.Column(db.DateTime, index=True, default=dt.utcnow)
        
    
    def __repr__(self):
        return f'<Item: {self.id} | {self.name}>'

    def add_to_cart(self, user):
        self.owner = user.id
        db.session.commit()

    def remove_from_cart(self):
        self.owner = None
        db.session.commit()

    def empty_cart(self):
        self.owner = None
        db.session.commit()
        
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        data={
            'id':self.id,
            "name":self.name,
            "price":self.price,
            "description":self.description,
            "category_id":self.category_id,
            "owner": self.owner,
            "img":self.img,
            "created_on":self.created_on
        }
        return data

    def from_dict(self, data):
        for field in ["name","price","img","description","category_id", "owner"]:
            if field in data:
                setattr(self, field, data[field])
        return data