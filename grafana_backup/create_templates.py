import json
from grafana_backup.dashboardApi import create_templates, get_grafana_version, search_templates, update_templates
from packaging import version


def main(args, settings, file_path):
    grafana_url = settings.get('GRAFANA_URL')
    http_post_headers = settings.get('HTTP_POST_HEADERS')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')

    try:
        grafana_version = get_grafana_version(grafana_url, verify_ssl, http_get_headers)
    except KeyError as error:
        if not grafana_version:
            raise Exception("Grafana version is not set.") from error

    minimum_version = version.parse('9.4.0')

    if minimum_version <= grafana_version:
        with open(file_path, 'r') as f:
            data = f.read()

        result = search_templates(grafana_url, http_post_headers, verify_ssl, client_cert, debug)
        status_code = result[0]
        existing_templates = []
        if status_code == 200:
            # Successfully received list of templates.
            # Append templates to list of existing templates
            for ecp in result[1]:
                existing_templates.append(ecp["name"])

        templates = json.loads(data)
        for cp in templates:
            if cp["name"] in existing_templates:
                print("Templates {0} already exists, updating".format(cp["name"]))
                result = update_templates(cp["name"], json.dumps(cp), grafana_url, http_post_headers, verify_ssl, client_cert, debug)
                if result[0] == 202:
                    print("Successfully updated templates")
                else:
                    print("[ERROR] Templates {0} failed to update. Return code:{1} - {2}".format(cp["name"], result[0], result[1]))
            else:
                print("Templates {0} does not exist, creating".format(cp["name"]))
                result = create_templates(cp["name"], json.dumps(cp), grafana_url, http_post_headers, verify_ssl, client_cert, debug)
                if result[0] == 202:
                    print("Successfully create templates")
                else:
                    print("[ERROR] Templates {0} failed to create. Retufn code:{1} - {2}".format(cp["name"], result[0], result[1]))
    else:
        print("Unable to create templates, requires Grafana version {0} or above. Current version is {1}".format(minimum_version, grafana_version))
