#!/bin/bash

source clean.sh

source setup_env.sh

CLINGO_PREFIX="" poetry run python app.py

