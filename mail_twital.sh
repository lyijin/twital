#!/bin/bash

# generate email, and on success, use system mail to send to lab mailing list
python3 generate_twital.py && cat <(echo -n \<pre\>) email_contents.txt <(echo \</pre\>) | mail -r 'Yi Jin Liew <REDACTED@gmail.com>' -a 'Content-Type: text/html' -s 'This Week in the Aranda Lab' REDACTED@kaust.edu.sa && rm -f email_contents.txt
