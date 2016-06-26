Changelog
=========

2.3.1 (2016-06-26)
------------------

- Add description to KPI pages [Chris Voll]

2.3.0 (2016-06-14)
------------------

- Ensure atomic experiment creation [Mark Williams]

2.2.0 (2016-03-24)
------------------

- Add StatsD support [Igor Bondarenko]


2.1.0 (2016-02-16)
------------------

- Fix restructured text issues in readme. [Jose Diaz-Gonzalez]

- Add release script. [Jose Diaz-Gonzalez]

- Add gunicorn and gevent. [Jose Diaz-Gonzalez]

  These don't need to be pegged to a specific version, and are confirmed working with gunicorn 17.5 through 19.4.1.

- Cast the environment variable to an integer. [Dan Alloway]

- Various improvements to README.rst. [John Bacon]

  Consistency improvements throughout the README.

- Bump version. [zackkitzmiller]

- Add a config value to disable csrf. [Thomas Meire]

- Allow traffic fraction to change in mid-flight. [nickveenhof]

- Fix readme heading for 2.0.1. [Jose Diaz-Gonzalez]

- Fix early bailout in existing_alternative for excluded clients. [Steve
  Webster]

  Also added an additional assert to the excluded client test that verifies excluded clients have no existing alternative even after a call to `Experiment.get_alternative`.


- [TRAFFIC] Fix over-recording. [zackkitzmiller]

- Remove round from choose alternative. [chaaaarlie]

  Rounding the random number generated at choose_alternative is excluding users who happen to get a random number greater or equal to 0.990000.

- Added unit tests. [Philipp Jardas]

  Redis database is now flushed after every test.


- Do not check traffic fraction for update on every participation.
  [Philipp Jardas]

  If a participation is requested without a traffic fraction argument, the traffic fraction is no longer assumed to be 1. This caused requests to always fail for experiments with a traffic fraction lower than 1 without explicit argument.

  Further, the server no longer defaults the request parameter "traffic_fraction" to 1 but simply leaves it at None. It's up to the model to default this value to 1 only when creating an new experiment.


- Catch ValueError during g_stat calculation. [Jose Diaz-Gonzalez]

  There can be cases where the conversions for a given alternative are zero, resulting in a math domain error when taking the log of the value.

- Discard conversions from excluded clients when traffic_fraction < 1.
  [Thomas Meire]

  When traffic_fraction is < 1, some clients get the control alternative.
  The participations of these excluded clients are not recorded to redis.
  When there is a conversion request for an excluded client, the conversion
  is not discarded and recorded to redis. When there are a couple of these
  conversions by excluded clients, the number of completed conversions
  becomes bigger than the number of participants, which should never be
  possible. The computation of the confidence_interval relies on this
  assumption and fails when the completed_count becomes bigger than
  participant_count.

  The solution is to discard the conversions of excluded clients as well.


- Fixing participating typo. [nickveenhof]

- Bump fakeredis version to v0.4.0 for bitcount implementation. [Thomas
  Meire]

- Display the number of clients that were excluded from the experiment.
  [Thomas Meire]

