from sqlalchemy.exc import IntegrityError
from datetime import datetime
from __init__ import app, db

class CookieSalesPrediction(db.Model):
    """
    Enhanced Cookie Sales Prediction Model with additional fields for the API
    
    Attributes:
        id (int): Primary key
        cookie_flavor (str): Cookie flavor name
        seasonality (str): Seasonality factor
        price (float): Product price
        marketing (int): Marketing score (1-10)
        distribution_channels (float): Distribution channels score
        predicted_success (bool): Whether prediction was successful
        success_score (float): Prediction success score (0-100)
        product_category (str): Product category
        date_created (DateTime): When record was created
    """
    __tablename__ = 'cookie_sales_predictions'

    id = db.Column(db.Integer, primary_key=True)
    cookie_flavor = db.Column(db.String(255), nullable=False)
    seasonality = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    marketing = db.Column(db.Integer, nullable=False)
    distribution_channels = db.Column(db.Float, nullable=False)
    predicted_success = db.Column(db.Boolean, nullable=False)
    success_score = db.Column(db.Float, nullable=False)
    product_category = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, cookie_flavor, seasonality, price, marketing, 
                 distribution_channels, predicted_success, success_score, 
                 product_category):
        self.cookie_flavor = cookie_flavor
        self.seasonality = seasonality
        self.price = price
        self.marketing = marketing
        self.distribution_channels = distribution_channels
        self.predicted_success = predicted_success
        self.success_score = success_score
        self.product_category = product_category

    def create(self):
        """Create a new prediction record"""
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError as e:
            db.session.rollback()
            app.logger.error(f"IntegrityError while saving prediction: {e}")
            return None
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Unexpected error while saving prediction: {e}")
            return None

    def read(self):
        """Return dictionary representation of the record"""
        return {
            "id": self.id,
            "cookie_flavor": self.cookie_flavor,
            "seasonality": self.seasonality,
            "price": self.price,
            "marketing": self.marketing,
            "distribution_channels": self.distribution_channels,
            "predicted_success": self.predicted_success,
            "success_score": self.success_score,
            "product_category": self.product_category,
            "date_created": self.date_created.isoformat() if self.date_created else None
        }

    def update(self, data):
        """Update fields with provided dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """Delete this record"""
        db.session.delete(self)
        db.session.commit()
        return None

def initCookieSalesPredictions():
    """Initialize the database table"""
    with app.app_context():
        db.create_all()
        app.logger.info("CookieSalesPrediction table initialized")