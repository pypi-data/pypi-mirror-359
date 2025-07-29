from pathlib import Path

from digitaltwins.core.connection import Connection
from digitaltwins.metadata.querier import Querier
from digitaltwins.metadata.exporter import Exporter

if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/postgres/configs.ini")
    dataset_uuid = "21e7de6e-01bc-11ef-878e-484d7e9beb16"
    dest = Path(r"./dataset_metadata")

    connection = Connection(config_file)
    connection.connect()

    exporter = Exporter(connection)
    exporter.export(dataset_uuid= dataset_uuid, dest=dest)


