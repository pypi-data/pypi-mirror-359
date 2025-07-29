from itertools import chain
class Querier(object):
    """
    Class for querying metadata.
    """
    # def __init__(self, config_file):
    #     pass

    def __init__(self, connection):
        """
        Constructor
        """
        self._connection = connection

        self._MAX_ATTEMPTS = 10

    def query(self, sql):
        cur = self._connection.get_cur()

        cur.execute(sql)
        resp = cur.fetchall()

        return resp

    def get_programs(self):
        sql = "SELECT * FROM program"
        resp = self.query(sql)

        return resp

    def get_projects(self):
        sql = "SELECT * FROM project"
        resp = self.query(sql)

        return resp

    def get_datasets(self, mappings={}):
        if mappings:
            conditions = ""
            for idx, key in enumerate(mappings):
                # if mappings[key] is list:
                    # SELECT * FROM your_table WHERE your_array_column @> ARRAY['value1', 'value2', 'value3'];
                    # if idx == 0:
                    #     conditions = "WHERE {key} @> ARRAY {keywords}".format(key=key, value=mappings[key])
                    # else:
                    #     conditions += " AND {key} LIKE '%{value}%'".format(key=key, value=mappings[key])

                if idx == 0:
                    conditions = "WHERE {key} LIKE '%{value}%'".format(key=key, value=mappings[key])
                else:
                    conditions += " AND {key} LIKE '%{value}%'".format(key=key, value=mappings[key])

            sql = "SELECT dataset_uuid, title FROM dataset_description {conditions}".format(conditions=conditions)
        else:
            sql = "SELECT * FROM dataset"


        resp = self.query(sql)

        return resp

    def get_datasets_by_descriptions(self, mappings={}):
        if mappings:
            conditions = ""
            for idx, key in enumerate(mappings):
                if idx == 0:
                    conditions = "WHERE {key} LIKE '%{value}%'".format(key=key, value=mappings[key])
                else:
                    conditions += " AND {key} LIKE '%{value}%'".format(key=key, value=mappings[key])

            sql = "SELECT dataset_uuid, title FROM dataset_description {conditions}".format(conditions=conditions)
        else:
            sql = "SELECT dataset_uuid, title FROM dataset_description"

        resp = self.query(sql)

        return resp

    def get_datasets_by_categories(self, categories=list()):
        formatted_categories_list = []

        # Loop through each category and format it
        for category in categories:
            formatted_category = f"'{category}'"
            formatted_categories_list.append(formatted_category)

        # Join the formatted categories into a single string
        formatted_categories = ', '.join(formatted_categories_list)

        sql = f"SELECT dataset_id, category FROM dataset WHERE category IN ({formatted_categories})"
        # sql = f"SELECT dataset_uuid, dataset_id, category FROM dataset WHERE category IN ({formatted_categories})"

        # Execute the query with the actual list of categories
        resp = self.query(sql)

        return resp

    def get_dataset_descriptions(self, dataset_uuid):
        sql = "SELECT * FROM dataset_description WHERE dataset_uuid='{dataset_uuid}'".format(dataset_uuid=dataset_uuid)
        resp = self.query(sql)

        return resp


    def get_subjects(self, dataset_uuid):
        sql = "SELECT * FROM dataset_mapping WHERE dataset_uuid='{dataset_uuid}'".format(dataset_uuid=dataset_uuid)
        resp = self.query(sql)

        return resp

    def get_samples(self, dataset_uuid=None, subject_uuid=None):
        sql = r"""SELECT subject_sample.sample_uuid FROM subject_sample INNER JOIN dataset_mapping ON subject_sample.subject_uuid=dataset_mapping.subject_uuid"""
        if dataset_uuid and not subject_uuid:
            sql = sql + " WHERE dataset_uuid='{dataset_uuid}'".format(dataset_uuid=dataset_uuid)
        elif not dataset_uuid and subject_uuid:
            sql = sql + " WHERE subject_uuid='{subject_uuid}'".format(subject_uuid=subject_uuid)
        elif dataset_uuid and subject_uuid:
            sql = sql + " WHERE dataset_uuid='{dataset_uuid}' AND subject_uuid='{subject_uuid}'".format(dataset_uuid=dataset_uuid, subject_uuid=subject_uuid)

        resp = self.query(sql)
        return resp


