---
layout: default
title: ITVS | ranalyze
show_home_nav: true
enable_demo: true
---

# ranalyze: Reddit Analyzer

### Analysis tool to traverse a set of subreddits extracting posts and comments

***

## Installation

**NOTE:** only Linux is supported.

1. Open a bash terminal
2. Download the latest update  
    `wget -O itvs.tgz https://github.com/comp523/ITVS/tarball/master`
3. Extract the archive  
    `tar -xzf itvs.tgz`
4. Navigate to the ranalyze folder  
    `cd comp523-ITVS-*/ranalyze`
5. Run the installer  
    `bash install-ranalyze.sh`
    
### To create a properly formatted, empty database

1. Open a bash terminal
2. Run  
    `ranalyze create-db db_name.db`

***
 
## Command Line Interface

### Usage

```
ranalyze [-h] [-d DATABASE_FILE] [-s SUBREDDITS [SUBREDDITS ...]]
         [-a AFTER] [-b BEFORE] [-c CONFIG_FILE]

optional arguments:
  -h, --help            show this help message and exit

database:
  -d DATABASE_FILE, --database-file DATABASE_FILE
                        analysis data will be written to this SQLite file

subreddit selection:
  -s SUBREDDITS [SUBREDDITS ...], --subreddit SUBREDDITS [SUBREDDITS ...]
                        subreddit to analyze, may be a single value, or a
                        space-delimited list

date range:
  -a AFTER, --after AFTER
                        only analyze posts on or after this date
  -b BEFORE, --before BEFORE
                        only analyze posts on or before this date, defaults to
                        today

configuration:
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        load configuration from file
```

### Options

Options may be specified directly on the command line, or from a configuration file.
In case both are provided, options specified as command line arguments override
those from a configuration file. Configuration files should be in [YAML](http://yaml.org/) format.

 - Required
   - `date_range.after` include entries on or after specified date
   - `database` specify output database
   - `subreddits` set of subreddits to scrape
 - Optional
   - `date_range.before` include entries on or before specified date

 
#### Date Range

Dates are specified in [ISO 8601](http://www.iso.org/iso/home/standards/iso8601.htm)
format, specifically YYYY-MM-DD.

#### Subreddit Selection

There are two ways to specify the set of subreddits to traverse: as a parameter in a configuration file,
or using the **`-s --subreddit`** option. The **`-s`** option may be used to specify one or more space-delimited
subreddits directly from the command line.  
At least one of these options must be specified.

***

### Examples

#### Specify options inline

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -s vape vaping e-cigs -a 2016-08-26 -d reddit.db \-/
{% endcapture %}

{% include demo.html %}  

**`-s`** can also be used multiple times

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -s vape -s vaping -s e-cigs -a 2016-08-26 -d reddit.db \-/
{% endcapture %}

{% include demo.html %}

#### Specify options from a configuration file

{% capture tab-names %}
Terminal
config.yml
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -c config.yml \-/
database: reddit.db
subreddits:
  - vape
  - vaping
  - e-cigs
date_range:
  after: 2016-08-26
{% endcapture %}

{% include demo.html %}

#### Specify options inline and from a configuration file

{% capture tab-names %}
Terminal
config.yml
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> ranalyze -c config.yml -s vapenation -a 2016-08-26 \-/
database: reddit.db
subreddits:
  - vape
  - vaping
  - e-cigs
{% endcapture %}

{% include demo.html %}

*all subreddits from config.yml and specified with the **`-s`** flag will be scraped.
