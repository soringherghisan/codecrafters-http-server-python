# A toy HTTP server made with Python.
Done via the tutorial from codecrafters.io -> https://app.codecrafters.io/courses/http-server
It has some basic functionality:
* read/parse http status line and headers 
* read/parse payload of Post requests
* compose and send basic response - either 200, 201 or 404 - with or without payload.
* supports multiple concurrent clients via threading 