- Add sixpack-java to list of clients. [Stephen D'Amico]

2.0.3 (2015-07-15)
------------------

- Bump version. [zackkitzmiller]

- Port should be an integer. [Mark Steve Samson]

- Added redis max connections setting. [Maxim Kamenkov]

- [TESTS] add coverage badge. [zackkitzmiller]

- [TESTS] try to add coveralls. [zackkitzmiller]

- [TESTS] try to add coveralls. [zackkitzmiller]

- Revert "[TESTS] try to add coveralls" [zackkitzmiller]

  This reverts commit 7303d112ff906dbeb8664c982672d086370db3cf.


- [TESTS] try to add coveralls. [zackkitzmiller]

- [TESTS] try to add coveralls. [zackkitzmiller]

- Add coveralls. [zackkitzmiller]

2.0.2 (2014-11-17)
------------------

- Bump Version. [zackkitzmiller]

- [BUG] Fix broken experiments when winner is set. [zackkitzmiller]

- Added client. [Neil Derraugh]

- Remove logs. [Zachary Sherman]

- Santize names and fix charts. [Zachary Sherman]

- [WEB] uridecode experiment names. [Zachary Sherman]

- Remove log. [Zachary Sherman]

- Sanitize names. [Zachary Sherman]

- Add comment. [Zachary Sherman]

2.0.1 (2014-10-20)
------------------

- Bump version. [Zachary Sherman]

- Error handline, url encoding, and new failing test section. [Zachary
  Sherman]

- Make this version 2.0-dev. [Eric Waller]

- Change record_participation arg to prefetch. [Eric Waller]

- StrictRedis has no attribute 'pipe'. [Maxim Kamenkov]

- Fix 500 error on experiments.json API. [kadoppe]

- Display traffic fraction in UI. [Rick Saenz]

2.0.0 (2014-09-15)
------------------

- [DOCS] update. [zackkitzmiller]

- Remove all multi-armed bandit code. [zackkitzmiller]

  This was completely unnecessary, and overshadowed by the newer determinstic choice algorithm


- [TESTS] fix broken test, add test for failing traffic fraction.
  [zackkitzmiller]

- Do no allow traffic fractions to be changed after an experiment has
  started. [zackkitzmiller]

- Minor: save description on reset, closes #124. [zackkitzmiller]

- More tests for uniform choice. [zackkitzmiller]

- Add some comments on decisions made. [zackkitzmiller]

- Allow a no-record participation. [zackkitzmiller]

- Experiments endpoint. [zackkitzmiller]

- Kill unused code. [zackkitzmiller]

- Only use first 7 chars of UUID for deterministic algo.
  [zackkitzmiller]

- Slim objectified methods. [zackkitzmiller]

- Kill client_chosen_alternative concept. [zackkitzmiller]

- Predictive alt selection, refs #132. [zackkitzmiller]

- [WEB] fix broken test from previous commit. [zackkitzmiller]

- [WEB] correctly format legacy dates, closes #130. [zackkitzmiller]

- [DELETEING] KPIs do not use a color as a separator, closes #110.
  [zackkitzmiller]

- [UI] always show created at date. [zackkitzmiller]

  closes #121


- [WEB] kill asset compression, closes #115. [zackkitzmiller]

- Fix insecure content warnings with HTTPS. [Václav Slavík]

  Change the fonts.googleapis.com link in layout.html to be protocol-relative.

  This fixes insecure content warnings from modern browsers when running sixpack-web over HTTPS.

- Sixpack/test/seed: fix find_or_create arguments. [Naoki AINOYA]

- Closes #119. [Eric Waller]

  The tests around sixpack-web aren't quite as good..

- Bump version. [zackkitzmiller]

- [INSTALLATION] don't put things in __init__.py. [zackkitzmiller]

  This causes pip install to fail, as it imports sixpack before requirements are installed.


- Bump version. [zackkitzmiller]

- Fix parameter ordering. [zackkitzmiller]

- Closes #118. [Eric Waller]

- Start pulling out analysis code. [Eric Waller]

- Be consistent about using properties. [Eric Waller]

- Refactor core logic into api.py. [Eric Waller]

  This has a few benefits:

  * You can use sixpack within a python app with `sixpack.participate(...)`
  * It's a bit easier to test
  * It paves the way to add programmatically accessible analysis APIs which I'm thinking maybe a good way to address stuff like https://github.com/seatgeek/sixpack/pull/112

- Stop hiding the interesting data on mobile. [Eric Waller]

- Kill CSS file that was supposed to be removed in
  eb1233267cf93eff848f32cfaa517050ff0133e2. [Eric Waller]

1.1.2 (2014-05-20)
------------------

- Bump version. [zackkitzmiller]

- Allow clients to choose an alternative. [Eric Waller]

  Useful for situations where you may not know if a test will be encountered until it's too late to rely on asynchronously choosing an alternative.

  For example, when testing the behavior of a button, if `participate` is called when the button is setup, users that never click the button will dilute the results, thus requiring more participations to reach significance.

- Handle None values returned by HGET. [Osvaldo Mena]

- Add support to non-ascii characters on experiment description.
  [Osvaldo Mena]

- Throw error on casting float. [zackkitzmiller]

1.1.1 (2014-02-05)
------------------

- Bump version. [zackkitzmiller]

- Add newline at the end of config.py. [Osvaldo Mena]

- Add Support for Redis Sentinel. [Osvaldo Mena]

  Support for Redis Sentinel using redis.sentinel.SentinelConnectionPool. Can be configured either by specifiying the env vars SIXPACK_CONFIG_REDIS_SENTINEL_SERVICE_NAME and SIXPACK_CONFIG_REDIS_SENTINELS, or by specifying redis_sentinel_service_name and redis_sentinels on config.yml


- Bump version. [zackkitzmiller]

1.1.0 (2014-01-20)
------------------

- [DOCS] add CHANGES.rst. [zackkitzmiller]

- [WEB] export should respect kpi. [zackkitzmiller]

- Document multi-armed bandit. [zackkitzmiller]

  Closes #89


- Revisit traffic distribution/fraction. [zackkitzmiller]

  closes #99


- Add ZeroDivisionError exception to avoid fatal error on calculating
  g_stat. [hsinhoyeh]

- Support settings via env variables. [zackkitzmiller]

  closes #98


- Type convertions from enviroment strings. [Otoniel Plahcinski]

- Fix testing to have no default config file. [Otoniel Plahcinski]

- Concept Code. [Otoniel Plahcinski]

- Document multi-armed bandit. [zackkitzmiller]

  Closes #89


- Link iOS client. [Jose Diaz-Gonzalez]

- Added sixpack client library for iOS. [Jose Diaz-Gonzalez]

- Added a Perl client package. [B10m]

1.0.5 (2013-10-16)
------------------

- Merge remote-tracking branch 'origin/master' [zackkitzmiller]

- Fix typo in README. [Bob Nadler]

- Bump version. [zackkitzmiller]

- Allow KPI conversion after non-KPI conversion. [zackkitzmiller]

  closes seatgeek/sixpack#95


1.0.4 (2013-09-12)
------------------

- Bump version. [zackkitzmiller]

- Manifest: Fix missing setup.py. [Philip Cristiano]

  The setup.py isn't in the package and wasn't being included

- Find_or_404 should only catch ValueError. [Dan Horrigan]

  By catching all errors it makes it very hard to debug.  For example, if
  the Redis service craps out in the middle of the request, a 404 will be
  returned instead of a 500, which means the exception will be silently
  ignored, and not being logged correctly.


- Typo. [Alif Rachmawadi]

- Add sixpack-go. [Alif Rachmawadi]

- Fixing the ASCII art.  Very Important of course. [Dan Horrigan]

- Removing uneeded markdown() call. [Dan Horrigan]

- Simplifying the debug check. [Dan Horrigan]

1.0.1 (2013-08-29)
------------------

- Bump version. [zackkitzmiller]

- Move third party js and css libraries to vendor folder.
  [zackkitzmiller]

  this should change the github language statistics


1.0.0 (2013-08-29)
------------------

- Bump version. [zackkitzmiller]

- Change error message. [zackkitzmiller]

- Add ability to turn off debug mode and add necessary notes to readme.
  [zackkitzmiller]

- All responses should be json. [zackkitzmiller]

- Dont throw a backtrace on start if Redis is not available.
  [zackkitzmiller]

- Add note about removing experiment code. [zackkitzmiller]

- Make confusing documentation more clear. [zackkitzmiller]

- Disable MAB by default. [zackkitzmiller]

- Less confusing behavior when there are no experiments.
  [zackkitzmiller]

- Kill unnecessary comment. [zackkitzmiller]

- Rename style.css to sixpack.css to be consistent with javascript
  files. [zackkitzmiller]

- Trivial language tweak. [Jack Groetzinger]

- Add 's' to experiment/ urls. [zackkitzmiller]

- Tests for multiple KPIs, fix bugs found with tests, refs #30.
  [zackkitzmiller]

- Invalid KPIs should throw exceptions on /convert on the server.
  [zackkitzmiller]

- Alternative names, experiments, and KPIs cannot have spaces.
  [zackkitzmiller]

- Exclude webassets cache. [zackkitzmiller]

- Fix for undefined js bug. [zackkitzmiller]

- Redirect when KPI is selected, refs #30. [zackkitzmiller]

- Auto select correct KPI on dropdown. [zackkitzmiller]

- Add current kpi to .json responses. [zackkitzmiller]

- Pass KPI value through javascript back to server, refs #30.
  [zackkitzmiller]

- Initial implementation of multiple KPIs in sixpack-web, refs #30.
  [zackkitzmiller]

- Hookup multiple KPI conversion to /convert action in server, refs #30.
  [zackkitzmiller]

- Add handling in models to allow for multiple KPIs, refs #30.
  [zackkitzmiller]

- Fix broken dashboard, expects list of names. [zackkitzmiller]

- No longer load in archived experiments and hide them with javascript.
  [zackkitzmiller]

- Add _status endpoint to sixpack-web closes #77. [zackkitzmiller]

- Refactor response handling, refs #77. [zackkitzmiller]

- Actually fix showing archived experiments on dashboard.
  [zackkitzmiller]

- Fix. [zackkitzmiller]

- Do not load archived experiments then hide them on the dashboard,
  closes #72. [zackkitzmiller]

- Do not load archived experiments then hide them on the dashboard,
  closes #72. [zackkitzmiller]

- Fixed another confidence interval bug. [Chris Voll]

- Some improvements to welcome page. [Chris Voll]

- Better bug fix. [Chris Voll]

- Fixed confidence interval boxplot bug for large datasets, new welcome
  screen. [Chris Voll]

- RST is not MD. [zackkitzmiller]

- Add note about hiredis install errors, thanks @taylorotwell.
  [zackkitzmiller]

- Bump version. [zackkitzmiller]

- Select traffic distribution for experiments, closes #29.
  [zackkitzmiller]

- Change order of imports. [zackkitzmiller]

- Adjust keyspace to allow for excluded clients, refs #29.
  [zackkitzmiller]

- Implemented confidence interval boxplots. [Chris Voll]

- Reduced confidence interval to one decimal. [Chris Voll]

- Added 80% confidence intervals, some other minor enhancements. [Chris
  Voll]

- Navigation UI improvements. [Chris Voll]

- Retina logo. [Chris Voll]

- Responsive description modal. [Chris Voll]

- Better responsiveness for chart dots on details page, better narrow
  width. [Chris Voll]

- Dashboard charts are now responsive. [Chris Voll]

- Fixed long variation name alignment, fixes #56. [Chris Voll]

- Not sure how that stray = got in there. [Chris Voll]

- Details page icons. [Chris Voll]

- Removed focus hackery. [Chris Voll]

- Final cleanup. [Chris Voll]

- Added zeroclipboard to details pages to copy querystrings. [Chris
  Voll]

- Adjusted table position. Unfortunately, negative right margin wasn't
  working, so the fix just removed the negative margins altogether.
  [Chris Voll]

- Added responsive charts to details pages. [Chris Voll]

- Added dot color to tooltip. [Chris Voll]

- Removed leading zeros, ref #52. [Chris Voll]

- Smaller dots for lots of data. [Chris Voll]

- Fixed earlier bug, moved a couple styles around. [Chris Voll]

- Final tooltip touches. [Chris Voll]

- Added tooltips. [Chris Voll]

- Initial dots implementation, no tooltip yet. [Chris Voll]

- UI updates, responsiveness, created better workarounds for a Chrome
  bug, new colors, updated nav. [Chris Voll]

- Fix json template for dashboard. [zackkitzmiller]

- Remove artificial limitation on markdown implementation, refs #61 and
  #64. [zackkitzmiller]

- Allow paragraph tags with markdown. [zackkitzmiller]

- Check that description exists before trying to parse with markdown,
  refs #64. [zackkitzmiller]

- Add limited markdown support to descriptions, closes #64.
  [zackkitzmiller]

- Initial markdown implementation for experiment descriptions, refs #64.
  [zackkitzmiller]

- Remove unnecessary comment. [zackkitzmiller]

- Add experiments.json endpoint. [zackkitzmiller]

- Add method to retrieve only archived experiments. [zackkitzmiller]

- Fix merge conflict. [zackkitzmiller]

- Resolve merge conflict. [zackkitzmiller]

- Fix merge conflict. [zackkitzmiller]

- Bump version. [zackkitzmiller]

- Remove the entire concept of 'versions' from sixpack. [zackkitzmiller]

- Modify keyspace to remove concept of experiment "versions"
  [zackkitzmiller]

- Bump version. [zackkitzmiller]

- Rename script.js to sixpack.js. [zackkitzmiller]

- More sahne archive UI, closes #51. [zackkitzmiller]

- Kill unnecessary comment. [zackkitzmiller]

- Bump version. [zackkitzmiller]

- Add experiment to export filename download. [zackkitzmiller]

- Bump version. [zackkitzmiller]

- Add ability to export experiment details to csv. [zackkitzmiller]

- Whitespace. [zackkitzmiller]

- Fix potentially devastating bug related to deleted experiments.
  [zackkitzmiller]

- Add .vfenv to .gitignore. [zackkitzmiller]

- Fix broken graphs on versioned experiments. [zackkitzmiller]

- Remove unused var. [zackkitzmiller]

- Pep8. [zackkitzmiller]

- Better idea: everything uses 'test statistic' nomenclature, agnostic
  to specific test stat used. [Steve Ritter]

- Details uses g_stat. [Steve Ritter]

- Dashboard uses g_stat. [Steve Ritter]

- Changed objectify to use g_stat. [Steve Ritter]

- Formatting. [Steve Ritter]

- Added g test for confidence level to replace hacky undocumented z
  score. [Steve Ritter]

- Fixes #53 - details page graph alignment and size. [Matthew Hudson]

- Fixing close button styling - closes #54. [Matthew Hudson]

- Remove unused allow_multiple_experiments option. [Eric Waller]

- Remove unused control_on_db_failure option. [Eric Waller]

- Remove unused full_response option. [Eric Waller]

- Fix robot detection (with tests) [Eric Waller]

- Sort chart lines so the active line is "above" the non-hovered lines.
  [Matthew Hudson]

- Removing chart tooltip. [Matthew Hudson]

- Adding support for chart/circle highlighting. [Matthew Hudson]

- Adjusting table-line highlighting behavior. [Matthew Hudson]

- Enabling chart hover states based on table interaction. [Matthew
  Hudson]

- Adding some helpful comments. [Matthew Hudson]

- Fixing experiment alternative highlighting. [Matthew Hudson]

- Adding hover state to chart lines. [Matthew Hudson]

- Basic build out for enabling chart hover state. [Matthew Hudson]

- Dont use == to compare with False. [zackkitzmiller]

- Fixing x-axis chart bug. [Matthew Hudson]

- Fixing details page header styling. [Matthew Hudson]

- Fixing update description default value. [Matthew Hudson]

- Details page experiment name doesn't need to be a link. [Matthew
  Hudson]

