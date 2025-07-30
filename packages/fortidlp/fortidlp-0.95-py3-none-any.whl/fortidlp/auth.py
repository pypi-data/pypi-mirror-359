import requests

class AuthenticationHandler:
      
    def test_authentication(self, headers, host):
        data = None
        status = False
        response_headers = None
        urls = ['api/v2/users/search', 'api/v2/dashboards']

        for url in urls:

            url = f'https://{host}/{url}'
            try:
                res = requests.get(url, headers=headers, verify=False)
                res_code = res.status_code
                status = False
                if res_code == 401:
                    data = "Unauthorized"
                elif res_code == 403:
                    data = "Forbidden"
                elif res_code == 404:
                    data = "Not Found"
                elif res_code == 500:
                    data = "Internal Server Error"
                else:
                    data = res
                    status = True
                    response_headers = res.headers
                    return status, data, response_headers

            except requests.exceptions.RequestException as err:
                raise SystemExit(err) from err
        
        return status, data, response_headers

    def get_headers(self, fdlp_host, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        status, data, res_headers = self.test_authentication(headers, fdlp_host)
        return (headers, fdlp_host) if status else (None, data)