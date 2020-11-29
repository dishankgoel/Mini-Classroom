from urllib.parse import unquote

def bytetostr(string):
    return string.decode("utf-8")

class HttpParser():

    def __init__(self, sock, buffer_size):

        self.sock = sock
        self.buffer_size = buffer_size
        self._remaining = []

        self.method = ""
        self.uri = ""
        self.version = ""

        self.headers = {}
    
        self._len_body_parsed = 0
        self.body = b""

        self.requested_path = ""
        self.query_string = {}
        self.form_data = {}

        self.first_line_complete = False
        self.headers_complete = False
        self.body_complete = False
        self.finish = False

    def get_headers(self):
        return self.headers

    def get_body(self):
        return self.body
    
    def get_uri(self):
        return self.uri
    
    def get_method(self):
        return self.method
    
    def get_version(self):
        return self.version

    def get_requested_path(self):
        return self.requested_path
        
    def get_query_string(self):
        return self.query_string

    def get_form_data(self):
        return self.form_data

    def get_sock_data(self):
        return self.sock.recv(self.buffer_size)

    def parse_first_line(self):

        if self._remaining == []:
            return
        first_line = self._remaining[0]
        method, uri, version = first_line.split()
        
        self.method = bytetostr(method)
        self.uri = bytetostr(uri)
        self.version = bytetostr(version)
        self.first_line_complete = True

        # Remove first line after parsing
        self._remaining.pop(0)  

    def parse_headers(self):
        
        parsed = 0
        for line in self._remaining:
            if line == b'':
                self.headers_complete = True
                break

            header, val = line.split(b": ")
            val = val.strip()
            self.headers[bytetostr(header)] = bytetostr(val)
            parsed += 1

        self._remaining = self._remaining[parsed+1:]

    def parsing_complete(self):
        self.body = bytetostr(self.body)
        self.body_complete = True
        self.finish = True

    
    def parse_body(self):
        if "Content-Length" not in self.headers:
            self.parsing_complete()
        else:
            if(self._len_body_parsed < int(self.headers["Content-Length"])):
                new_data = self._remaining[0]
                self.body += new_data
                self._len_body_parsed += len(new_data)
                self._remaining = []
                if(self._len_body_parsed == int(self.headers["Content-Length"])):
                    self.parsing_complete()    
            else:
                self.parsing_complete()
            
    def parse_query_string(self):
        '''Parse the uri for query string'''
        elements = self.uri.split("?")
        print(elements)
        self.requested_path = elements[0]
        self.requested_path.replace("..", "")
        if(len(elements) > 1):
            queries = elements[1].split("&")
            for query in queries:
                field, val = query.split("=")
                field = unquote(field).replace("+", " ")
                val = unquote(val).replace("+", " ")
                self.query_string[field] = val

    def parse_form_data(self):
        '''Parse the body for POST form data'''
        if(self.body == "" or self.body == b""):
            return
        form = self.body.split("&")
        for data in form:
            field, val = data.split("=")
            field = unquote(field).replace("+", " ")
            val = unquote(val).replace("+", " ")
            self.form_data[field] = val

    def parse(self):

        while not self.finish:
            data = self.get_sock_data()
            if not data:
                break
            self._remaining.extend(data.split(b"\r\n"))
            if not self.first_line_complete:
                self.parse_first_line()
            
            if not self.headers_complete:
                self.parse_headers()
            
            if not self.body_complete:
                self.parse_body()

        self.parse_query_string()
        self.parse_form_data()


status_reasons = {
    # Status Codes
    # Informational
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',

    # Successful
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi Status',
    226: 'IM Used',

    # Redirection
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',

    # Client Error
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    426: 'Upgrade Required',

    # Server Error
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    507: 'Insufficient Storage',
    510: 'Not Extended',
}
class HttpResponse():

    def __init__(self, sock):

        self.sock = sock
        
        self.body = b""
        self.headers = ""
        self.first_line = ""

    def prepare_first_line(self, status_code):
        self.first_line = "{} {} {}\r\n".format("HTTP/1.0", status_code, status_reasons[status_code])

    def prepare_headers_and_body(self, headers, body):

        self.body = body
        if len(body) != 0:
            headers["Content-Length"] = len(body)
        for header in headers:
            val = headers[header]
            self.headers += "{}: {}\r\n".format(header, val)

    
    def respond(self, status_code, headers, body):

        self.prepare_first_line(status_code)
        self.prepare_headers_and_body(headers, body)

        response = bytes(self.first_line + self.headers + "\r\n", "utf-8") + self.body

        self.sock.sendall(response)
