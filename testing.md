---
layout: default
title: ITVS | Testing
---

# Ideal Plan

## Platform

Ranalyze is written in Python, so in order to utilize the ranalyze code directly, all automated unit testing will also use Python. In order to validate ranalyze's interfaces, HTTP and SQL requests will be employed from Python. System testing will be performed on various ranalyze deployments.

## Test Cases

Ranalyze is a simplistic tool that scrapes data from Reddit and stores it in a database. Because relatively little processing is done internally, the most likely points of failure are the interfaces that expose ranalyze to the outside world. Automated unit testing is required for the following interfaces:

 - **CLI (command line interface)**: verify that command line arguments are parsed correctly
 - **Reddit API**: verify that the correct data is being collected from the Reddit servers
 - **Database**: verify that data can be stored, updated, and retrieved correctly

These unit tests should run automatically with every commit to ensure nothing obvious breaks during development.
Because of ranalyze's simplicity, the best way to do system testing is to deploy it and monitor the resulting database. The clients requested a high degree of control over the output of ranalyze, so it is important to verify that any valid operation will not produce any unintended side affects. Test environments include:

 - **Long term deployment**: ensure that daily ranalyze runs over a week or more correctly update the database without corrupting older data
 - **Multiple high traffic subreddits**: ensure that ranalyze can cope with a high volume of data from multiple sources
 - **Changing configuration**: ensure that changing the ranalyze settings during deployment will not corrupt older data or break new data collection
 - **Database agnosticism**: ensure that the ranalyze database can be safely queried and modified by an outside user without breaking new data collection
 - **Reproducible behavior**: multiple deployments of ranalyze run simultaneously should produce exactly the same results

Comprehensive system testing will only occur after all required features have been implemented. Should there be any stretch goals, system testing must be performed again to ensure that new bugs were not introduced. System test deployments (that is, ranalyze installations on different operating systems and networks) should include development environments, the client's current production environment, and any likely candidates for future deployments. System tests should be performed by developers with oversight by the client to demonstrate proper use of the product, as well as gathering any last-minute client input.

***

# Intended Plan

We only have the time and resources for limited testing, but we should be able to cover all the most pressing requirements from the ideal plan.

## Platform

Python will be used for all automated unit testing. Travis will be used to automate testing on every git commit, and Slack bots will be used to monitor Travis build results. System testing will be performed on various ranalyze deployments.

## Test Cases

All interfaces from the ideal plan will be covered by unit tests. The following unit tests will validate individual ranalyze components to ensure they are functioning as intended:

 - **CLI testing** will ensure that ranalyze fails whenever it is given an invalid configuration. Note that ensuring ranalyze succeeds when given a correct configuration falls under system testing, and will not be covered by the unit tests.
 - **Reddit API testing** will collect data from a private subreddit (r/itvs_testing, moderated by reddit user dchiquit). The data will be validated against the data known to already be present in the subreddit. Note that this test must be updated if the subreddit is modified by posting, commenting, or voting.
 - **Database testing** will verify that retrieving previously stored data does not modify it, and that updating an existing post or comment is sucessful. 

Validating the schema is outside the scope of this test.
 
Planned system tests are as follows:

 - **Medium term deployment**: running a ranalyze deployment on an automated schedule over the course of a single day. This will ensure that ranalyze can successfully pick up new posts and comments without destroying old ones. In the interest of time, this test assumes that the time interval between collections is irrelevant, which is a fairly safe assumption.
 - **Multiple high traffic subreddits**: running ranalyze against a large number of popular subreddits. Most subreddits of interest to ITVS are relatively small, but for scalability it would be wise to ensure that ranalyze does not failed unexpectedly when given large datasets to process.
 - **Changing configuration**: adding new subreddits, removing old ones, and changing date settings between ranalyze runs on the same database. This will ensure that ranalyze runs are as atomic as possible to avoid any unexpected behavior.

These tests will all be run on the production environment once the final feature set is finalized, and any erros will be reproduced and investigated in development.
After completion of these system tests, the client will have an opportunity to set up and use a ranalyze deployment with the supervision of the developers, though without their assistance.
