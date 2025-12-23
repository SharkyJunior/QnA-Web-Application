#!/bin/bash

$"curl" "localhost:8081"

$"curl" "localhost:8081/?foo=bar"

$"curl" "-d" "{\"foo\":\"baz\"}" "localhost:8081/?foo=bar&foo=baz"