- 'Update Description' button should allow you to update an existing
  description. [Matthew Hudson]

  Closes #45

- Make MAB not the default and change the config option for it. [Jose
  Diaz-Gonzalez]

- Adjusting dashboard page chart positioning. [Matthew Hudson]

- Optimixing x-axis tick spacing. [Matthew Hudson]

- Adding x-axis labels to charts. [Matthew Hudson]

- Fix duplicate conversions in by-period data. [Eric Waller]

- Test for the by-period conversion data. [Eric Waller]

- Fix experiment version caching. [Eric Waller]

- Kill unused property. [Eric Waller]

- Cache sequential ids again. [Eric Waller]

- Sequential ids are stored per experiment. [Eric Waller]

  This will prevent memory usage from growing uncontrollably for conversion/participations keys. It also means that memory can be fully reclaimed when experiments are deleted.

- Whitespace. [Eric Waller]

- Rename get_alternative_by_client_id. [Eric Waller]

- Control is a property. [Eric Waller]

- Kill unused collection models. [Eric Waller]

- Whitespace. [Eric Waller]

- Fix _get_stats. [Eric Waller]

- Test conversion. [Eric Waller]

- Shorten key names to conform w/ updated CLIENTSPEC. [Eric Waller]

- Lua implementation of get_alternative_by_client_id. [Eric Waller]

  and delete the unused has_converted_by_client_id

