<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>${report_title}</title>

        <link title="light" rel="stylesheet" href="css/light-style.css" type="text/css" media="print, projection, screen" />
        <link title="dark"  rel="stylesheet" href="css/dark-style.css"  type="text/css" media="print, projection, screen" />

        <script type="text/javascript" src="http://people.canonical.com/~kernel/reports/js/styleswitcher.js"></script>

        <link href='http://fonts.googleapis.com/css?family=Cantarell&subset=latin'              rel='stylesheet' type='text/css'>
        <script type="text/javascript" src="http://people.canonical.com/~kernel/reports/js/jquery-latest.js"></script>
        <script type="text/javascript" src="js/jquery.tablesorter.js"></script>

    </head>


    <body class="bugbody">

        <div class="outermost">
            <div class="title">
		    ${report_title}
            </div>
            <div class="section">
                <table id="linux" class="tablesorter" border="0" cellpadding="0" cellspacing="1" width="100%%">
                    <thead>
                        <tr>
                            <th width="40">Bug</th>
                            <th>Summary</th>
                            <th width="60">Series</th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
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
                        <tr><td>Bug        </td><td>Launchpad Bug number and a link the the Launchpad Bug.           </td></tr>
                        <tr><td>Summary    </td><td>'summary' or 'title' from the bug.                               </td></tr>
                        <tr><td>Importance </td><td>Bug task's importance.                                           </td></tr>
                        <tr><td>Status     </td><td>Bug task's status.                                               </td></tr>
                        <tr><td>Assignee   </td><td>Person or team assigned to work on the bug.                      </td></tr>
                        <tr><td>Series     </td><td>Ubuntu series name the bug was found in.                         </td></tr>
                        <tr><td>CO         </td><td>Number of comments added to the bug.                             </td></tr>
                        <tr><td>SU         </td><td>Number of subscribers to the bug.                                </td></tr>
                        <tr><td>AM         </td><td>Number of people that have indicated "affects me".               </td></tr>
                        <tr><td>Heat       </td><td>Launchpad Heat calculation.                                      </td></tr>
                        <tr><td>Nominations</td><td>A list of all the series the bug has been nominated for.         </td></tr>
                    </tbody>
                </table>
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
           is: function(s) {
               // return false so this parser is not auto detected
               return false;
           },
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
           is: function(s) {
               // return false so this parser is not auto detected
               return false;
           },
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
           is: function(s) {
               // return false so this parser is not auto detected
               return false;
           },
           format: function(s) {
               // format your data for normalization
                   return s.toLowerCase().replace(/new/,12).replace(/incomplete/,11).replace(/confirmed/,10).replace(/triaged/,9).replace(/in progress/,8).replace(/fix committed/,7).replace(/fix released/,6).replace(/invalid/,5).replace(/won't fix/,4).replace(/confirmed/,3).replace(/opinion/,2).replace(/expired/,1).replace(/unknown/,0);
           },
           // set type, either numeric or text
           type: 'numeric'
       });
       $(function() {
            $("#linux").tablesorter({
                headers: {
                    2: {
                        sorter:'importance'
                    },
                    3: {
                        sorter:'status'
                    },
                    11: {
                        sorter:'numeric'
                    }
                },
                widgets: ['zebra']
            });
        });
    </script>

    <script type="text/javascript">
        var series = ["precise", "jaunty", "oneiric", "karmic", "natty", "hardy", "maverick", "lucid", ""];
        var importance = ["Critical", "Low", "High", "Wishlist", "Medium", "Undecided"];
        var task_status = ["New", "Incomplete", "Confirmed", "Fix Released", "Triaged", "Won't Fix", "In Progress", "Opinion", "Fix Committed", "Invalid"];
        var assignees = [];
        var date_filter = -1;
        var jd = ${json_data_string};

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
                build_table();
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
                build_table();
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
                build_table();
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
                build_table();
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
                build_table();
            }
        }

        function build_table() {
            s = "";
            odd = true;
            $.each(jd, function(bid, val) {
                var bug = jd[bid];
                var fail = false;

                if (!fail) {
                    if (odd) {
                        s += "<tr class=\"odd\">";
                        odd = false;
                    } else {
                        s += "<tr class=\"even\">";
                        odd = true;
                    }
                    s += "<td><a href=\"http://launchpad.net/bugs/" + bid + "\">" + bid + "</a></td>";
                    s += "<td>" + bug[0].bug["title"] + "</td>";
                    s += "<td>" + bug[0].bug["series_name"] + "</td>";
                    s += "</tr>";
                }
            });

            $("#linux tbody").html(s);
            $("#linux").trigger("update");
            sortList = [[1,1]];
            $("#linux").trigger("sorton", [sortList]);
        }

        $(document).ready(function(){
            build_table();
        });
    </script>

</html>
<!-- vi:set ts=4 sw=4 expandtab: -->
