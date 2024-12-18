#!/bin/bash

isMounted() {
        findmnt "$1" >/dev/null;
}

# Show a welcome message on shell login.
echo -e ''
if isMounted "/mnt/glados-backup";
        then echo -e '\e[38;5;154m >\033[1;30m Glados database backup :\e[38;5;154m Mounted.'
        else echo -e '\e[38;5;154m >\033[1;30m Glados database backup :\033[91m Not mounted.'
fi
echo -e '\e[38;5;154m >\033[1;30m Watch glados service   : watch-glados-service'
echo -e '\e[38;5;154m >\033[1;30m Start glados service   : start-glados-service'
echo -e '\e[38;5;154m >\033[1;30m Stop glados service    : stop-glados-service'
echo -e '\e[38;5;154m >\033[1;30m Mount glados backup    : mount-glados-backup'
echo -e ''
