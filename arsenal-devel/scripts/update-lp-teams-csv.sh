#!/bin/bash
#
# Get the packages to which teams are subscribed in Launchpad and make a
# csv file like the package to team mapping with those subscriptions in
# it

cd /home/ubuntureports/source/arsenal/scripts/

for TEAM in checkbox-bugs desktop-packages documentation-packages dx-packages edubuntu-bugs foundations-bugs kernel-packages kubuntu-bugs lubuntu-packaging ubuntu-apps-bugs ubuntu-phonedations-bugs ubuntu-security-bugs ubuntu-server ubuntu-sdk-bugs ubuntu-webapps-bugs ubuntuone-hackers unity-api-bugs unity-ui-bugs xubuntu-bugs
do
    /home/ubuntureports/source/arsenal/scripts/ls-team-subscribed-packages.py --team $TEAM --csv >> lp-package-team-mapping.csv.tmp
done

mv lp-package-team-mapping.csv.tmp lp-package-team-mapping.csv
