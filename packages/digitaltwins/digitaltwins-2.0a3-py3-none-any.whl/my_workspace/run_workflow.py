from pathlib import Path

from digitaltwins import Workflow

if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini")
    assay_id = 2
    # assay_id = 18 # ep2 workflow 1

    workflow = Workflow(config_file)
    response, workflow_monitor_url = workflow.run(assay_id=assay_id)

    print("response.status_code:" + str(response.status_code))
    print("Monitoring workflow on: " + workflow_monitor_url)
