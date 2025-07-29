import requests

# Airflow REST API
BASE_URL = "http://130.216.208.137:8080"
USERNAME = "admin"
PASSWORD = "PgKFTfe4B2C7ragN"


def get_query_string(params):
    """
    # get query parameters into string

    :param params:
    :type params: dict()
    :return:
    :rtype:
    """
    query_string = '?'

    for key, value in params.items():
        query_string = query_string + '&' + key + '=' + str(value)

    return query_string


def list_dags():
    url = f"{BASE_URL}/api/v1/dags"

    response = requests.get(url, auth=(USERNAME, PASSWORD))

    if response.status_code == 200:
        print("DAGs fetched successfully!")
        dags = response.json()
        print("DAGs List:")
        for dag in dags.get("dags", []):
            print(f"- {dag['dag_id']}: {dag['description'] or 'No description'}")
    else:
        print("Failed to fetch DAGs")
        print("Response:", response.text)


def list_dag_runs(dag_id, **params):
    url = f"{BASE_URL}/api/v1/dags/{dag_id}/dagRuns"

    if params:
        query_string = get_query_string(params)
        url = url + query_string

    response = requests.get(url, auth=(USERNAME, PASSWORD))
    response = response.json()

    print(response)


if __name__ == '__main__':
    list_dags()
    # list_dag_runs("ep4")
    # list_dag_runs("ep4", limit=5)
    list_dag_runs("d15dbdd2-ed7a-11ef-917d-484d7e9beb16")
