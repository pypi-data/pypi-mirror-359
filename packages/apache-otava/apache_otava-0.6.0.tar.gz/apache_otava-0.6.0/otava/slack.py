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
from math import isinf
from typing import Dict, List

from pytz import UTC
from slack_sdk import WebClient

from otava.data_selector import DataSelector
from otava.series import AnalyzedSeries, ChangePointGroup


@dataclass
class NotificationError(Exception):
    message: str


@dataclass
class SlackConfig:
    bot_token: str


class SlackNotification:
    tests_with_insufficient_data: List[str]
    test_analyzed_series: Dict[str, AnalyzedSeries]
    since: datetime

    def __init__(
        self,
        test_analyzed_series: Dict[str, AnalyzedSeries],
        data_selection_description: str = None,
        since: datetime = None,
    ):
        self.data_selection_description = data_selection_description
        self.since = since
        self.tests_with_insufficient_data = []
        self.test_analyzed_series = dict()
        for test, series in test_analyzed_series.items():
            if series:
                self.test_analyzed_series[test] = series
            else:
                self.tests_with_insufficient_data.append(test)

    def __init_insufficient_data_dispatch(self):
        dispatch = [
            self.__text_block(
                "header",
                "plain_text",
                "Otava found insufficient data for the following tests :warning:",
            )
        ]
        if self.data_selection_description:
            dispatch.append(self.__data_selection_block())
        return dispatch

    def __init_report_dispatch(self):
        dispatch = [self.__header()]
        if self.data_selection_description:
            dispatch.append(self.__data_selection_block())
        if self.since:
            dispatch.append(self.__report_selection_block())
        return dispatch

    def __minimum_dispatch_length(self):
        min = 1  # header
        if self.data_selection_description:
            min += 1
        if self.since:
            min += 1
        return min

    # A Slack message can only contain 50 blocks so
    # large summaries must be split across messages.
    def create_dispatches(self) -> List[List[object]]:
        dispatches = []
        cur = self.__init_insufficient_data_dispatch()
        for test_name in self.tests_with_insufficient_data:
            if len(cur) == 50:
                dispatches.append(cur)
                cur = self.__init_insufficient_data_dispatch()
            cur.append(self.__plain_text_section_block(test_name))

        if len(cur) > self.__minimum_dispatch_length():
            dispatches.append(cur)

        dates_change_points = {}
        for test_name, analyzed_series in self.test_analyzed_series.items():
            for group in analyzed_series.change_points_by_time:
                cpg_time = datetime.fromtimestamp(group.time, tz=UTC)
                if self.since and cpg_time < self.since:
                    continue
                date_str = self.__datetime_to_str(cpg_time)
                if date_str not in dates_change_points:
                    dates_change_points[date_str] = {}
                dates_change_points[date_str][test_name] = group

        cur = self.__init_report_dispatch()
        for date in sorted(dates_change_points):
            add = [
                self.__block("divider"),
                self.__title_block(date),
            ] + self.__dates_change_points_summary(dates_change_points[date])

            if not len(cur) + len(add) < 50:
                dispatches.append(cur)
                cur = self.__init_report_dispatch()

            cur = cur + add

        if len(cur) > self.__minimum_dispatch_length():
            dispatches.append(cur)

        return dispatches

    @staticmethod
    def __datetime_to_str(date: datetime):
        return str(date.strftime("%Y-%m-%d %H:%M:%S"))

    @staticmethod
    def __block(block_type: str, content: Dict = None):
        block = {"type": block_type}
        if content:
            block.update(content)
        return block

    @classmethod
    def __text_block(cls, type, text_type, text):
        return cls.__block(
            type,
            content={
                "text": {
                    "type": text_type,
                    "text": text,
                }
            },
        )

    @classmethod
    def __fields_section(cls, fields_text):
        def field_block(text):
            return {"type": "mrkdwn", "text": text}

        return cls.__block("section", content={"fields": [field_block(t) for t in fields_text]})

    @classmethod
    def __plain_text_section_block(cls, text):
        return cls.__text_block("section", "plain_text", text)

    def __header(self):
        header_text = (
            "Otava has detected change points"
            if self.test_analyzed_series
            else "Otava did not detect any change points"
        )
        return self.__text_block("header", "plain_text", header_text)

    def __data_selection_block(self):
        return self.__plain_text_section_block(self.data_selection_description)

    def __report_selection_block(self):
        return self.__fields_section(["Report Since", self.__datetime_to_str(self.since)])

    @classmethod
    def __title_block(cls, name):
        return cls.__text_block("section", "mrkdwn", f"*{name}*")

    def __dates_change_points_summary(self, test_changes: Dict[str, ChangePointGroup]):
        fields = []
        for test_name, group in test_changes.items():
            fields.append(f"*{test_name}*")
            summary = ""
            for change in group.changes:
                change_percent = change.forward_change_percent()
                change_emoji = self.__get_change_emoji(test_name, change)
                if isinf(change_percent):
                    report_percent = change_percent
                # Avoid rounding decimal change points to zero
                elif -5 < change_percent < 5:
                    report_percent = f"{change_percent:.1f}"
                else:
                    report_percent = round(change_percent)
                summary += f"{change_emoji} *{change.metric}*: {report_percent}%\n"
            fields.append(summary)

        sections = []
        i = 0
        while i < len(fields):
            section_fields = []
            while len(section_fields) < 10 and i < len(fields):
                section_fields.append(fields[i])
                i += 1
            sections.append(self.__fields_section(section_fields))

        return sections

    def __get_change_emoji(self, test_name, change):
        metric_direction = self.test_analyzed_series[test_name].metric(change.metric).direction
        regression = metric_direction * change.forward_change_percent()
        if regression >= 0:
            return ":large_blue_circle:"
        else:
            return ":red_circle:"


class SlackNotifier:
    __client: WebClient

    def __init__(self, client: WebClient):
        self.__client = client

    def notify(
        self,
        test_analyzed_series: Dict[str, AnalyzedSeries],
        selector: DataSelector,
        channels: List[str],
        since: datetime,
    ):
        dispatches = SlackNotification(
            test_analyzed_series,
            data_selection_description=selector.get_selection_description(),
            since=since,
        ).create_dispatches()
        if len(dispatches) > 3:
            raise NotificationError(
                "Change point summary would produce too many Slack notifications"
            )
        for channel in channels:
            for blocks in dispatches:
                self.__client.chat_postMessage(channel=channel, blocks=blocks)
