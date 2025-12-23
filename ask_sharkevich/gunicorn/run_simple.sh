#!/bin/bash

$"gunicorn" "--bind" "localhost:8081" "--workers" 1 "--threads" 1 "--timeout" 0 "simple"