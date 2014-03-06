# Gary documentation #

Gary is a python IRC bot.

## Introduction ##

### Goals ###

* simplicity
* little boilerplate
* minimal magic
* power
* multithreading
* automatic reloading
* extensibility

### Features ###

* multithreaded dispatch and the ability to connect to multiple networks at
  a time
  * easy plugin development with automatic reloading and a simple hooking API

  ### Requirements ###

  * Gary runs on Python 2.6 and 2.7. 
  * Many of the plugins require [lxml](http://lxml.de/).
  * Many plugins require BeautifulSoup4.
  * GVoice plugin requires pygooglevoice, I recommend [my fork](https://github.com/MikeRixWolfe/pygooglevoice).


  ## Table of contents ##

  * [[Installation]]
  * [[Configuration]]
  * [[Plugin development]]
