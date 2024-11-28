import os

from requestyai import AInsights

ainsights = AInsights.new_client(
    api_key=os.environ["REQUESTY_API_KEY"], base_url=os.environ.get("REQUESTY_BASE_URL")
)
