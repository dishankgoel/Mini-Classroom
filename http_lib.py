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
            
class HttpResponse():

    def __init__(self, sock, buffer_size):

        self.sock = sock
        self.buffer_size = buffer_size

    
