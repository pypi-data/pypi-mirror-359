import configparser
import psycopg2
from pathlib import Path


def connect(config_file):
    configs = configparser.ConfigParser()
    configs.read(config_file)
    print(configs.sections())
    configs_postgres = configs["postgres"]
    conn = psycopg2.connect(
        host=configs_postgres["host"],
        port=configs_postgres["port"],
        database=configs_postgres["database"],
        user=configs_postgres["user"],
        password=configs_postgres["password"])
    # create a cursor
    cur = conn.cursor()

    return conn, cur


def disconnect(conn, cur):
    cur.close()
    conn.close()


if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/postgres/configs.ini")
    conn, cur = connect(config_file)

    cur.execute('SELECT version()')
    db_version = cur.fetchone()
    print(db_version)

    sql = "SELECT * FROM program"
    cur.execute(sql)
    resp = cur.fetchall()
    print("programs: " + str(resp))

    sql = "SELECT * FROM project"
    cur.execute(sql)
    resp = cur.fetchall()
    print("projects: " + str(resp))

    sql = "SELECT * FROM dataset"
    cur.execute(sql)
    resp = cur.fetchall()
    print("datasets: " + str(resp))

    disconnect(conn, cur)

    print("done")
