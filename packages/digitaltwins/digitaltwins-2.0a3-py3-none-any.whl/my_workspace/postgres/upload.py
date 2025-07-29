from pathlib import Path

from digitaltwins.core.connection import Connection

def upload_dataset(connection, project_uuid, dataset_id, version=1, subject_mappings=None):
    query = r"""INSERT INTO dataset (project_uuid, dataset_id, version) VALUES (%s, %s, %s) RETURNING *;"""
    values = (project_uuid, dataset_id, version)
    cur = connection.get_cur()
    conn = connection.get_conn()
    cur.execute(query, values)

    dataset_uuid = cur.fetchone()[1]
    conn.commit()

    # get subject info. hard-code for testing
    subjects = [
        {
            "subject_id": "sub-001",
            "age": "12 weeks",
            "sex": "male",
            "species": "Mus musculus"
        },
        {
            "subject_id": "sub-002",
            "age": "20 years old",
            "sex": "female",
            "species": "Mus musculus"
        }
    ]

    upload_subjects(connection, dataset_uuid, subjects, subject_mappings)

def upload_subjects(connection, dataset_uuid, subjects, subject_mappings):
    # check if subjects exist
    # subject_mappings = [
    #     {"subject_id": subject_id, "subject_uuid": subject_uuid},
    #     {"subject_id": subject_id, "subject_uuid": subject_uuid},
    #     ...
    # ]
    cur = connection.get_cur()
    conn = connection.get_conn()

    for subject in subjects:
        subject_id = subject["subject_id"]

        subject_uuid = subject_mappings.get(subject_id)
        if subject_uuid:
            query = r"""INSERT INTO dataset_mapping (dataset_uuid, subject_uuid) VALUES (%s, %s) RETURNING *;"""
            values = (dataset_uuid, subject_uuid)
            cur.execute(query, values)

            results = cur.fetchone()
            conn.commit()
            print(results)
        else:
            query = r"""INSERT INTO subject (subject_id, age, sex, species) VALUES (%s, %s, %s, %s) RETURNING *;"""
            values = (subject["subject_id"], subject["age"], subject["sex"], subject["species"])
            cur.execute(query, values)

            subject_uuid = cur.fetchone()[0]
            conn.commit()

            query = r"""INSERT INTO dataset_mapping (dataset_uuid, subject_uuid) VALUES (%s, %s) RETURNING *;"""
            values = (dataset_uuid, subject_uuid)
            cur.execute(query, values)

            results = cur.fetchone()
            conn.commit()
            print(results)

    # for mapping in subject_mappings:
    #     subject_id = mapping["subject_id"]
    #     subject_uuid = mapping["subject_uuid"]
    #
    #     if subject_uuid:
    #         query = r"""INSERT INTO dataset_subject (subject_id, age, sex, species) VALUES (%s, %s) RETURNING *;"""
    #         values = (project_uuid, dataset_id)
    #         cur = connection.get_cur()
    #         conn = connection.get_conn()
    #         cur.execute(query, values)
    #         conn.commit()
    #     else:
    #         subject = subjects[]
    #         query = r"""INSERT INTO subject (dataset_uuid, subject_uuid) VALUES (%s, %s) RETURNING *;"""
    #         values = (project_uuid, dataset_id)
    #         cur = connection.get_cur()
    #         conn = connection.get_conn()
    #         cur.execute(query, values)
    #         conn.commit()

if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/postgres/configs.ini")

    project_uuid = "01480638-ba55-11ee-8dd3-484d7e9beb16"
    dataset_id = "dataset_tmp"

    # subject_mappings
    subject_mappings = {
        "sub-001": "a69c829a-124c-11ef-9766-484d7e9beb16"
    }
    # subject_mappings = [
    #     {"subject_id": "sub-001", "subject_uuid": "a69c829a-124c-11ef-9766-484d7e9beb16"}
    # ]

    connection = Connection(config_file)
    connection.connect()

    upload_dataset(connection,
                   project_uuid=project_uuid,
                   dataset_id=dataset_id,
                   subject_mappings=subject_mappings
                   )

    connection.disconnect()
