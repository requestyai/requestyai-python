import os

from requestyai import AInsights

requesty_key = os.environ["REQUESTY_KEY"]
insights = AInsights.new_client(
    api_key=requesty_key, base_url="https://api.requesty.ai"
)
