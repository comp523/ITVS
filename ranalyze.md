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
2. Navigate to your preferred installation directory  
    `cd ~`
3. Download the latest update  
    `wget -O itvs.tgz https://github.com/comp523/ITVS/tarball/master`
4. Extract the archive  
    `tar -xzf itvs.tgz`
5. Navigate to the ranalyze folder  
    `cd comp523-ITVS-*/ranalyze`
6. Run the installer  
    `bash install-ranalyze.sh`

***

## Commands

To run commands in the module, you must be in the ranalyze folder:  
`python -m ranalyze command [options]`

Commands:

 - `create-db` - Create a formatted database for use with ranalyze
 - `import` - Import a list of Reddit post/comment permalinks to a local database
 - `scrape` - Scrape Reddit for new posts and comments
 - `search` - Search a local database for specific keywords

## Usage

### create-db

```
ranalyze create-db [-h] name

positional arguments:
  name        File name of the SQLite database to create

optional arguments:
  -h, --help  show this help message and exit
```

### import

```
ranalyze import [-h] -i IMPORT [-d DATABASE_FILE]

optional arguments:
  -h, --help            show this help message and exit

import:
  -i IMPORT, --import IMPORT
                        file to import permalinks from

database:
  -d DATABASE_FILE, --database-file DATABASE_FILE
                        analysis data will be written to this SQLite file
```

### scrape

```
ranalyze scrape [-h] [-d DATABASE_FILE] [-c CONFIG_FILE]
                       [-s SUBREDDITS [SUBREDDITS ...]]

optional arguments:
  -h, --help            show this help message and exit

database:
  -d DATABASE_FILE, --database-file DATABASE_FILE
                        analysis data will be written to this SQLite file

configuration:
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        load configuration from file

subreddit selection:
  -s SUBREDDITS [SUBREDDITS ...], --subreddit SUBREDDITS [SUBREDDITS ...]
                        subreddit to analyze, may be a single value, or a
                        space-delimited list
```

### search

```
ranalyze search [-h] -d DATABASE_FILE [-f {json,csv}]
                       [-c COLUMNS [COLUMNS ...]] [-e EXPRESSION] [-k KEYWORD]
                       [-a AFTER] [-b BEFORE] [-s SUBREDDIT]

optional arguments:
  -h, --help            show this help message and exit

database:
  -d DATABASE_FILE, --database-file DATABASE_FILE
                        SQLite database to search

output:
  -f {json,csv}, --format {json,csv}
                        can be used to specify output format, available.
                        default is json
  -c COLUMNS [COLUMNS ...], --columns COLUMNS [COLUMNS ...]
                        space-delimited list of columns to include in results

search criteria:
  -e EXPRESSION, --expression EXPRESSION
                        search using a boolean expression in the form: [not]
                        "KEYWORD1" [and|or] [not] "KEYWORD2"
  -k KEYWORD, --keyword KEYWORD
                        specify search keywords/phrases
  -a AFTER, --after AFTER
                        only search posts on or after a specified date
  -b BEFORE, --before BEFORE
                        only search posts on or before a specified date
  -s SUBREDDIT, --subreddit SUBREDDIT
                        restrict search to specified subreddits
```

***

## Command Options

### create-db

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze create-db reddit.db
{% endcapture %}

{% include demo.html %}

### import

{% capture tab-names %}
Terminal
posts.csv
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze -d reddit.db -i posts.csv \-/
"https://www.reddit.com/r/Vaping/comments/56bow0/safe_to_say_i_found_my_brand/"
"https://www.reddit.com/r/Vaping/comments/56bq0a/hellhound_handcheck/"
"https://www.reddit.com/r/Vaping/comments/56bq5i/i_love_a_good_handcheck_but_even_the_crappy_blu/"
"https://www.reddit.com/r/Vaping/comments/56br0j/if_your_tanks_spits_should_you_swallow/"
"https://www.reddit.com/r/Vaping/comments/56btob/here_you_go_guys_this_is_one_of_my_favourites_ive/"
{% endcapture %}

{% include demo.html %}

### scrape

#### Specify options inline

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze scrape -s vape vaping e-cigs -a 2016-08-26 -d reddit.db
{% endcapture %}

{% include demo.html %}  

**`-s`** can also be used multiple times

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze scrape -s vape -s vaping -s e-cigs -d reddit.db
{% endcapture %}

{% include demo.html %}

#### Specify options from a configuration file

{% capture tab-names %}
Terminal
config.yml
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze scrape -c config.yml \-/
database: reddit.db
subreddits:
  - vape
  - vaping
  - e-cigs
{% endcapture %}

{% include demo.html %}

#### Specify options inline and from a configuration file

{% capture tab-names %}
Terminal
config.yml
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze scrape -c config.yml -s vapenation \-/
database: reddit.db
subreddits:
  - vape
  - vaping
  - e-cigs
{% endcapture %}

{% include demo.html %}

*all subreddits from config.yml and specified with the **`-s`** flag will be scraped.

### search

#### Basic Keyword Search

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze search -d reddit.db -k vape vapenation
{% endcapture %}

{% include demo.html %}

*This example is equivalent to an expression search using `'vape' or 'vapenation'`

#### Complex Expression Search

**Example expression:** `'FDA' and not ('deeming' or 'popcorn')`  
**Explanation:** Search for posts and comments containing "FDA" containing
neither "deeming" nor "popcorn".

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze search -d reddit.db -e "'FDA' and not ('deeming' or 'popcorn')"
{% endcapture %}

{% include demo.html %}

#### Subreddit Restricted Search

**Default search includes all subreddits in the database**

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze search -d reddit.db -k vape vapenation -s vaping
{% endcapture %}

{% include demo.html %}

*This search will limit results to the `vaping` subreddit

#### Date Restricted Search

Dates are specified in [ISO 8601](http://www.iso.org/iso/home/standards/iso8601.htm)
format, specifically YYYY-MM-DD.

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze search -d reddit.db -k vape vapenation -a 2016-09-20 -b 2016-09-30
{% endcapture %}

{% include demo.html %}

*This search will limit results to the inclusive date-range [9/20/16, 9/30/16]

#### Output Format

**Default output format is JSON**

Output as CSV:

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze search -d reddit.db -k vape vapenation -f csv
{% endcapture %}

{% include demo.html %}

**Default output includes all fields**

Output only certain columns:

{% capture tab-names %}
Terminal
{% endcapture %}

{% capture tabs %}
<span class="terminal-prompt">~/ITVS $</span> python -m ranalyze search -d reddit.db -k vape vapenation -c id permalink text_content
{% endcapture %}

{% include demo.html %}
