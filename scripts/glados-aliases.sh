#!/bin/bash

# Create glados aliases
alias watch-glados-service='watch -c SYSTEMD_COLORS=1 systemctl status glados.service'
alias start-glados-service='sudo systemctl start glados.service'
alias stop-glados-service='sudo systemctl stop glados.service'
