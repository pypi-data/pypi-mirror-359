import requests

# Airflow REST API details
BASE_URL = "http://130.216.208.137:8080"
USERNAME = "admin"  # Replace with your Airflow username
# PASSWORD = "admin"
# PASSWORD = "CYsWGZY7y23vB7Su"
PASSWORD = "PgKFTfe4B2C7ragN"


def login():
    """
    If your auth_backends is set to airflow.api.auth.backend.session,
    it means the Airflow REST API requires session-based authentication,
    which involves obtaining a CSRF token and using a session cookie for subsequent requests.
    """
    login_url = f"{BASE_URL}/login"
    session = requests.Session()

    login_payload = {"username": USERNAME, "password": PASSWORD}
    login_response = session.post(login_url, data=login_payload)

    if login_response.status_code == 200:
        print("Logged in successfully!")
    else:
        print("Failed to log in")
        print("Response:", login_response.text)
        exit()


def connection():
    url = f"{BASE_URL}/api/v1/connections"

    response = requests.get(url, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        print("Connections fetched successfully!")
        print("Connections:", response.json())
    else:
        print("Failed to fetch connections")
        print("Response:", response.text)


if __name__ == '__main__':
    # login()
    connection()
