from sqlalchemy.exc import IntegrityError
from __init__ import app, db

class CookieSalesPrediction(db.Model):
    """
    Cookie Sales Prediction Model
    
    Attributes:
        id (int): Primary key for the prediction record.
        cookie_flavor (str): Flavor of the cookie.
        seasonality (str): Seasonality category (e.g., 'Holiday', 'Regular').
        price (float): Price of the cookie.
        marketing (int): Whether marketing is applied (1 for Yes, 0 for No).
        customer_sentiment (float): Average customer sentiment score (0-1 scale).
        predicted_success (bool): Prediction outcome (True for success, False for failure).
    """
    __tablename__ = 'cookie_sales_predictions'

    id = db.Column(db.Integer, primary_key=True)
    cookie_flavor = db.Column(db.String(255), nullable=False)
    seasonality = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    marketing = db.Column(db.Integer, nullable=False)
    customer_sentiment = db.Column(db.Float, nullable=False)
    predicted_success = db.Column(db.Boolean, nullable=False)

    def __init__(self, cookie_flavor, seasonality, price, marketing, customer_sentiment, predicted_success):
        self.cookie_flavor = cookie_flavor
        self.seasonality = seasonality
        self.price = price
        self.marketing = marketing
        self.customer_sentiment = customer_sentiment
        self.predicted_success = predicted_success

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError as e:
            db.session.rollback()
            print(f"IntegrityError while saving prediction: {e}")
            return None
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error while saving prediction: {e}")
            return None

    def read(self):
        return {
            "id": self.id,
            "cookie_flavor": self.cookie_flavor,
            "seasonality": self.seasonality,
            "price": self.price,
            "marketing": self.marketing,
            "customer_sentiment": self.customer_sentiment,
            "predicted_success": self.predicted_success
        }

    def update(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()


def initCookieSalesPredictions():
    with app.app_context():
        db.create_all()
        print("CookieSalesPrediction table initialized.")
