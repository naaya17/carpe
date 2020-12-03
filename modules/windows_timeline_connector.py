# -*- coding: utf-8 -*-
"""module for Timeline."""
import os
from modules import manager
from modules import interface
from modules import logger
from modules.windows_timeline import lv1_windows_timeline as wt


class WindowsTimelineConnector(interface.ModuleConnector):

    NAME = 'windows_timeline_connector'
    DESCRIPTION = 'Module for windows_timeline'

    _plugin_classes = {}

    def __init__(self):
        super(WindowsTimelineConnector, self).__init__()

    def Connect(self, par_id, configuration, source_path_spec, knowledge_base):

        query_separator = self.GetQuerySeparator(source_path_spec, configuration)
        path_separator = self.GetPathSeparator(source_path_spec)
        this_file_path = os.path.dirname(os.path.abspath(__file__)) + path_separator + 'schema' + path_separator

        yaml_list = [this_file_path + 'lv1_os_win_windows_timeline.yaml']
        table_list = ['lv1_os_win_windows_timeline']

        if not self.check_table_from_yaml(configuration, yaml_list, table_list):
            return False

        query = f"SELECT name, parent_path, extension FROM file_info WHERE (par_id='{par_id}' " \
                f"and name like '%ActivitiesCache.db') and ("

        for user_accounts in knowledge_base._user_accounts.values():
            for hostname in user_accounts.values():
                if hostname.identifier.find('S-1-5-21') == -1:
                    continue
                query += f"parent_path like 'root{query_separator}Users{query_separator}{hostname.username}{query_separator}AppData{query_separator}Local{query_separator}ConnectedDevicesPlatform%' or "
        query = query[:-4] + ");"

        windows_timeline_files = configuration.cursor.execute_query_mul(query)

        if windows_timeline_files == -1:
            print("There are no timeline files")
            return False

        if len(windows_timeline_files) == 0:
            print("There are no timeline files")
            return False


        insert_data = []
        for timeline in windows_timeline_files:
            timeline_path = timeline[1][timeline[1].find(path_separator):] + path_separator + timeline[0]  # document full path
            file_name = timeline[0]
            output_path = configuration.root_tmp_path + path_separator + configuration.case_id + path_separator + configuration.evidence_id + path_separator + par_id
            if not os.path.exists(output_path):
                os.mkdir(output_path)
            self.ExtractTargetFileToPath(
                source_path_spec=source_path_spec,
                configuration=configuration,
                file_path=timeline_path,
                output_path=output_path)

            self.ExtractTargetFileToPath(
                source_path_spec=source_path_spec,
                configuration=configuration,
                file_path=timeline_path + '-wal',
                output_path=output_path)

            self.ExtractTargetFileToPath(
                source_path_spec=source_path_spec,
                configuration=configuration,
                file_path=timeline_path + '-journal',
                output_path=output_path)

            self.ExtractTargetFileToPath(
                source_path_spec=source_path_spec,
                configuration=configuration,
                file_path=timeline_path + '-shm',
                output_path=output_path)

            fn = output_path + path_separator + file_name

            time_zone = knowledge_base.time_zone

            # WindowsTimeline
            result = wt.WINDOWSTIMELINE(fn)
            if not result:
                return False
            for timeline in result:
                insert_data.append(
                    tuple([par_id, configuration.case_id, configuration.evidence_id,
                           str(timeline.program_name).replace('\\', '/'),
                           str(timeline.display_name), str(timeline.content),
                           str(timeline.activity_type), str(timeline.focus_seconds),
                           str(configuration.apply_time_zone(timeline.start_time, time_zone)),
                           str(configuration.apply_time_zone(timeline.end_time, time_zone)),
                           str(timeline.activity_id), str(timeline.platform),
                           str(configuration.apply_time_zone(timeline.created_time, time_zone)),
                           str(configuration.apply_time_zone(timeline.created_in_cloud_time, time_zone)),
                           str(configuration.apply_time_zone(timeline.last_modified_time, time_zone)),
                           str(configuration.apply_time_zone(timeline.last_modified_on_client_time, time_zone)),
                           str(configuration.apply_time_zone(timeline.original_last_modified_on_client_time, time_zone)),
                           str(timeline.local_only_flag), str(timeline.group),
                           str(timeline.clipboardpayload), str(timeline.timezone)]))
        query = "Insert into lv1_os_win_windows_timeline " \
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        configuration.cursor.bulk_execute(query, insert_data)
manager.ModulesManager.RegisterModule(WindowsTimelineConnector)