- Use a shorter default prefix. [Eric Waller]

- Fixes a bug that causes the spinner to load infinitely. [Matthew
  Hudson]

- Add a quick benchmark script. [Eric Waller]

  This could be extended a good deal. The main thing I want to add is the ability to generate data for a couple of days at a time.

  Note, it uses a modified version of the client with the module name changed to sixpack_client, b/c otherwise it conflicts with the server module.


- Reduce redis queries for participate from 13 to 7. [Eric Waller]

  (6 to 3 for bots)


- Duplicate conversions aren't exceptional. [Eric Waller]

- Experiment.winner is now a cached property. [Eric Waller]

- Re-order alternative choosing precedence. [Eric Waller]

  New precedence ordering:
  * The force param
  * If the server is not enabled, the control is returned
  * If there's a winner, it's returned
  * If the visitor is excluded, return the control
  * Otherwise create an internal client_id and return a "chosen" alternative

  This ensures the following:
  * Bots do not cause internal client_ids to be created
  * Bots *do* get the winner if one exists
  * The force param *always* works
  * Redis work is minimized

  Note: I added code to delete all sixpack related keys before starting the tests. I don't *think* there's anything wrong with that, but I figured I'd call it out.

- Fix bug with returning the winner. [Eric Waller]

- Remove extra Experiment.find. [Eric Waller]

