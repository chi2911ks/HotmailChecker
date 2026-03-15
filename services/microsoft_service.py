import requests
from config import AppConfig

class MicrosoftService:
    @staticmethod
    def check_refresh_token(client_id, refresh_token):
        """
        Checks if a refresh token is valid by attempting to get a new access token.
        Returns (True, data) if valid, (False, error_message) otherwise.
        """
        payload = {
            'client_id': client_id,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        try:
            response = requests.post(AppConfig.MS_TOKEN_URL, data=payload, timeout=15)
            if response.status_code == 200:
                return True, response.json()
            else:
                error_data = response.json()
                error_msg = error_data.get('error_description', error_data.get('error', 'Unknown error'))
                return False, error_msg
        except requests.exceptions.RequestException as e:
            return False, str(e)
