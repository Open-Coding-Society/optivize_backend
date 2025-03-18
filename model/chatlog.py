
import logging
from sqlite3 import IntegrityError
from __init__ import app, db
class ChatLog(db.Model):
    __tablename__ = 'chat_logs'
    id = db.Column(db.Integer, primary_key=True)
    _question = db.Column(db.String(500), nullable=False)
    _response = db.Column(db.String(2000), nullable=False)
    def __init__(self, question, response):
        """
        Constructor to initialize ChatLog object.
        Args:
            question (str): The user's question.
            response (str): The AI's response.
        """
        self._question = question
        self._response = response
    @property
    def question(self):
        return self._question
    @property
    def response(self):
        return self._response
    def create(self):
        """
        Add the object to the database and commit the transaction.
        Raises:
            Exception: If an error occurs during the commit.
        """
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    def read(self):
        """
        Retrieve the object's data as a dictionary.
        Returns:
            dict: A dictionary containing the question and response.
        """
        return {
            'id': self.id,
            'question': self._question,
            'response': self._response,
        }
    def update(self, updates):
        # Extract the updated values from the dictionary
        question = updates.get('question', None)
        response = updates.get('response', None)
        # Update attributes if new values are provided
        if question:
            self._question = question
        if response:
            self._response = response
        # Attempt to commit the changes to the database
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            logging.warning(f"IntegrityError: Could not update chat log with ID '{self.id}'.")
            return None
        return self
    @staticmethod
    def restore(data):
        """
        Restore data from a list of dictionaries into the database.
        Args:
            data (list): List of dictionaries containing chat logs.
        Returns:
            dict: A dictionary of restored chat logs.
        """
        chat_logs = {}
        for log_data in data:
            _ = log_data.pop('id', None)
            question = log_data.get("question", None)
            log = ChatLog.query.filter_by(_question=question).first()
            if log:
                log.update(log_data)
            else:
                log = ChatLog(**log_data)
                log.create()
        return chat_logs
@staticmethod
def restore(chat_data):
    for log_entry in chat_data:
        _ = log_entry.pop('id', None)  # Remove 'id' to avoid conflicts
        session_id = log_entry.get("session_id")
        chatlog = ChatLog.query.filter_by(session_id=session_id).first()
        if chatlog:
            chatlog.update(log_entry)
        else:
            chatlog = ChatLog(**log_entry)
            chatlog.create()
def initChatLogs():
    """
    Initialize the database with example chat logs for testing.
    """
    with app.app_context():
        db.create_all()
        # Example chat logs
        log1 = ChatLog(question="How far is the moon", response="The Moon is 238,900 mi")
        log2 = ChatLog(question="Whats the capital of China", response="The capital of China is Beijing.")
        chat_logs = [log1, log2]
        for log in chat_logs:
            try:
                log.create()
            except IntegrityError:
                db.session.rollback()
# Ensuring the table is created
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Table creation complete.")