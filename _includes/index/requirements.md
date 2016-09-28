# Use Cases

### Data Collection

**[ranalyze](/ITVS/ranalyze)** can be used to collect data from the social media website
[reddit](https://reddit.com). Data can be gathered from multiple subreddits, and includes
information such as post title, post content, external url, up-vote count, comment count,
comment text, etc. This data can be automatically updated to reflect up-to-date information
on non-static fields such as up-vote count, comment count, etc.

### Data Analysis

**[ranalyze](/ITVS/ranalyze)** can also be used to flexibly extract data categorically,
or based on the presence and/or frequency of specified keywords.

### ITV Identification

*tbd* provides a machine learning approach to the identification of internet tobacco vendors
(ITV). Through the analysis of various metrics, a website is assigned a score representing
the likelihood that it is, in fact, an ITV.

# Requirements

### [ranalyze](/ITVS/ranalyze)

This utility will scrape a user specified set of subreddits and over a particular date range 
and output the result into a relational database for further manipulation and analysis. 
Within the limits of the reddit API, every post, comment, and relevant data and metadata
(title, url, up-vote count, up-vote ratio, comment body, etc.) will be collected and stored.
This process will run on a regular schedule and update non-static metadata in an incremental
fashion.
