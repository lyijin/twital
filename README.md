# twital: automate lab weekly newsletter #

"twital" stands for "This Week in the Aranda Lab", by the way. Creative naming is not my forte.

Note: for security concerns, I have modified the script to remove several addresses. These addresses appears as "REDACTED", so you'll have to plug your own details to get it to work. I have also excluded client_secret.json, which is required for task #1.

## Overview of process ##
There's basically three tasks:

1. Parse lab Google Calendar.
2. Find a way to email the text out.
3. Set a timer to do it once every week.

## Parsing Google Calendar ##
Surprisingly NOT the hardest part of the project. #2 was a bigger PITA.

Google has provided sample code to parse one's personal calendar.
https://developers.google.com/google-apps/calendar/quickstart/python

It's supposed to generate two files: .credentials and client_secret.json if it is unable to find these files on your system. I WAS UNABLE TO GENERATE THEM ON BASH: THE TEXT-MODE AUTHENTICATION DID NOT WORK FOR SOME REASON. I had to run the code on Windows to authenticate via my browser to generate these two files, then move them over to my Debian system. -__-"

Once parsed, there's a lot of unexplained mojo in the script to deal with parsing dates and times. I've standardised the script to use a specific timezone (GMT+3) to properly output event start and end times.

## Emailing the text out ##
Again, RTFM and follow instructions.
https://wiki.debian.org/GmailAndExim4

I tried using Yahoo Mail and it didn't work. I guess there's a reason why Gmail is dominating the free email space.

## Setting up the weekly trigger ##
crontab -e
0 9 * * 0 cd /home/liewy/kaust/twital/ && ./mail_twital.sh

(cron, by default, runs from ~, so one needs to cd into the folder containing the script.)