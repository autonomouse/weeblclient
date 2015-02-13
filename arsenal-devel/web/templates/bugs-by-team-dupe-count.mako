<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<%
    importance_color = {
            "Unknown"       : "importance-unknown",
            "Critical"      : "importance-critical",
            "High"          : "importance-high",
            "Medium"        : "importance-medium",
            "Low"           : "importance-low",
            "Wishlist"      : "importance-wishlist",
            "Undecided"     : "importance-undecided"
        }
    status_color     = {
            "New"           : "status-new",
            "Incomplete"    : "status-incomplete",
            "Confirmed"     : "status-confirmed",
            "Triaged"       : "status-triaged",
            "In Progress"   : "status-in_progress",
            "Fix Committed" : "status-fix_committed",
            "Fix Released"  : "status-fix_released",
            "Invalid"       : "status-invalid",
            "Won't Fix"     : "status-wont_fix",
            "Opinion"       : "status-opinion",
            "Expired"       : "status-expired",
            "Unknown"       : "status-unknown"
        }

    bugs_by_team = {}
    tasks = template_data['tasks']
    for bid in tasks:
        for t in tasks[bid]:
            team = 'unknown' if t['team'] == '' else t['team']

            if team not in bugs_by_team:
                bugs_by_team[team] = {}

            if bid not in bugs_by_team[team]:
                bugs_by_team[team][bid] = []

            if t['bug_target_name'] not in bugs_by_team[team][bid]:
                bugs_by_team[team][bid].append(t['bug_target_name'])

    team_report_order = []
    if 'unknown' in bugs_by_team:
        team_report_order.append('unknown') # We want unknown first
    for t in sorted(bugs_by_team):
        if t != 'unknown':
            team_report_order.append(t)

    report_options = template_data['report']
