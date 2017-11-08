#!/bin/bash

echo "Starting Infrary Pre-Ansible setup..."

echo "Checking for Ansible Galaxy requirements..."

if [ ! -z "$REQUIREMENTS" ] && [ "$REQUIREMENTS" != "NO" ] && [ "$REQUIREMENTS" != "0" ]; then
    echo "ENV REQUIREMENTS is set. Will try to download packages requested in /requirements.yml"
    ansible-galaxy install -r /requirements.yml
fi


/bin/bash