- Added default background-color to prevent FOUC. [Matthew Hudson]

- Remove duplicative conversion rate with bad formatting.
  [zackkitzmiller]

  During a merge conflict, the proper formatting of the conversion rate was removed from the .json experiment endpoints.


- Commas. [zackkitzmiller]

- Revert super agressive preloading. [zackkitzmiller]

- Build out ajax templates for charts and dashboards. [Matthew Hudson]

- Better response for conversion rate in json endpoint. [zackkitzmiller]

- More info on alternative .json endpoint. [zackkitzmiller]

- More comprehensive .json endpoint. [zackkitzmiller]

- Merged master. [Matthew Hudson]

- Compress, do not just concatconcatenate assets. [zackkitzmiller]

- Compress, do not just concatenate assets. [zackkitzmiller]

- Better formatting. [zackkitzmiller]

- Fade-in Dashboard charts on-scroll. [Matthew Hudson]

- Load Dashboard charts on scroll. [Matthew Hudson]

- Added $.waypoints plugin. [Matthew Hudson]

- Don't include boostrap.js twice. [zackkitzmiller]

- Add .webassets-cache to gitignore. [Eric Waller]

- Allow datetime to be specified by clients. [Eric Waller]

- Higher-resolution data in charts. [Matthew Hudson]

- Removed legacy JS. [Matthew Hudson]

- Transitioned selector language to use chart instead of graph. [Matthew
  Hudson]

- Removed legacy code. [Matthew Hudson]

- Dashboard graphs are now cumulative. [Matthew Hudson]

- Revert "Revert "bump version"" [zackkitzmiller]

  This reverts commit c6121a5a45057625ebf9880f3a49e71c8595c9b3.


- Revert "maybe this" [zackkitzmiller]

  This reverts commit b7cbd1a384627b63b9d4b9a98a248eacb62fa58c.


- Revert "bump version" [zackkitzmiller]

  This reverts commit 100ed05fe390588a9da646de86af90e6491b623b.


- Maybe this. [zackkitzmiller]

- Bump version. [zackkitzmiller]

- Märk control alt as such. [zackkitzmiller]

- Change default host to 0.0.0.0 for dev mode. [zackkitzmiller]

- Add .json endpoints to sixpack-web for experiments. [zackkitzmiller]

- Move error templates, add 500 error page. [zackkitzmiller]

- Added asset_path to readme. [zackkitzmiller]

- 404 page. [zackkitzmiller]

- Line break. [zackkitzmiller]

- Kill debug. [zackkitzmiller]

- Configurable asset path. [zackkitzmiller]

- Add empty folder. [zackkitzmiller]

- Readme: Fix numbering of steps. [Philip Cristiano]

- Readme: Fix seed example command. [Philip Cristiano]

  The command requires a PYTHONPATH in order to find the models. Also
  since this is in the development section it should follow the pattern
  of the other example commands which include the local config.yml
  instead of instruction to replace with the path to the config file.


- Enable debug. [zackkitzmiller]

- Fix git whoops. [zackkitzmiller]

- Revert "Merge branch 'compress-assets'" [zackkitzmiller]

  This reverts commit 5cd51272ef6e505e35626e1e144976a22c05af88, reversing
  changes made to 40e784c3140992ab9040f550a1a553cd7185146d.


- More css. [zackkitzmiller]

- Remove unnecessary css. [zackkitzmiller]

- Bundle the css. [zackkitzmiller]

- First go at compressing all assets, refs #20. [zackkitzmiller]

- This list should actually be reversed. [zackkitzmiller]

- Attempt to find a matching variation of a experiment if it exists.
  [zackkitzmiller]

  This will avoid the issue of dozens of tests being created when switching back and forth between two sets are alternatives for the same experiment.


- Bump version. [zackkitzmiller]

- Allow to view old version results. [zackkitzmiller]

- Enable/disable six-pack server level, closes #33. [zackkitzmiller]

- Faster dashboard, use redis pipelining when possible. [zackkitzmiller]

- Fixed graphs. [Matthew Hudson]

- Turned off the archive toolbar when there isn't any experiment data.
  [Matthew Hudson]

- Fix broken test, whoops. [zackkitzmiller]

- Fixed template bug that reversed the position of name and description.
  [Matthew Hudson]

- Better description handling. [zackkitzmiller]

- Better description handling. [zackkitzmiller]

- Remove unnecessary whitespace. [zackkitzmiller]

- Fixed archive notice button padding. [Matthew Hudson]

- Much better seeding, closes #31. [zackkitzmiller]

- Changed words. [zackkitzmiller]

- Improved UI styling for archive included/excluded notice. [Matthew
  Hudson]

- Switch for including archived experiments. [zackkitzmiller]

- Version bump. [zackkitzmiller]

- Seed instructions are more clear. [zackkitzmiller]

- Change link reference. [Jack Groetzinger]

- Changing to BSD 2-Clause license. [Jack Groetzinger]

- Typo fix. [Jack Groetzinger]

- Add Google Group. [Jack Groetzinger]

