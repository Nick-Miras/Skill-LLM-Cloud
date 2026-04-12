#!/bin/sh

python propagate_ids.py \
    --input-csv "../data/raw/Validators' Skill Sheet - Extracted Job Descriptions.csv" \
    --output-csv "../data/cleaned/Cleaned Extracted Job Descriptions.csv"