%>
<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>${report_title}</title>

        <link title="light" rel="stylesheet" href="http://people.canonical.com/~kernel/reports/css/light-style.css" type="text/css" media="print, projection, screen" />
        <link title="dark"  rel="stylesheet" href="http://people.canonical.com/~kernel/reports/css/dark-style.css"  type="text/css" media="print, projection, screen" />

        <script type="text/javascript" src="http://people.canonical.com/~kernel/reports/js/styleswitcher.js"></script>

        <link href='http://fonts.googleapis.com/css?family=Cantarell&subset=latin' rel='stylesheet' type='text/css'>
        <script type="text/javascript" src="http://people.canonical.com/~kernel/reports/js/jquery-latest.js"></script>
        <script type="text/javascript" src="http://people.canonical.com/~kernel/reports/js/jquery.tablesorter.js"></script>

    </head>


    <body class="bugbody">
        <!-- Top Panel -->
        <div id="toppanel">
            <!-- Sliding Panel
            -->
            <div id="panel">
                <form name="filter">
                <div class="content clearfix">

                    <table width="100%">
                        <tr valign="top">
                            <td valign="top" width="30%">
                                <p class="l2-section-heading">Importance</p>
                                <table width="100%">
                                    <tr><td width="50%"> <input type="checkbox" name="importance" onclick="importance_handler(this, 'importance', true)" checked value="Critical"  /> Critical  </td>
                                        <td width="50%"> <input type="checkbox" name="importance" onclick="importance_handler(this, 'importance', true)" checked value="Low"       /> Low       </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="importance" onclick="importance_handler(this, 'importance', true)" checked value="High"      /> High      </td>
                                        <td width="50%"> <input type="checkbox" name="importance" onclick="importance_handler(this, 'importance', true)" checked value="Wishlist"  /> Wishlist  </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="importance" onclick="importance_handler(this, 'importance', true)" checked value="Medium"    /> Medium    </td>
                                        <td width="50%"> <input type="checkbox" name="importance" onclick="importance_handler(this, 'importance', true)" checked value="Undecided" /> Undecided </td></tr>
                                </table>
                            </td>

                            <td width="20">&nbsp;</td>

                            <td valign="top">
                                <p class="l2-section-heading">Status</p>
                                <table width="100%">
                                    <tr><td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="New"           /> New           </td>
                                        <td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="Incomplete"    /> Incomplete    </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="Confirmed"     /> Confirmed     </td>
                                        <td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="Fix Released"  /> Fix Released  </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="Triaged"       /> Triaged       </td>
                                        <td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="Won't Fix"     /> Won't Fix     </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="In Progress"   /> In Progress   </td>
                                        <td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="Opinion"       /> Opinion       </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="Fix Committed" /> Fix Committed </td>
                                        <td width="50%"> <input type="checkbox" name="status"     onclick="status_handler(this, 'status', true)" checked value="Invalid"       /> Invalid       </td></tr>
                                </table>
                            </td>

                            <td width="20">&nbsp;</td>

                            <td valign="top" width="30%">
                                <p class="l2-section-heading">Series</p>
                                <table width="100%">
                                    <tr><td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="quantal"  /> Quantal  </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="precise"  /> Precise  </td>
                                        <td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="jaunty"   /> Jaunty   </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="oneiric"  /> Oneiric  </td>
                                        <td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="karmic"   /> Karmic   </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="natty"    /> Natty    </td>
                                        <td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="hardy"    /> Hardy    </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="maverick" /> Maverick </td>
                                        <td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value=""         /> Unknown  </td></tr>
                                    <tr><td width="50%"> <input type="checkbox" name="series"     onclick="series_handler(this, 'series', true)" checked value="lucid"    /> Lucid    </td></tr>
                                </table>
                            </td>

                        </tr>

                        <!--
                        <tr valign="top">

                            <td valign="top" width="30%" colspan="5">
                                <p class="l2-section-heading">Assignee</p>
                                <table width="100%">
                                    % for i, elem in enumerate(assignees_list):
                                        % if i % 5 == 0:
                                        <tr>
                                        % endif
                                            <td width="20%"> <input type="checkbox" name="assignees"  onclick="assignee_handler(this, 'series', true)" checked value="${assignees_list[i]}"         /> ${assignees_list[i]} </td>
                                        % if i % 5 == 4:
                                        </tr>
                                        % endif
                                    % endfor
                                </table>
                            </td>
                        </tr>

                        <tr valign="top">

                            <td valign="top">
                                <p class="l2-section-heading">Date</p>
                                <table width="100%">
                                    <tr><td colspan="4">Created within:</td></tr>
                                    <tr><td width="10">&nbsp;</td>
                                        <td width="50"> <input type="radio" name="date"     onclick="date_handler(this, 'date', true)" checked value="1"    /> 24 Hrs.   </td>
                                        <td width="50"> <input type="radio" name="date"     onclick="date_handler(this, 'date', true)" checked value="7"    /> 1 Week    </td>
                                        <td width="50"> <input type="radio" name="date"     onclick="date_handler(this, 'date', true)" checked value="30"   /> 1 Month   </td></tr>
                                    <tr><td width="10">&nbsp;</td>
                                        <td width="50"> <input type="radio" name="date"     onclick="date_handler(this, 'date', true)" checked value="-1"   /> Unlimited </td></tr>
                                </table>
                            </td>

                            <td width="20">&nbsp;</td>

                            <td valign="top">
                                &nbsp;
                            </td>

                            <td width="20">&nbsp;</td>

                            <td valign="top">
                                &nbsp;
                            </td>
                        </tr>
                        -->

                    </table>

                </div>
                </form>

                <div style="clear:both;"></div>
            </div> <!-- panel -->

            <!-- The tab on top -->
            <div class="tab">
                <ul class="login">
                    <li class="left">&nbsp;</li>
                    <li id="toggle">
                        <a id="open" class="open" href="#">&nbsp;Options</a>
                        <a id="close" style="display: none;" class="close" href="#">&nbsp;Close&nbsp;&nbsp;</a>
                    </li>
                    <li class="right">&nbsp;</li>
                </ul>
            </div> <!-- / top -->
        </div> <!-- Top Panel -->

        <div class="outermost">
            <div class="title">
		    ${report_title}
            </div>
            <div class="section">
                % for team in team_report_order:
                    % if 'show_total_bugs_per_team' in report_options and report_options['show_total_bugs_per_team']:
                        <% total = len(bugs_by_team[team].keys()) %>
                        <div class="section-heading">${team}&nbsp;&nbsp;(<span id="${team}-total">${total}</span>)</div>
                    % else:
                        <div class="section-heading">${team}</div>
                    % endif

                    <% id = team.replace(' ', '_') %>
                    <table id="${id}" class="tablesorter" border="0" cellpadding="0" cellspacing="1" width="100%%">
                        <thead>
                            <tr>
                                <th width="40">Bug</th>
                                <th>Summary</th>
                                <th width="100">Package</th>
                                <th width="80">Importance</th>
                                <th width="80">Status</th>
                                <th width="140">Assignee</th>
                                <th width="60">Found</th>
                                <th width="60">Target</th>
                                <th width="100">Duplicates</th>
                            </tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                % endfor

            </div>
            <br />
            <br />
            <div>
                % if 'show_total_bugs' in report_options and report_options['show_total_bugs']:
                    <div id="bug-total">Total: 000</div>
                % endif

            </div>
            <div>
                <br />
                <hr />
                <table width="100%%" cellspacing="0" cellpadding="0">
                    <thead>
                        <tr>
                            <td width="100">Column</td>
                            <td>Description</td>
                        </tr>
                    </th>
                    <tbody>
                        <tr><td>Bug       </td><td>The Launchpad Bug number and a link the the Launchpad Bug.           </td></tr>
                        <tr><td>Summary   </td><td>The 'summary' or 'title' from the bug.                               </td></tr>
                        <tr><td>Package   </td><td>The package a bug task was created for relating to the specific bug. </td></tr>
                        <tr><td>Importance</td><td>The bug task's importance.                                           </td></tr>
                        <tr><td>Status    </td><td>The bug task's status.                                               </td></tr>
                        <tr><td>Assignee  </td><td>The person or team assigned to work on the bug.                      </td></tr>
                        <tr><td>Found     </td><td>The milestone during which the bug was found.                        </td></tr>
                        <tr><td>Target    </td><td>The milestone the bug task is targeted to be fixed.                  </td></tr>
                        <tr><td>Duplicates</td><td>Quantity of duplicate bug reports.                                   </td></tr>
                    </tbody>
                </table>
                <br />
            </div>
            <div>
                <br />
                <hr />
                <table width="100%%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            ${timestamp}
                        </td>
                        <td align="right">
                            &nbsp;
                            Themes:&nbsp;&nbsp;
                            <a href='#' onclick="setActiveStyleSheet('dark'); return false;">DARK</a>
                            &nbsp;
                            <a href='#' onclick="setActiveStyleSheet('light'); return false;">LIGHT</a>
                        </td>
                    </tr>
                </table>
                <br />
            </div>


        </div> <!-- Outermost -->
    </body>

    <script type="text/javascript">
       // add parser through the tablesorter addParser method
       $.tablesorter.addParser({
           // set a unique id
           id: 'age',
           is: function(s) { return false; },
           format: function(s) {
               // format your data for normalization
               fields  = s.split('.')
               days    = parseInt(fields[0], 10) * (60 * 24);
               hours   = parseInt(fields[1], 10) * 60;
               minutes = parseInt(fields[2]);
               total   = minutes + hours + days
               return total;
           },
           // set type, either numeric or text
           type: 'numeric'
       });

       // add parser through the tablesorter addParser method
       $.tablesorter.addParser({
           // set a unique id
           id: 'importance',
           is: function(s) { return false; },
           format: function(s) {
               // format your data for normalization
               return s.toLowerCase().replace(/critical/,6).replace(/high/,5).replace(/medium/,4).replace(/low/,3).replace(/wishlist/,2).replace(/undecided/,1).replace(/unknown/,0);
           },
           // set type, either numeric or text
           type: 'numeric'
       });

       // add parser through the tablesorter addParser method
       $.tablesorter.addParser({
           // set a unique id
           id: 'status',
           is: function(s) { return false;
           },
           format: function(s) {
               // format your data for normalization
               return s.toLowerCase().replace(/new/,12).replace(/incomplete/,11).replace(/confirmed/,10).replace(/triaged/,9).replace(/in progress/,8).replace(/fix committed/,7).replace(/fix released/,6).replace(/invalid/,5).replace(/won't fix/,4).replace(/confirmed/,3).replace(/opinion/,2).replace(/expired/,1).replace(/unknown/,0);
           },
           // set type, either numeric or text
           type: 'numeric'
       });
       $(function() {
            % for team in team_report_order:
                <% id = team.replace(' ', '_') %>
                $("#${id}").tablesorter({
                    headers: {
                        3: {
                            sorter:'importance'
                        },
                        4: {
                            sorter:'status'
                        }
                    },
                    widgets: ['zebra']
                });
            % endfor
        });
    </script>

    <script type="text/javascript">
        var series = ["precise", "jaunty", "oneiric", "karmic", "natty", "hardy", "maverick", "lucid", ""];
        var importance = ["Critical", "Low", "High", "Wishlist", "Medium", "Undecided"];
        var task_status = ["New", "Incomplete", "Confirmed", "Fix Released", "Triaged", "Won't Fix", "In Progress", "Opinion", "Fix Committed", "Invalid"];
        var assignees = [];
        var date_filter = -1;
        var jd = ${json_data_string};
        var first_time = true;

        var importance_color = {
                "Unknown"       : "importance-unknown",
                "Critical"      : "importance-critical",
                "High"          : "importance-high",
                "Medium"        : "importance-medium",
                "Low"           : "importance-low",
                "Wishlist"      : "importance-wishlist",
                "Undecided"     : "importance-undecided"
            };

        var status_color = {
                "New"           : "status-new",
                "Incomplete"    : "status-incomplete",
                "Confirmed"     : "status-confirmed",
                "Triaged"       : "status-triaged",
                "In Progress"   : "status-in_progress",
                "Fix Committed" : "status-fix_committed",
                "Fix Released"  : "status-fix_released",
                "Invalid"       : "status-invalid",
                "Won't Fix"     : "status-wont_fix",
                "Opinion"       : "status-opinion",
                "Expired"       : "status-expired",
                "Unknown"       : "status-unknown"
            };

        var teams_id_list = [];
        var teams_name_list = [];
        % for team in team_report_order:
            <% id = team.replace(' ', '_') %>
            teams_id_list.push("${id}");
            teams_name_list.push("${team}");
        % endfor

        function series_handler(chkbx, grp, update_table) {
            series = [];
            for (i = 0; i < document.filter.length; i++) {
                if (document.filter[i].name == "series") {
                    if (document.filter[i].checked) {
                        series.push(document.filter[i].value);
                    }
                }
            }

            if (update_table) {
                update_tables();
            }
        }

        function importance_handler(chkbx, grp, update_table) {
            importance = [];
            for (i = 0; i < document.filter.length; i++) {
                if (document.filter[i].name == "importance") {
                    if (document.filter[i].checked) {
                        importance.push(document.filter[i].value);
                    }
                }
            }

            if (update_table) {
                update_tables();
            }
        }

        function assignee_handler(chkbx, grp, update_table) {
            assignees = [];
            for (i = 0; i < document.filter.length; i++) {
                if (document.filter[i].name == "assignees") {
                    if (document.filter[i].checked) {
                        assignees.push(document.filter[i].value);
                    }
                }
            }

            if (update_table) {
                update_tables();
            }
        }

        function status_handler(chkbx, grp, update_table) {
            task_status = [];
            for (i = 0; i < document.filter.length; i++) {
                if (document.filter[i].name == "status") {
                    if (document.filter[i].checked) {
                        task_status.push(document.filter[i].value);
                    }
                }
            }

            if (update_table) {
                update_tables();
            }
        }

        function date_handler(chkbx, grp, update_table) {
            date_filter = -1;
            for (i = 0; i < document.filter.length; i++) {
                if (document.filter[i].name == "date") {
                    if (document.filter[i].checked) {
                        date_filter = parseInt(document.filter[i].value);
                    }
                }
            }

            if (update_table) {
                update_tables();
            }
        }

        function update_tables() {
            var bug_total = 0;
            var tables = {
            % for team in team_report_order:
                "${team}" : "",
            % endfor
            };
            var totals = {
            % for team in team_report_order:
                "${team}" : 0,
            % endfor
            };

            var oddness = {
            % for team in team_report_order:
                "${team}" : true,
            % endfor
            };

            $.each(jd, function(bid, tasks) {
                $.each(tasks, function(index, task) {
                    var fail = false;

                    if (series.indexOf(task.bug.series_name) == -1) {
                        fail = true;
                    }

                    if (!fail && importance.indexOf(task.importance) == -1) {
                        fail = true;
                    }

                    if (!fail && task_status.indexOf(task.status) == -1) {
                        fail = true;
                    }

                    /*
                    if (!fail && assignees.indexOf(task.assignee) == -1) {
                        fail = true;
                    }

                    if (!fail && date_filter != -1) {
                        if (task.bug.age > date_filter) {
                            fail = true;
                        }
                    }
                    */

                    s = "";
                    if (!fail) {
                        bug_total++;
                        if (oddness[task.team]) {
                            s += "<tr class=\"odd\">";
                            oddness[task.team] = false;
                        } else {
                            s += "<tr class=\"even\">";
                            oddness[task.team] = true;
                        }
                        s += "<td><a href=\"http://launchpad.net/bugs/" + bid + "\">" + bid + "</a></td>";
                        s += "<td>" + task.bug.title + "</td>";
                        s += "<td>" + task.task_name + "</td>";
                        s += "<td class=\"" + importance_color[task.importance] + "\">" + task.importance + "</td>";
                        s += "<td class=\"" + status_color[task.status] + "\">" + task.status + "</td>";
                        s += "<td>" + task.assignee + "</td>";
                        s += "<td>" + task.milestone_found + "</td>";
                        s += "<td>" + task.milestone_target + "</td>";
                        s += "<td>" + task.bug.number_of_duplicates + "</td>";
                        s += "</tr>";
                        tables[task.team] += s;
                        totals[task.team]++;
                    }
                });
            });

            $.each(tables, function(team, val) {
                id = team.replace(/ /g, '_');
                $("#" + id + " tbody").html(tables[team]);
                $("#" + id).trigger("update");
                % if 'show_total_bugs_per_team' in report_options and report_options['show_total_bugs_per_team']:
                    document.getElementById(team + "-total").innerHTML = totals[team];
                % endif
            });
            if (first_time) {
                first_time = false;
                sortList = [[8,1], [3,1], [4,1]];
                $.each(tables, function(team, val) {
                    id = team.replace(/ /g, '_');
                    $("#" + id).trigger("sorton", [sortList]);
                });
            }
            % if 'show_total_bugs' in report_options and report_options['show_total_bugs']:
                document.getElementById("bug-total").innerHTML = "Total: " + bug_total;
            % endif
        }

        $(document).ready(function(){
            // Expand Panel
            $("#open").click(function(){ $("div#panel").slideDown("slow"); });

            // Collapse Panel
            $("#close").click(function(){ $("div#panel").slideUp("slow"); });

            // Switch buttons on the tab from "Options" to "Close"
            $("#toggle a").click(function () { $("#toggle a").toggle(); });

            series_handler(null, null, false);
            importance_handler(null, null, false);
            status_handler(null, null, false);
            /*
            assignee_handler(null, null, false);
            date_handler(null, null, false);
            */
            update_tables();
        });
    </script>

</html>
<!-- vi:set ts=4 sw=4 expandtab syntax=mako: -->
