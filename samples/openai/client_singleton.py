import os

from requestyai import AInsights

requesty_key = os.environ["REQUESTY_KEY"]
base_url = os.environ.get("REQUESTY_BASE_URL", default=None)
insights = AInsights.new_client(api_key=requesty_key, base_url=base_url)
