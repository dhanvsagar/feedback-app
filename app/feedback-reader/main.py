import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import json
import time
import os
from datetime import datetime, date
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

class FeedbackReader:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'feedback'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.db_config)
            return True
        except psycopg2.Error as e:
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()
    
    def read_all_feedback(self):
        # read all rows
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM feedback ORDER BY id")
                rows = cursor.fetchall()

                if not rows:
                    print("No feedback records found in the database.")
                    return []
                # Convert rows to list of dictionaries
                feedback_data = []
                for row in rows:
                    row_dict = dict(row)

                    for key, value in row_dict.items():
                        if isinstance(value, (datetime, date)):
                            row_dict[key] = value.isoformat()
                    feedback_data.append(row_dict)
                return feedback_data
        except psycopg2.Error as e:
            logger.error(f"Error reading feedback table: {e}")
            return []
    
    def print_feedback_records(self, feedback_data):
        print(f"FEEDBACK RECORDS - Total: {len(feedback_data)}")
        for i, record in enumerate(feedback_data, 1):
            for key, value in record.items():
                print(f"{key}: {value}")


def main():
    logger.info("Starting Feedback Reader Application")
    feedback_reader = FeedbackReader()
    feedback_reader.connect()
    feedback_data = feedback_reader.read_all_feedback()
    feedback_reader.print_feedback_records(feedback_data)
    feedback_reader.disconnect()
    logger.info("Application finished")

if __name__ == "__main__":
    main()