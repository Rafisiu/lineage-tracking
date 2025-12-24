import os
import requests
from typing import Dict, Any
from datetime import datetime, timedelta

class KeycloakService:
    def __init__(self):
        self.keycloak_url = os.getenv("KEYCLOAK_URL", "http://192.168.100.129:31088")
        self.realm = os.getenv("KEYCLOAK_REALM", "bpkp")
        self.client_id = os.getenv("KEYCLOAK_CLIENT_ID", "bpkp-service")
        self.client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET", "")
        self.token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"
        self.userinfo_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/userinfo"
        self.logout_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/logout"
        print("Keycloak config:", self.keycloak_url, self.realm, self.client_id, self.client_secret)

    def authenticate(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with Keycloak using password grant type
        
        Args:
            username: User's username or email
            password: User's password
            
        Returns:
            Dictionary containing access_token, refresh_token, and user info
            
        Raises:
            Exception: If authentication fails
        """
        try:
            data = {
                'grant_type': 'password',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'username': username,
                'password': password,
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Get user info
                user_info = self.get_user_info(token_data['access_token'])
                
                return {
                    'success': True,
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data.get('refresh_token'),
                    'expires_in': token_data.get('expires_in', 3600),
                    'token_type': token_data.get('token_type', 'Bearer'),
                    'user': {
                        'username': user_info.get('preferred_username'),
                        'email': user_info.get('email'),
                        'name': user_info.get('name'),
                        'sub': user_info.get('sub'),
                    }
                }
            else:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error_description', 'Authentication failed')
                return {
                    'success': False,
                    'error': error_message
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Connection timeout to Keycloak server'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Cannot connect to Keycloak server'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Authentication error: {str(e)}'
            }

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information using access token
        
        Args:
            access_token: Valid access token
            
        Returns:
            User information dictionary
        """
        try:
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(
                self.userinfo_url,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return {}

    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New token data
        """
        try:
            data = {
                'grant_type': 'refresh_token',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(
                self.token_url,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    **response.json()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to refresh token'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Refresh token error: {str(e)}'
            }

    def logout(self, refresh_token: str) -> bool:
        """
        Logout user by invalidating refresh token
        
        Args:
            refresh_token: User's refresh token
            
        Returns:
            True if logout successful
        """
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
            }
            
            response = requests.post(
                self.logout_url,
                data=data,
                timeout=10
            )
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"Logout error: {str(e)}")
            return False

# Singleton instance
keycloak_service = KeycloakService()