- Use proper legal name for SG. [Jack Groetzinger]

- Markdown > RST. [Jack Groetzinger]

- Why the hell are we not using markdown. [Jack Groetzinger]

- Fix license link. [Jack Groetzinger]

- Mention license in README. [Jack Groetzinger]

- Added path to bin scripts. [zackkitzmiller]

- Improved y-axis for dashboard graphs. [Matthew Hudson]

- Refactored drawing of multiple lines for dashboard graph. [Matthew
  Hudson]

- Added support for unique line colors on graphs. [Matthew Hudson]

- Implemented multiple lines on dashboard page graphs. [Matthew Hudson]

- Hide graphs without at least 2 intervals of data. [Matthew Hudson]

- Fixed identation. [Matthew Hudson]

- Added NaN check to prevent division-by-zero bug. [Matthew Hudson]

- Refactored JS graphing code. [Matthew Hudson]

- Addresses #26. [Matthew Hudson]

- Fixing typo. [Jack Groetzinger]

- Minor language change. [Jack Groetzinger]

- More readme cleanup. [Jack Groetzinger]

- Add CLIENTSPEC link. [Jack Groetzinger]

- Why aren't we using markdown? [Jack Groetzinger]

- Fixing awkward readme language. [Jack Groetzinger]

- Require that server location be configurable. [Eric Waller]

- Relax sentence about idiomatic client extensions. [Eric Waller]

- More detailed client spec. [Eric Waller]

- Further performance enhancements. [zackkitzmiller]

- Better no graph message on details page. [Matthew Hudson]

- Better no graph message. [Jack Groetzinger]

- Fixed multi-line display of graphs on dashboard pages. [Matthew
  Hudson]

- Bump version. [zackkitzmiller]

- Some caching to resolve performance issues. [zackkitzmiller]

- Fixed dashboard styling of 'Not enough data..' message. [Matthew
  Hudson]

- Add favicon. [Jack Groetzinger]

- Add requests to requirements. [zackkitzmiller]

- Hide charts if there is less than two days of data. [Matthew Hudson]

- Removed console.log() calls. [Matthew Hudson]

- Removed superfluous percentage sign. [Matthew Hudson]

- Closes #19. [Jack Groetzinger]

- Charts complete. [Matthew Hudson]

- Adjusted format for printing graph data in template. [Matthew Hudson]

- Javascript-encoded graph data for details page. [Matthew Hudson]

- Fixed base url when there are no experiments (closes #8). [Matthew
  Hudson]

- Added confirm reset modal. [Matthew Hudson]

- Added confirm delete modal. [Matthew Hudson]

- Added a little bottom padding to ensure tables never end flush with
  their parent container. [Matthew Hudson]

- Bottom align charts on details page. [Matthew Hudson]

- Match control and winner indicators on dashboard to details page.
  [Matthew Hudson]

- Basic layout for a chart on details page, changed winner language.
  [Matthew Hudson]

- Added mininum height to experiment header to ensure bottom spacing
  when description doesn't exist. [Matthew Hudson]

- Fixed positioning of description in relation to the buttons. [Matthew
  Hudson]

- Fixed table layout on details page. [Matthew Hudson]

- Removed unnecessary console.log() [Matthew Hudson]

- Better responsive handling for header buttons. [Matthew Hudson]

- Wrapped chart code in a function to enable drawing for each
  experiment. Better usage of space for chart on dashbaord. [Matthew
  Hudson]

- Fixed responsive bug on dashboard. [Matthew Hudson]

- Dashboard is fully responsive. [Matthew Hudson]

- Groundwork for homepage responsiveness. [Matthew Hudson]

- Converted indentation style to use spaces. [Matthew Hudson]

- Fixed responsive ui bugs in the navbar. [Matthew Hudson]

- Minor tweaks to typography. [Matthew Hudson]

- Further buildout and styling of lightbox and buttons. [Matthew Hudson]

- Initial mockup of details page. [Matthew Hudson]

- Fixed typos in README. [Russell DSouza]

- Language improvements to CLIENTSPEC. [Jack Groetzinger]

- Bump version. [zackkitzmiller]

- Uniform decimal places, closes #7. [zackkitzmiller]

- Added seed information to readme, closes #13. [zackkitzmiller]

- There we go. [zackkitzmiller]

- I just can't seem to use rst. [zackkitzmiller]

- I just can't seem to use rst. [zackkitzmiller]

- Additional specs for clients. [zackkitzmiller]

- Fixed broken rst. [Jose Diaz-Gonzalez]

- First pass at client spec. [zackkitzmiller]

- Reverted z-score to cube approximation. [Steve Ritter]

- Expose sixpack version from status endpoint. [zackkitzmiller]

- Readme. [zackkitzmiller]

- Bump version. [zackkitzmiller]

- Breaking: change/standardize responses. [zackkitzmiller]

- Minor: cleanup some redundant code. [zackkitzmiller]

- Add conversions/participations per day to alternative model.
  [zackkitzmiller]

- More docs. [zackkitzmiller]

- Docs. [zackkitzmiller]

- Add conversions/participations per day to experiment model.
  [zackkitzmiller]

- Make whiplash configurable. [zackkitzmiller]

- Bump version. [zackkitzmiller]

- README: Fix instructions on how to run locally. [Philip Cristiano]

  Running ./bin/sixpack-web will set the PYTHONPATH to ./bin/
  which does not have the Sixpack code available.


