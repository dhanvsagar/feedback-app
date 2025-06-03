import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

class AsanaClient:
    def __init__(self):
        self.api_token = os.getenv('ASANA_API_TOKEN')
        self.project_id = os.getenv('ASANA_PROJECT_ID')

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def create_feedback_task(self, feedback_data):
        if not self.api_token or not self.project_id:
            logger.error("Asana API token or project ID missing")
            return None

        positive = sum(1 for f in feedback_data if f.get('sentiment') == 'positive')
        negative = sum(1 for f in feedback_data if f.get('sentiment') == 'negative')
        neutral = sum(1 for f in feedback_data if f.get('sentiment') == 'neutral')
        total = len(feedback_data)

        positive_prc = round((positive / total) * 100, 1) if total > 0 else 0
        negative_prc = round((negative / total) * 100, 1) if total > 0 else 0
        neutral_prc = round((neutral / total) * 100, 1) if total > 0 else 0

        # Create a task
        task_name = f"Feedback Summary - {datetime.now().strftime('%Y-%m-%d')}"
        task_notes = f"""Daily Feedback Summary
        Total: {total} feedback
😊 Positive: {positive} ({positive_prc}%)
😞 Negative: {negative} ({negative_prc}%)
😐 Neutral: {neutral} ({neutral_prc})

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

        task_data = {
            "data": {
                "name": task_name,
                "notes": task_notes,
                "projects": [self.project_id]
            }
        }

        response = requests.post(
            "https://app.asana.com/api/1.0/tasks",
            headers=self.headers,
            json=task_data,
            timeout=10
        )

        if response.status_code == 201:
            task_id = response.json()["data"]["gid"]
            task_url = f"https://app.asana.com/0/{self.project_id}/{task_id}"
            logger.info(f"Created Asana task {task_url}")
            return task_url
        else:
            logger.error("Failed to create task")
            return None
