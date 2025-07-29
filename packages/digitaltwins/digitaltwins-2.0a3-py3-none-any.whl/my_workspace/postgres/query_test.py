from connect_postgres import connect, disconnect
from pathlib import Path
import numpy

def query(cur, sql):
    cur.execute(sql)
    resp = cur.fetchall()

    return resp


def get_programs(cur):
    sql = "SELECT * FROM program"
    resp = query(cur, sql)
    print("programs: " + str(resp))

    return resp


def get_projects(cur):
    sql = "SELECT * FROM project"
    resp = query(cur, sql)
    print("projects: " + str(resp))

    return resp


def get_datasets(cur):
    sql = "SELECT * FROM dataset"
    resp = query(cur, sql)
    print("datasets: " + str(resp))

    return resp


def get_datasets_by_descriptions(cur, mappings={}):
    conditions = ""
    if mappings:
        for idx, key in enumerate(mappings):
            if idx == 0:
                conditions = "WHERE {key} LIKE '%{value}%'".format(key=key, value=mappings[key])
            else:
                conditions += " AND {key} LIKE '%{value}%'".format(key=key, value=mappings[key])

    conditions = "title LIKE '%test%'"
    sql = "SELECT dataset_uuid, title FROM dataset_description WHERE {conditions}".format(conditions=conditions)

    resp = query(cur, sql)
    print("datasets: " + str(resp))

    return resp


if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/postgres/configs.ini")
    conn, cur = connect(config_file)

    programs = get_programs(cur)

    projects = get_projects(cur)

    datasets = get_datasets(cur)

    datasets = get_datasets_by_descriptions(cur, mappings={"title": "test"})

    disconnect(conn, cur)

    print("done")