- Initial documention work. [zackkitzmiller]

- Pep8. [zackkitzmiller]

- More cleanup/tests. [zackkitzmiller]

- Clean up some of the error/response handling, refs #2.
  [zackkitzmiller]

- No longer using z_score from split-rb. [zackkitzmiller]

- Fixed incorrect web reference. [Jose Diaz-Gonzalez]

- Switched standard deviation calc to something I understand. [Steve
  Ritter]

- Fixed confidence intervals. [Steve Ritter]

- Minor show experiments view, closes #6. [zackkitzmiller]

- Comma-ify number in dashboard, closes #5. [zackkitzmiller]

- CSS cleanup. [Jack Groetzinger]

- Move seed.py to bin/sixpack-seed. [Jose Diaz-Gonzalez]

- More minor CSS tuning. [Jack Groetzinger]

- Evening out bad column. [Jack Groetzinger]

- Turning down opacity. [Jack Groetzinger]

- Fine tuning Chrome CSS3 workaround. [Jack Groetzinger]

- Tweaking the Chrome bug workaround. [Jack Groetzinger]

- Working around Chrome CSS table bug. [Jack Groetzinger]

- Bump version. [zackkitzmiller]

- Minor fixes and tweaks. [zackkitzmiller]

- Fixed confidence intervals. [Steve Ritter]

- Switched standard deviation to something I understand for now. [Steve
  Ritter]

- Disable whiplash. [zackkitzmiller]

- Include package data. [Jose Diaz-Gonzalez]

- Added missing * to package manifest. [Jose Diaz-Gonzalez]

- Added missing templates dir to MANIFEST.in. [Jose Diaz-Gonzalez]

- Potential preliminary graph style. [Jack Groetzinger]

- Working ugly d3 graph. [Jack Groetzinger]

- Added color dots.  Table tweaks.  Beginning with d3. [Jack
  Groetzinger]

- Table design. [Jack Groetzinger]

- Minor UI cleanup. [Jack Groetzinger]

- Fix tests related to changing response. [zackkitzmiller]

- Better error message. [zackkitzmiller]

- Response should be consistent when excluding a visitor.
  [zackkitzmiller]

- More error handling. [zackkitzmiller]

- Error responses should be more consistant. [zackkitzmiller]

- Case. [zackkitzmiller]

- Move sixpack-web app secret key into config. [zackkitzmiller]

- Only need REDIS from db. [zackkitzmiller]

- Imports in proper order. [zackkitzmiller]

- Don't do this. [zackkitzmiller]

- Use ValueError instead of generic exceptions where appropriate, fix
  appropriate tests. [zackkitzmiller]

- Return None not False when winner doesn't exist. [zackkitzmiller]

- Less yoda. [zackkitzmiller]

- Correct order of imports. [zackkitzmiller]

- Config should be a relative import. [zackkitzmiller]

- Empty string will persist on object. [zackkitzmiller]

- Pep8. [zackkitzmiller]

- Cleaned up decorator a little bit. [zackkitzmiller]

- Pep8. [zackkitzmiller]

- Call test before converting. [zackkitzmiller]

- Inject sample size (or something) for testing. [zackkitzmiller]

- Many many more tests, models are pretty well tested, as well as the
  server with integration tests. [zackkitzmiller]

- Start redis in travis. [zackkitzmiller]

- Trying something. [zackkitzmiller]

- Jsonp support. [Mike Dirolf]

- Context-Type -> Content-Type. [Mike Dirolf]

- Tests that don't pass yet. [Mike Dirolf]

- Basic structure for testing server interaction. [Mike Dirolf]

- Lots a more tests. [zackkitzmiller]

- More tests. [zackkitzmiller]

- Add fakeredis to requirements.txt. [zackkitzmiller]

- Replace magic mock with fakeredis, fix tests, add new ones.
  [zackkitzmiller]

- Add status to response. [zackkitzmiller]

- Minor: small script to load data and convert. [zackkitzmiller]

- Pep8. [zackkitzmiller]

  There are several lines that are too long still. I'm fine with that.


- Make fairness score more obvious. [zackkitzmiller]

- Minor: remove debug. [zackkitzmiller]

- My probably poor attempt at implementing one armed bandit/whiplast
  alto. [zackkitzmiller]

- Fix floating point math. [zackkitzmiller]

- More pythonic division by zero checking, reduces redis calls.
  [zackkitzmiller]

- Z_score in title, needs work/help. [zackkitzmiller]

- Implement basic conversion rate. [zackkitzmiller]

- Fix incorrect completion count returned from
  alternative#completion_count. [zackkitzmiller]

- Minor: logic comment. [zackkitzmiller]

- Return control on archived experiment. [zackkitzmiller]

- Hook up archive logic. [zackkitzmiller]

- Hookup some info on the dashboard. [zackkitzmiller]

  also implement conversion_rate


- Implement alternative#is_control. [zackkitzmiller]

- Implement archive and update description. [zackkitzmiller]

- Implement archiving. [zackkitzmiller]

- Implement reset and delete. [zackkitzmiller]

- Implement Experiment#reset. [zackkitzmiller]

- Flask should be 0.9. [Eric Waller]

- Set/reset experiment winners. [zackkitzmiller]

- Minor clean up. [zackkitzmiller]

- Add secret key. [zackkitzmiller]

- Implement alternative is_winner. [zackkitzmiller]

- Csrf protection. [zackkitzmiller]

