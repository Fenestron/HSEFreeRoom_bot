#!/usr/bin/env bash

# open file test.data for reading
exec 6<file.pid
# read until end of file
while read -u 6 dta
do
  kill -9 "$dta" 
done
# close file test.data
exec 6<&-

> file.pid
