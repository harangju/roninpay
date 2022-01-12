#!/bin/sh

config="slp-payment-config.json"

source ~/opt/miniconda3/etc/profile.d/conda.sh
conda activate roninpay
python generate_json.py
python pay.py $config
rm $config
conda deactivate