- Basic table layout. Still a long way to go. [Jack Groetzinger]

- I dont know how to readme. [Zack Kitzmiller]

- Very basic readme updates. [zackkitzmiller]

- Seed some data for testing. [zackkitzmiller]

- Fix broken tests. [zackkitzmiller]

- Spw work. [zackkitzmiller]

- Removed alternative reset method in favor of version incrementing.
  [zackkitzmiller]

- Code clean up. [zackkitzmiller]

- Fix incorrect version handling. [zackkitzmiller]

- Minor fixes from refactor and tests. [zackkitzmiller]

- Temp: commented out tests that I'm un sure were testing anything
  relevent. [zackkitzmiller]

- Work around script reloading bug in redis-py. [Eric Waller]

- Use decorator for status endpoint as well. [Eric Waller]

- Decorator to handle redis going away, as per #2. [Eric Waller]

- Conform model classes to respect KEYSPACES. [zackkitzmiller]

- Experiment details in sixpack-web. [zackkitzmiller]

- Display some keys. [zackkitzmiller]

- Hookup twitter bootstrap, render home view. [zackkitzmiller]

- Moving things around. [zackkitzmiller]

- Minor work on sixpack-web. [zackkitzmiller]

- Empty templates and static files. [zackkitzmiller]

- Stubbing out sixpack web controllers. [zackkitzmiller]

- Sorta stub for alternative collection. [zackkitzmiller]

- Check for valid ip address. [zackkitzmiller]

- Test is_robot. [zackkitzmiller]

- Change default redis db to 0. [zackkitzmiller]

- Whitespace. [zackkitzmiller]

- Cleanup. [zackkitzmiller]

- Server side robot/ip detection. [zackkitzmiller]

- Format config.yml. [zackkitzmiller]

- Note on KEYSPACE. [zackkitzmiller]

- More configuration options. [zackkitzmiller]

- Lazily call redis. [zackkitzmiller]

- Hookup and test new valid name regex. [zackkitzmiller]

- Add sum keys for conversions to keyspace spec. [Eric Waller]

- Add a winner key to the keyspace spec. [Eric Waller]

- Documentation on how I think we should layout the keyspace. [Eric
  Waller]

- Alternative/experiment name validation regex. [Eric Waller]

- Sequential_id should be internal to models.py. [Eric Waller]

- Minor. [zackkitzmiller]

- Non-trivial readme cleanup. [Jose Diaz-Gonzalez]

- Add necessary requirements. [zackkitzmiller]

- Add new line to file. [zackkitzmiller]

- Load config from yml. [zackkitzmiller]

- Server:start for gunicorn. [zackkitzmiller]

- Hrm. [zackkitzmiller]

- Fixes. [zackkitzmiller]

- Better json responses. [zackkitzmiller]

- Cleaning up server.py. [zackkitzmiller]

- Text -> dales. [zackkitzmiller]

- Readme: heading. [zackkitzmiller]

- Removed unnecessary comment. [zackkitzmiller]

- Moved client logic out of controller for now. [zackkitzmiller]

- Server.py is born. [zackkitzmiller]

- No more scratch.py. [zackkitzmiller]

- Better exceptions, ignore favicon. [zackkitzmiller]

- Status/healthcheck endpoint. [zackkitzmiller]

- Show version in resp for debug. [zackkitzmiller]

- Merged in jacks readme. [zackkitzmiller]

- Trivial readme cleanup. [Jack Groetzinger]

- Fixed a type, not sure why. [zackkitzmiller]

- Broke a method. [zackkitzmiller]

- Delete all participation keys on version change. [zackkitzmiller]

- Initial work on versioning. [zackkitzmiller]

- Fixes. [zackkitzmiller]

- Moving more stuff around. [zackkitzmiller]

- Formatting. [zackkitzmiller]

- Remove unnecessary import. [zackkitzmiller]

- Check participation before conversion. [zackkitzmiller]

- Use setbit/getbit/bitcount instead of a hash. fix related tests.
  [zackkitzmiller]

- Minor refactoring. [zackkitzmiller]

- Move record_participation into alternative model. [zackkitzmiller]

- More tests. [zackkitzmiller]

- Tests: more. [zackkitzmiller]

- Typo. [zackkitzmiller]

- Try this. [zackkitzmiller]

- Travis-ci. [zackkitzmiller]

- Tests: experiment model test stub. [zackkitzmiller]

- More DI. [zackkitzmiller]

- Tests: alternative model tests. [zackkitzmiller]

- Injecting redis dependency. [zackkitzmiller]

- Requirements: update. [zackkitzmiller]

- Remove troll unused mock_redis. [zackkitzmiller]

- Tests: more test stubs. [zackkitzmiller]

- Initial version of mockredis. [zackkitzmiller]

- Test stub, reorg project. [zackkitzmiller]

- Scratch: call experiment.convert on 'on_convert' [zackkitzmiller]

- Minor refactor, stub convert, implement Experiment.all()
  [zackkitzmiller]

- Scratch: convert endpoint. [zackkitzmiller]

- Implement Experiment.find. [zackkitzmiller]

- More work. client_ids are now properly respected. [zackkitzmiller]

- Some work on sixpack, mostly scratch and model stubs. working
  werkzeug. [zackkitzmiller]

- Started playing around with some redis scripts. [Eric Waller]

- Well that's pretty much done. [Eric Waller]

- First commit. [Eric Waller]
