import json

from digitaltwins.metadata.querier import Querier

class Exporter(object):
    def __init__(self, connection):
        self._connection = connection
        self._querier = Querier(self._connection)

        self._MAX_ATTEMPTS = 10

    def _get_columns(self, table_name):
        sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = N'{table_name}';".format(table_name=table_name)

        columns = self._querier.query(sql)

        return columns

    def _mapping(self, data, columns):
        output = []
        for row_data in data:
            output_row = {}
            for i in range(len(columns)):
                column = str(columns[i])
                column = column.replace("('", "")
                column = column.replace("',)", "")
                value = row_data[i]
                output_row[column] = value
            output.append(output_row)
        return output

    def _save(self, output, dest, filename):
        dest.mkdir(exist_ok=True)

        path = dest.joinpath(filename)
        with open(path, 'w') as f:
            json.dump(output, f, indent=4)

    def _get_subject_uuids(self, dataset_uuid):
        # subject_uuids = list()
        sql = "SELECT subject_uuid FROM dataset_mapping WHERE dataset_uuid='{dataset_uuid}'".format(dataset_uuid=dataset_uuid)
        subject_uuids = self._querier.query(sql)
        subject_uuids = [i[0] for i in subject_uuids]
        return subject_uuids


    def export(self, dataset_uuid, dest):
        # dataset_description
        print("Exporting dataset description")
        sql = "SELECT * FROM dataset_description WHERE dataset_uuid='{dataset_uuid}'".format(dataset_uuid=dataset_uuid)
        results = self._querier.query(sql)

        columns = self._get_columns("dataset_description")

        output = self._mapping(results, columns)
        print(output)

        filename = "dataset_description.json"
        self._save(output, dest, filename)

        # # subject
        # print("Exporting subject")
        # subject_uuids = self._get_subject_uuids(dataset_uuid=dataset_uuid)
        # sql = "SELECT * FROM subject WHERE subject_uuid IN ({subject_uuids})".format(subject_uuids=subject_uuids)
        # results = self._querier.query(sql)
        #
        # print(results)
