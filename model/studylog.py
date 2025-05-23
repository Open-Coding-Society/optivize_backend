from sqlalchemy.exc import IntegrityError
from datetime import datetime
from __init__ import app, db

class productSalesPrediction(db.Model):
    """
    Product Sales Prediction Model
    
    Attributes:
        id (int): Primary key
        product_type (str): Product type name
        seasonality (str): Seasonality factor
        price (float): Product price
        marketing (int): Marketing score (1-10)
        distribution_channels (float): Distribution channels score
        predicted_success (bool): Whether prediction was successful
        success_score (float): Prediction success score (0-100)
        product_category (str): Product category
        date_created (DateTime): When record was created
    """
    __tablename__ = 'product_sales_predictions'

    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(255), nullable=True)  # Made nullable for initialization
    seasonality = db.Column(db.String(50), nullable=True)    # Made nullable for initialization
    price = db.Column(db.Float, nullable=True)              # Made nullable for initialization
    marketing = db.Column(db.Integer, nullable=True)        # Made nullable for initialization
    distribution_channels = db.Column(db.Float, nullable=True) # Made nullable for initialization
    predicted_success = db.Column(db.Boolean, nullable=True)  # Made nullable for initialization
    success_score = db.Column(db.Float, nullable=True)       # Made nullable for initialization
    product_category = db.Column(db.String(50), nullable=True) # Made nullable for initialization
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, product_type=None, seasonality=None, price=None, marketing=None, 
                 distribution_channels=None, predicted_success=None, success_score=None, 
                 product_category=None):
        self.product_type = product_type
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
            "product_type": self.product_type,
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

def initproductSalesPredictions():
    """Initialize the database table - drops existing table and creates new one"""
    with app.app_context():
        try:
            # Drop the table if it exists
            db.drop_all()
            app.logger.info("Dropped existing product_sales_predictions table")
            
            # Create all tables
            db.create_all()
            app.logger.info("Created new product_sales_predictions table")
            
            # Optional: Add a test record
            test_record = productSalesPrediction(
                product_type="Sample Product",
                seasonality="All Year",
                price=19.99,
                marketing=7,
                distribution_channels=8,
                predicted_success=True,
                success_score=85.0,
                product_category="Sample"
            )
            db.session.add(test_record)
            db.session.commit()
            app.logger.info("Added test record to product_sales_predictions table")
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error initializing product sales predictions table: {e}")
            raise