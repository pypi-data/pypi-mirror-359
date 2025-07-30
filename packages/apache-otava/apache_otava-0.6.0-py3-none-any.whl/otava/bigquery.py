# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from google.cloud import bigquery
from google.oauth2 import service_account

from otava.analysis import ChangePoint
from otava.test_config import BigQueryTestConfig


@dataclass
class BigQueryConfig:
    project_id: str
    dataset: str
    credentials: str


@dataclass
class BigQueryError(Exception):
    message: str


class BigQuery:
    __client = None
    __config = None

    def __init__(self, config: BigQueryConfig):
        self.__config = config

    @property
    def client(self) -> bigquery.Client:
        if self.__client is None:
            credentials = service_account.Credentials.from_service_account_file(
                self.__config.credentials,
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            self.__client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        return self.__client

    def fetch_data(self, query: str):
        query_job = self.client.query(query)  # API request
        results = query_job.result()
        columns = [field.name for field in results.schema]
        return (columns, results)

    def insert_change_point(
        self,
        test: BigQueryTestConfig,
        metric_name: str,
        attributes: Dict,
        change_point: ChangePoint,
    ):
        kwargs = {**attributes, **{test.time_column: datetime.utcfromtimestamp(change_point.time)}}
        update_stmt = test.update_stmt.format(
            metric=metric_name,
            forward_change_percent=change_point.forward_change_percent(),
            backward_change_percent=change_point.backward_change_percent(),
            p_value=change_point.stats.pvalue,
            **kwargs
        )
        query_job = self.client.query(update_stmt)

        # Wait for the query to finish
        query_job.result()

        # Output the number of rows affected
        print("Affected rows: {}".format(query_job.num_dml_affected_rows))
