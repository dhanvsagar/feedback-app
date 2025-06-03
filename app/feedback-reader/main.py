import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import json
import time
import os
from datetime import datetime, date
from dotenv import load_dotenv
from sentiment_analyzer import analyze_sentiment

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
                query = """
                SELECT rating, message, created_at FROM feedback
                WHERE created_at >= NOW() - INTERVAL '24 hours'
                ORDER BY created_at DESC
                """
                cursor.execute(query)
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

                    # Add simple sentiment analysis
                    if 'message' in row_dict and row_dict['message']:
                        sentiment = analyze_sentiment(row_dict['message'])
                        row_dict['sentiment'] = sentiment
                    else:
                        row_dict['sentiment'] = 'neutral'
                    feedback_data.append(row_dict)
                return feedback_data
        except psycopg2.Error as e:
            logger.error(f"Error reading feedback table: {e}")
            return []
    
    def print_feedback_records(self, feedback_data):
        if not feedback_data:
             print("No recent feedback data to display.")
             return
        
        print(f"FEEDBACK RECORDS - Total: {len(feedback_data)}")
        
        positive = sum(1 for f in feedback_data if f.get('sentiment') == 'positive')
        negative = sum(1 for f in feedback_data if f.get('sentiment') == 'negative')
        neutral = sum(1 for f in feedback_data if f.get('sentiment') == 'neutral')
        total = len(feedback_data)

        positive_prc = round((positive / total) * 100, 1) if total > 0 else 0
        negative_prc = round((negative / total) * 100, 1) if total > 0 else 0
        neutral_prc = round((neutral / total) * 100, 1) if total > 0 else 0

        print(f"😊 Positive: {positive} ({positive_prc}%) | 😞 Negative: {negative} ({negative_prc}%) | 😐 Neutral: {neutral} ({neutral_prc}%)")

        print(feedback_data)
        


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