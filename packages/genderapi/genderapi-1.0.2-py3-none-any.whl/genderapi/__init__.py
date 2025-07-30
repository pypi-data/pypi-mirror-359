import requests

class GenderAPI:
    def __init__(self, api_key, base_url="https://api.genderapi.io"):
        """
        GenderAPI.io Python SDK
        :param api_key: Your Bearer token
        :param base_url: API Base URL (default: https://api.genderapi.io)
        """
        self.api_key = api_key
        self.base_url = base_url

    def get_gender_by_name(self, name, country=None, askToAI=False):
        """
        Determine gender from a name.

        :param name: Name to query (required)
        :param country: Optional 2-letter country code (e.g. "US")
        :param askToAI: Whether to directly query AI for prediction (default False)
        :return: JSON response as dict
        """
        return self._post_request("/api", {"name": name, "country": country, "askToAI": askToAI})

    def get_gender_by_email(self, email, country=None, askToAI=False):
        """
        Determine gender from an email address.

        :param email: Email address to query (required)
        :param country: Optional 2-letter country code (e.g. "US")
        :param askToAI: Whether to directly query AI for prediction (default False)
        :return: JSON response as dict
        """
        return self._post_request("/api/email", {"email": email, "country": country, "askToAI": askToAI})

    def get_gender_by_username(self, username, country=None, askToAI=False):
        """
        Determine gender from a username.

        :param username: Username to query (required)
        :param country: Optional 2-letter country code (e.g. "US")
        :param askToAI: Whether to directly query AI for prediction (default False)
        :return: JSON response as dict
        """
        return self._post_request("/api/username", {"username": username, "country": country, "askToAI": askToAI})

    def _post_request(self, endpoint, payload):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
