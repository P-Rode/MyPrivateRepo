#!/bin/bash

var="Volvo Passat Skoda"
for i in $var
do
   p="$p"$'\n'"$i"  
done
echo "$p" #double quotes required, but -e not required


body="Start:"
body="Name of failed jobb is $2"$'\n'"$body"
body="Url to failed jobb is $2"$'\n'"$body"
echo "$body"


printf '%s\n' $body


