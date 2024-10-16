#!/usr/bin/env bash

poetry run hypercorn linkpulse.main:app --reload