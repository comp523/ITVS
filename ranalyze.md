---
layout: default
title: ITVS | ranalyze
---

# ranalyze: Reddit Analyzer

### Analysis tool to traverse a set of subreddits extracting post information including:

 - Post title
 - Post date
 - Post URL (if not a self post)
 - Number of upvotes/downvotes
 
***
 
## Command Line Interface

`ranalyze [options]`

### Options

 - Required
   - `-a --after` include posts on or after specified date
   - `-o --output-file` specify *.xlsx output filename
   - *`-i --input-file` include a list of subreddits from a text file (space-delimited)
   - *`-s --subreddit` specify one or more subreddits from the command line (space-delimited)
 - Optional
   - `-b --before` include posts on or before specified date
 
  *Only one of `-i` or `-s` is required, though multiple of each may be specified.
 
#### Date Range

Dates for the **`-a --after`** and **`-b --before`** options arespecified in
[ISO 8601](http://www.iso.org/iso/home/standards/iso8601.htm) format, specifically YYYY-MM-DD.

#### Subreddit Selection

There are two ways to specify the set of subreddits to traverse: using the `-i --input-file` option,
or using the `-s --subreddit` option. Using `-i` a plain text file may be specified that contains
a space-delimited list of subreddits. The `-s` option may be used to specify one or more space-delimited
subreddits directly from the command line.  
At least one of these options must be specified.