#     def _get_project_id(self, program, project):
#         if program is None:
#             program = self._program
#         if project is None:
#             project = self._project
#
#         project_id = program + '-' + project
#         return project_id
#
#     def get_program(self):
#         return self._program
#
#     def get_project(self):
#         return self._project
#
#     def graphql_query(self, query_string, variables=None, count=0):
#         """
#         Sending a GraphQL query to Gen3
#
#         :param query_string: query in GraphQL syntax
#         :type query_string: string
#         :param variables: query variables (optional)
#         :type variables: dict
#         :return: query response
#         :rtype: dict
#         """
#         if count >= self._MAX_ATTEMPTS:
#             raise ValueError(f"Max attempts {count} exceeded. Please try again. If the error "
#                              f"persists, please contact the developers".format(count=count))
#         try:
#             print("Sending request...")
#             response = self._querier.query(query_string, variables)
#             data = response.get("data")
#             return data
#         except Gen3AuthError as e:
#             time.sleep(2)
#             count = count + 1
#             print("Connection failed.")
#             return self.graphql_query(query_string, variables=variables, count=count)
#         except HTTPError as e:
#             print("Connection failed.")
#             raise HTTPError("HTTP connection error: Please make sure you have access to the remote server. then "
#                                   "try again!")
#         except ConnectionError as e:
#             print("Connection failed.")
#             raise ConnectionError("HTTP connection error: Please make sure you have access to the remote server. then "
#                                   "try again!")
#
#     def get_all_programs(self):
#         """
#         Getting all programs that the user have access to
#
#         :return: List of programs
#         :rtype: list
#         """
#         query_string = f"""
#         {{
#             program{{
#                 name
#             }}
#         }}
#         """
#         data = self.graphql_query(query_string)
#         programs = data.get('program')
#
#         return programs
#
#     def get_projects_by_program(self, program):
#         """
#         Getting the projects by program name
#
#         :param program: Name of a Gen3 program
#         :type program: str
#         :return: List of projects
#         :rtype: list
#         """
#         query_string = f"""
#         {{
#             program (name: "{program}"){{
#                 name
#                 projects{{
#                     name
#                 }}
#             }}
#         }}
#         """
#         data = self.graphql_query(query_string)
#
#         projects = None
#         programs = data.get('program')
#         if programs and len(programs) >= 0:
#             projects = programs[0].get("projects")
#
#         return projects
#
#     def get_datasets(self, program=None, project=None):
#         if program is None and project is None:
#             query_string = f"""
#             {{
#                 program{{
#                     name
#                     projects{{
#                         name
#                         experiments{{
#                             submitter_id
#                         }}
#                     }}
#                 }}
#             }}
#             """
#         if program and project is None:
#             query_string = f"""
#             {{
#                 program (name: "{program}"){{
#                     name
#                     projects{{
#                         name
#                         experiments{{
#                             submitter_id
#                         }}
#                     }}
#                 }}
#             }}
#             """
#         if program is None and project:
#             query_string = f"""
#             {{
#                 program{{
#                     name
#                     projects (name: "{project}"){{
#                         name
#                         experiments{{
#                             submitter_id
#                         }}
#                     }}
#                 }}
#             }}
#             """
#         if program and project:
#             query_string = f"""
#             {{
#                 program (name: "{program}") {{
#                     name
#                     projects (name: "{project}"){{
#                         name
#                         experiments {{
#                             submitter_id
#                         }}
#                     }}
#                 }}
#             }}
#             """
#         data = self.graphql_query(query_string)
#
#         datasets = list()
#         programs = data.get('program')
#         for program in programs:
#             program_name = program.get("name")
#             projects = program.get("projects")
#             for project in projects:
#                 project_name = project.get("name")
#                 experiments = project.get("experiments")
#                 for experiment in experiments:
#                     submitter_id = experiment.get("submitter_id")
#                     dataset = Dataset(id=submitter_id, program=program_name, project=project_name, config_file=self._config_file)
#                     datasets.append(dataset)
#
#         return datasets
#
#     def get_dataset(self, dataset_id, program=None, project=None):
#         if program is None:
#             program = self._program
#         if project is None:
#             project = self._project
#
#         query_string = f"""
#         {{
#             program (name: "{program}"){{
#                 name
#                 projects (name: "{project}"){{
#                     name
#                     experiments (submitter_id: "{dataset_id}"){{
#                         submitter_id
#                     }}
#                 }}
#             }}
#         }}
#         """
#         data = self.graphql_query(query_string)
#
#         dataset = None
#         if data:
#             dataset = Dataset(dataset_id, program, project, self._config_file)
#         else:
#             print("Dataset not found: " + str(dataset_id))
#
#         return dataset
#
#
#     def get_subjects(self, dataset_id, program=None, project=None):
#         project_id = self._get_project_id(program, project)
#
#         query_string = f"""
#         {{
#           experiment(project_id: "{project_id}", submitter_id: "{dataset_id}"){{
#             cases{{
#               subject_id
#             }}
#           }}
#         }}
#         """
#         response = self.graphql_query(query_string)
#         experiment = response.get("experiment")[0]
#         cases = experiment.get("cases")
#         return cases
#
#     def get_dataset_descriptions(self, dataset_id, program=None, project=None):
#         project_id = self._get_project_id(program, project)
#         query_string = f"""
#         {{
#           experiment(project_id: "{project_id}", submitter_id: "{dataset_id}"){{
#             dataset_descriptions{{
#               metadata_version,
#               dataset_type,
#               title,
#               subtitle,
#               keywords,
#               funding,
#               acknowledgments,
#               study_purpose,
#               study_data_collection,
#               study_primary_conclusion,
#               study_organ_system,
#               study_approach,
#               study_technique,
#               study_collection_title,
#               contributor_name,
#               contributor_orcid,
#               contributor_affiliation,
#               contributor_role,
#               identifier_description,
#               relation_type,
#               identifier,
#               identifier_type,
#               number_of_subjects,
#               number_of_samples,
#               dataset_type,
#               title,
#               subtitle,
#               keywords,
#               funding,
#               acknowledgments,
#               study_purpose,
#               study_data_collection,
#               study_primary_conclusion,
#               study_organ_system,
#               study_approach,
#               study_technique,
#               study_collection_title,
#               contributor_name,
#               contributor_orcid,
#               contributor_affiliation,
#               contributor_role,
#               identifier_description,
#               relation_type,
#               identifier,
#               identifier_type,
#               number_of_subjects,
#               number_of_samples
#             }}
#           }}
#         }}
#         """
#
#         response = self.graphql_query(query_string)
#         dataset = response.get("experiment")[0]
#         dataset_descriptions = dataset.get("dataset_descriptions")
#
#         return dataset_descriptions
#
#     def get_node_records(self, node, program, project):
#         """
#         Getting all the records in a Gen3 node
#
#         :param node: Name of the target node
#         :type node: str
#         :param program: program name
#         :type program: str
#         :param project: project name
#         :type project: str
#         :return: A list of records in dictionary format
#         :rtype: list
#         """
#         response = self._querier.export_node(program, project, node, "json")
#         data = response.get("data")
#         return data
#
#     def get_dataset_records(self, dataset_id, program=None, project=None):
#         project_id = self._get_project_id(program, project)
#
#         query_string = f"""
#                 {{
#                   experiment(project_id: "{project_id}", submitter_id: "{dataset_id}"){{
#                     id,
#                     submitter_id,
#                     cases{{
#                       id,
#                       submitter_id,
#                       samples{{
#                         id,
#                         submitter_id
#                       }}
#                     }},
#                     dataset_descriptions{{
#                       id,
#                       submitter_id
#                     }},
#                     manifests{{
#                       id,
#                       submitter_id
#                     }}
#                   }}
#                 }}
#                 """
#         response = self.graphql_query(query_string)
#         datasets = response.get("experiment")
#         if len(datasets) == 0:
#             return None
#
#         # the submitter_ids var is only for testing purpose
#         submitter_ids = list()
#         submitter_id_tag = "submitter_id"
#
#         records = list()
#         uuid_tag = "id"
#         # uuid_tag = "submitter_id"
#
#         dataset = datasets[0]
#         records.insert(0, dataset.get(uuid_tag))
#         submitter_ids.insert(0, dataset.get(submitter_id_tag))
#
#         cases = dataset.get("cases")
#         for case in cases:
#             records.insert(0, case.get(uuid_tag))
#             submitter_ids.insert(0, case.get(submitter_id_tag))
#             samples = case.get("samples")
#             for sample in samples:
#                 records.insert(0, sample.get(uuid_tag))
#                 submitter_ids.insert(0, sample.get(submitter_id_tag))
#
#         dataset_descriptions = dataset.get("dataset_descriptions")
#         for dataset_desc in dataset_descriptions:
#             records.insert(0, dataset_desc.get(uuid_tag))
#             submitter_ids.insert(0, dataset_desc.get(submitter_id_tag))
#
#         manifests = dataset.get("manifests")
#         for manifest in manifests:
#             records.insert(0, manifest.get(uuid_tag))
#             submitter_ids.insert(0, manifest.get(submitter_id_tag))
#
#         return records
#
#
#
#
# from digitaltwins.core.dataset import Dataset
