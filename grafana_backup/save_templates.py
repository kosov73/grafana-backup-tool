import os
from grafana_backup.dashboardApi import search_templates, get_grafana_version
from grafana_backup.commons import to_python2_and_3_compatible_string, print_horizontal_line, save_json
from packaging import version


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')
    folder_path = '{0}/templates/{1}'.format(backup_dir, timestamp)
    log_file = 'templates_{0}.txt'.format(timestamp)
    grafana_version_string = settings.get('GRAFANA_VERSION')

    if grafana_version_string:
        grafana_version = version.parse(grafana_version_string)

    try:
        grafana_version = get_grafana_version(grafana_url, verify_ssl, http_get_headers)
    except KeyError as error:
        if not grafana_version:
            raise Exception("Grafana version is not set.") from error

    minimum_version = version.parse('9.0.0')
    if minimum_version <= grafana_version:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        templates = get_all_templates_in_grafana(
            grafana_url, http_get_headers, verify_ssl, client_cert, debug)
        save_templates(
            'templates', templates, folder_path, pretty_print)
    else:
        print("Unable to save templates, requires Grafana version {0} or above. Current version is {1}".format(
            minimum_version, grafana_version))

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def get_all_templates_in_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status, content) = search_templates(
        grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    if status == 200:
        templates = content
        print("There are {0} templates: ".format(len(templates)))
        for template in templates:
            print("name: {0}, template: {1}".format(to_python2_and_3_compatible_string(
                template['name']), to_python2_and_3_compatible_string(template['template'])))
        return templates
    else:
        print("query templates failed, status: {0}, msg: {1}".format(
            status, content))
        return []


def save_templates(file_name, templates, folder_path, pretty_print):
    file_path = save_json(file_name, templates,
                          folder_path, 'templates', pretty_print)
    print_horizontal_line()
    print("templates are saved to {0}".format(file_path))
    print_horizontal_line()
