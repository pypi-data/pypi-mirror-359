import json
from .. import input_outputs


class InputOutput(input_outputs.InputOutput):
    _body = None
    _request_method = None
    _script_name = ""
    _path_info = ""
    _query_string = ""
    _content_type = ""
    _protocol = ""
    _query_parameters = None
    _context_specifics = None
    _client_ip = None
    response = None

    def __init__(
        self,
        request_headers=None,
        body=None,
        request_method="GET",
        request_url="",
        script_name="",
        path_info="",
        query_string="",
        content_type="",
        protocol="",
        query_parameters=None,
        authorization_data=None,
        context_specifics=None,
        client_ip=None,
    ):
        self.set_request_method(request_method)
        self.set_body(body)
        self.set_request_headers(request_headers)
        self.set_request_url(request_url, script_name=script_name)
        self._path_info = path_info
        self._query_string = query_string
        self._content_type = content_type
        self._protocol = protocol
        self._query_parameters = query_parameters if query_parameters is not None else {}
        self._authorization_data = authorization_data
        self._context_specifics = context_specifics if context_specifics is not None else {}
        self._client_ip = client_ip if client_ip is not None else "127.0.0.1"

    def respond(self, body, status_code=200):
        self.response = {"body": body, "status_code": status_code, "headers": self._response_headers}
        return (body, status_code)

    def get_body(self):
        return self._body

    def has_body(self):
        return bool(self._body)

    def set_body(self, body):
        self._body = None
        if body:
            self._body = body if type(body) == str else json.dumps(body)

    def set_request_url(self, request_url, script_name=""):
        if request_url and script_name:
            raise ValueError("You cannot specify both request_url and script_name")
        self._script_name = request_url if request_url else script_name

    def get_request_method(self):
        return self._request_method

    def set_request_method(self, request_method):
        self._request_method = request_method.upper()

    def set_request_headers(self, request_headers):
        self._request_headers = {}
        if request_headers is None:
            request_headers = {}
        for key, value in request_headers.items():
            self._request_headers[key.lower()] = value

    def set_query_parameters(self, query_parameters):
        if query_parameters is None:
            self._query_parameters = {}
        else:
            self._query_parameters = query_parameters

    def get_script_name(self):
        return self._script_name

    def get_path_info(self):
        return self._path_info

    def get_query_string(self):
        return self._query_string

    def get_content_type(self):
        return self._content_type

    def get_protocol(self):
        return self._protocol

    def has_request_header(self, header_name):
        return header_name.lower() in self._request_headers

    def get_request_header(self, header_name, silent=True):
        if not self.has_request_header(header_name):
            if not silent:
                raise ValueError(f"Request header '{header_name}' not found in request")
            return ""
        return self._request_headers[header_name.lower()]

    def get_query_parameter(self, key):
        return self._query_parameters[key] if key in self._query_parameters else ""

    def get_query_parameters(self):
        return self._query_parameters

    def set_context_specifics(self, context_specifics):
        self._context_specifics = context_specifics

    def context_specifics(self):
        return self._context_specifics

    def get_client_ip(self):
        return self._client_ip
