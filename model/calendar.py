from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from datetime import datetime

class Event(db.Model):
    """
    Event Model
    Attributes:
        id (int): Primary key for the event.
        uid (str): User ID to associate events with specific users.
        title (str): Title of the event.
        description (str): Description of the event.
        start_time (datetime): Event start time.
        end_time (datetime): Event end time.
        category (str): Category of the event.
    """
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def __init__(self, uid, title, description, start_time, end_time, category):
        self.uid = uid
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.category = category

    def create(self):
        """
        Add the current Event instance to the database.
        Returns:
            self: The created Event instance if successful, None otherwise.
        """
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        """
        Convert the Event instance to a dictionary.
        Returns:
            dict: A dictionary representation of the Event instance.
        """
        return {
            'id': self.id,
            'uid': self.uid,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None,
            'category': self.category
        }

    def update(self, data):
        """
        Update the Event instance with new data.
        Args:
            data (dict): A dictionary containing the new data for the Event instance.
        Returns:
            self: The updated Event instance.
        """
        for key, value in data.items():
            if key == "title":
                self.title = value
            elif key == "description":
                self.description = value
            elif key == "start_time":
                self.start_time = datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if isinstance(value, str) else value
            elif key == "end_time":
                self.end_time = datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if isinstance(value, str) else value
            elif key == "category":
                self.category = value
        db.session.commit()
        return self

    def delete(self):
        """
        Delete the current Event instance from the database.
        """
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def restore(data):
        """
        Restore Event instances from a list of dictionaries.
        Args:
            data (list): A list of dictionaries containing the data for Event instances.
        """
        for event_data in data:
            _ = event_data.pop('id', None)
            id = event_data.get('id', None)
            uid = event_data.get('uid', None)
            title = event_data.get('title', None)
            description = event_data.get('description', None)
            start_time_str = event_data.get('start_time', None)
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S') if start_time_str else None
            end_time_str = event_data.get('end_time', None)
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S') if end_time_str else None
            category = event_data.get('category', None)
            event = Event.query.filter_by(id=id).first()
            if event:
                event.update(event_data)
            else:
                event = Event(uid=uid, title=title, description=description, start_time=start_time, end_time=end_time, category=category)
                event.create()

class Employee(db.Model):
    """
    Employee Model
    Attributes:
        id (int): Primary key for the employee.
        uid (str): User ID to associate employees with specific users.
        name (str): Name of the employee.
        position (str): Position of the employee.
        work_time (str): Work hours, e.g., "9 AM - 5 PM".
    """
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    work_time = db.Column(db.String(100), nullable=False)

    def __init__(self, uid, name, position, work_time):
        self.uid = uid
        self.name = name
        self.position = position
        self.work_time = work_time

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'name': self.name,
            'position': self.position,
            'work_time': self.work_time
        }

    def update(self, data):
        for key, value in data.items():
            if key == "name":
                self.name = value
            elif key == "position":
                self.position = value
            elif key == "work_time":
                self.work_time = value
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def restore(data):
        for emp_data in data:
            _ = emp_data.pop('id', None)
            id = emp_data.get('id', None)
            uid = emp_data.get('uid', None)
            name = emp_data.get('name', None)
            position = emp_data.get('position', None)
            work_time = emp_data.get('work_time', None)
            emp = Employee.query.filter_by(id=id).first()
            if emp:
                emp.update(emp_data)
            else:
                emp = Employee(uid=uid, name=name, position=position, work_time=work_time)
                emp.create()

class Shipment(db.Model):
    """
    Shipment Model
    Attributes:
        id (int): Primary key for the shipment.
        uid (str): User ID to associate shipments with specific users.
        inventory (str): Inventory item name.
        amount (int): Amount shipped.
        transport_method (str): Method of transport.
        shipment_time (str): Shipment time (can be ISO string or text).
        destination (str): Destination of the shipment.
    """
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), nullable=False)
    inventory = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    transport_method = db.Column(db.String(50), nullable=False)
    shipment_time = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=True)

    def __init__(self, uid, inventory, amount, transport_method, shipment_time, destination=None):
        self.uid = uid
        self.inventory = inventory
        self.amount = amount
        self.transport_method = transport_method
        self.shipment_time = shipment_time
        self.destination = destination

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'inventory': self.inventory,
            'amount': self.amount,
            'transport_method': self.transport_method,
            'shipment_time': self.shipment_time,
            'destination': self.destination
        }

    def update(self, data):
        for key, value in data.items():
            if key == "inventory":
                self.inventory = value
            elif key == "amount":
                self.amount = value
            elif key == "transport_method":
                self.transport_method = value
            elif key == "shipment_time":
                self.shipment_time = value
            elif key == "destination":
                self.destination = value
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def restore(data):
        for ship_data in data:
            _ = ship_data.pop('id', None)
            id = ship_data.get('id', None)
            uid = ship_data.get('uid', None)
            inventory = ship_data.get('inventory', None)
            amount = ship_data.get('amount', None)
            transport_method = ship_data.get('transport_method', None)
            shipment_time = ship_data.get('shipment_time', None)
            destination = ship_data.get('destination', None)
            ship = Shipment.query.filter_by(id=id).first()
            if ship:
                ship.update(ship_data)
            else:
                ship = Shipment(uid=uid, inventory=inventory, amount=amount, transport_method=transport_method,
                                shipment_time=shipment_time, destination=destination)
                ship.create()

class Task(db.Model):
    """
    Task Model
    Attributes:
        id (int): Primary key for the task.
        uid (str): User ID to associate tasks with specific users.
        title (str): Title of the task.
        description (str): Description of the task.
        due_date (datetime): Due date of the task.
        priority (str): Priority level of the task.
        status (str): Current status of the task.
        employee (str): Employee assigned to the task.
    """
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    employee = db.Column(db.String(100), nullable=True)

    def __init__(self, uid, title, description, due_date, priority, status, employee=None):
        self.uid = uid
        self.title = title
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.status = status
        self.employee = employee

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        return {
            'id': self.id,
            'uid': self.uid,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.strftime('%Y-%m-%d %H:%M:%S') if self.due_date else None,
            'priority': self.priority,
            'status': self.status,
            'employee': self.employee
        }

    def update(self, data):
        for key, value in data.items():
            if key == "title":
                self.title = value
            elif key == "description":
                self.description = value
            elif key == "due_date":
                self.due_date = datetime.strptime(value, '%Y-%m-%d %H:%M:%S') if isinstance(value, str) else value
            elif key == "priority":
                self.priority = value
            elif key == "status":
                self.status = value
            elif key == "employee":
                self.employee = value
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def restore(data):
        for task_data in data:
            _ = task_data.pop('id', None)
            id = task_data.get('id', None)
            uid = task_data.get('uid', None)
            title = task_data.get('title', None)
            description = task_data.get('description', None)
            due_date_str = task_data.get('due_date', None)
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d %H:%M:%S') if due_date_str else None
            priority = task_data.get('priority', None)
            status = task_data.get('status', None)
            employee = task_data.get('employee', None)
            task = Task.query.filter_by(id=id).first()
            if task:
                task.update(task_data)
            else:
                task = Task(uid=uid, title=title, description=description, due_date=due_date, 
                           priority=priority, status=status, employee=employee)
                task.create()

def initEvents():
    with app.app_context():
        db.create_all()
        print("All tables created (events, employees, shipments, tasks).")
        db.session.commit()
        print("Initialization complete.")
