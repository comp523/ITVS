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
   - `-o --output-file` specify .xlsx output filename
   - *`-i --input-file` include a list of subreddits from one or more text files (space-delimited)
   - *`-s --subreddit` specify one or more subreddits from the command line (space-delimited)
 - Optional
   - `-b --before` include posts on or before specified date
 
  *Only one of `-i` or `-s` is required, though multiple of each may be specified.
 
#### Date Range

Dates for the **`-a --after`** and **`-b --before`** options are specified in
[ISO 8601](http://www.iso.org/iso/home/standards/iso8601.htm) format, specifically YYYY-MM-DD.

#### Subreddit Selection

There are two ways to specify the set of subreddits to traverse: using the **`-i --input-file`** option,
or using the **`-s --subreddit`** option. Using **`-i`** a plain text file may be specified that contains
a space-delimited list of subreddits. The **`-s`** option may be used to specify one or more space-delimited
subreddits directly from the command line.  
At least one of these options must be specified.

***

### Examples

#### Specify subreddits inline

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -s vape vaping e-cigs -a 2016-08-26 -o reddit_data.xlsx \-/
{% endcapture %}

{% include demo.html %}  

**`-s`** can also be used multiple times

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -s vape -s vaping -s e-cigs -a 2016-08-26 -o reddit_data.xlsx \-/
{% endcapture %}

{% include demo.html %}

#### Specify subreddits from file

{% capture tab-names %}
Terminal
subs.txt
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -i subs.txt -a 2016-08-26 -o reddit_data.xlsx \-/
vape vaping e-cigs
{% endcapture %}

{% include demo.html %}

**`-i`** can also be used to include multiple files

{% capture tab-names %}
Terminal
subs1.txt
subs2.txt
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -i subs1.txt subs2.txt -a 2016-08-26 -o reddit_data.xlsx \-/
vape vaping e-cigs \-/
vapenation e-juice
{% endcapture %}

{% include demo.html %}

multiple files may also be specified with separate **`-i`** flags

{% capture tab-names %}
Terminal
subs1.txt
subs2.txt
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -i subs1.txt -i subs2.txt -a 2016-08-26 -o reddit_data.xlsx \-/
vape vaping e-cigs \-/
vapenation e-juice
{% endcapture %}

{% include demo.html %}

#### Specify subreddits inline and from a file

{% capture tab-names %}
Terminal
subs.txt
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -i subs.txt -s vapenation e-juice -a 2016-08-26 -o reddit_data.xlsx \-/
vape vaping e-cigs
{% endcapture %}

{% include demo.html %}

#### Specify an end date

{% capture tab-names %}
Terminal
subs.txt
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -i subs.txt -a 2016-08-26 -b 2016-09-02 -o reddit_data.xlsx \-/
vape vaping e-cigs
{% endcapture %}

{% include demo.html %}