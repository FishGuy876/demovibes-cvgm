Overview
========

Some tests using Selenium (http://seleniumhq.org/) 
for automated browser testing.

Selenium is a system for automated testing of web apps via scripted 
browser events. As a result, it needs to be run on a computer with
a graphical environment, and browser(s) installed.

It also needs external access to a webserver running the code to be tested.

Selenium
========

To run these tests, you need Selenium installed. There's two options:

 1. Firefox IDE - Perfect for making tests and non-automated testing
 2. Remote Server - Can run many different browsers, works as a daemon 
    that other hosts can connect and run tests via.
    
Start testserver
================

Command : python manage.py testserver --addrport=0.0.0.0:9877 selenium_testdata --settings settings_test

 selenium_testdata.json contains the test data to be inserted into the DB.
 settings_test.py contains some changes to the settings, to facilitate testing.
                 (Currently it turns of caching, ajax refresh, and removes south from installed_apps)

TestCases / TestSuite
=====================

It's highly recommended to load the test suite ("FuncTests.ts") and run the
testcases in the order given there. Some of the tests relies on steps done by
previous tests (most notably the "login" test).

If some of the tests fail, try running them at slower speeds. Especially the
background AJAX submits might be aborted too early.
