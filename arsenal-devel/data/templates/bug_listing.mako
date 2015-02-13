<%include file="header.mako"/>
    <body class="bugbody">
        <%include file="sliding_panel.mako"/>

        <div class="outermost">
            <div class="title">
		    ${report["title"]}
            </div>
            <div class="section">
                % for team in report["team_order"]:
                    <div class="section-heading">${team}</div>

                    <% id = team.replace(' ', '_') %>
                    <table id="${id}" class="tablesorter">
                        <thead>
                            <tr>
                                <th width="40">Bug</th>
                                <th>Summary</th>
                                <th width="140">Package</th>
                                <th width="80">Importance</th>
                                <th width="80">Status</th>
                                <th width="80">Assignee</th>
                                <th width="60">Found</th>
                                <th width="60">Target</th>
                                <th width="40">Age</th>
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
                        <tr><td>Age   </td><td>Days since the bug was created.</td></tr>
                    </tbody>
                </table>
                <br />
            </div>
            <div>
                <br />
                <hr />
                <table width="100%%" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>${timestamp}</td>
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
            % for team in report["team_order"]:
                <% id = team.replace(' ', '_') %>
                $("#${id}").tablesorter({
                    headers: {
                        3: { sorter:'importance' },
                        4: { sorter:'status' }
                    },
                    widgets: ['zebra']
                });
            % endfor
        });
    </script>

    <script type="text/javascript">
        var series = ${report["series"]};
        var importance = ${report["importance"]};
        var task_status = ${report["status"]};
        var assignees = [];
        var date_filter = -1;
	var data = ${data};
        var first_time = true;

        var importance_color = {
	    % for prop in report["importance"]:
            "${prop}": "importance-${prop.lower()}",
	    % endfor
            };
        var status_color = {
	    % for prop in report["status"]:
            "${prop}": "status-${prop.lower().replace(' ', '_').replace("'", "")}",
	    % endfor
            };

        var teams_id_list = [];
        var teams_name_list = [];
        % for team in report["team_order"]:
            <% id = team.replace(' ', '_') %>
            teams_id_list.push("${id}");
            teams_name_list.push("${team}");
        % endfor

	function get_filtered_items(filt) {
	    items = [];
            for (i = 0; i < document.filter.length; i++) {
                if (document.filter[i].name == filt) {
                    if (document.filter[i].checked) {
                        items.push(document.filter[i].value);
                    }
                }
            }
	    return items;
        }
		    
        function series_handler(chkbx, grp, update_table) {
            series = get_filtered_items("series");
            if (update_table) {
                update_tables();
            }
        }

        function importance_handler(chkbx, grp, update_table) {
            importance = get_filtered_items("importance");
            if (update_table) {
                update_tables();
            }
        }

	function assignee_handler(chkbx, grp, update_table) {
            assignees = get_filtered_items("assignees");
            if (update_table) {
                update_tables();
            }
        }

        function status_handler(chkbx, grp, update_table) {
	    task_status = get_filtered_items("status");	    
            if (update_table) {
                update_tables();
            }
        }

        function date_handler(chkbx, grp, update_table) {
            date_filter = -1;
            items = get_filtered_items("date");
            if (len(items) > 0) {
                date_filter = parseInt(items[0]);
            }
            if (update_table) {
                update_tables();
            }
        }

        function update_tables() {
            var tables = {
            % for team in report["team_order"]:
                "${team}" : "",
            % endfor
            };

            var oddness = {
            % for team in report["team_order"]:
                "${team}" : true,
            % endfor
            };

            $.each(data, function(bid, bug) {

                $.each(bug.tasks, function(index, task) {
                    var fail = false;
		    var bug = data[bid];

/*
                    if (series.indexOf(bug.series_name) == -1) {
                        fail = true;
                    }
*/
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
                        if (bug.age > date_filter) {
                            fail = true;
                        }
                    }
*/
                    s = "";
                    if (!fail) {
                        if (oddness["ubuntu-x-swat"]) {
                            s += "<tr class=\"odd\">";
                            oddness["ubuntu-x-swat"] = false;
                        } else {
                            s += "<tr class=\"even\">";
                            oddness["ubuntu-x-swat"] = true;
                        }
                        s += "<td><a href=\"http://launchpad.net/bugs/" + bid + "\">" + bid + "</a></td>";
                        s += "<td>" + bug.title + "</td>";
                        s += "<td>" + task.target + "</td>";
                        s += "<td class=\"" + importance_color[task.importance] + "\">" + task.importance + "</td>";
                        s += "<td class=\"" + status_color[task.status] + "\">" + task.status + "</td>";
			if (task.assignee) {
                            s += "<td>" + task.assignee + "</td>";
			} else {
			    s += "<td></td>";
			}
		        if (task.milestone_found) {
                            s += "<td>" + task.milestone_found + "</td>";
                        } else {
                            s += "<td></td>";
                        }
		        if (task.milestone) {
                            s += "<td>" + task.milestone + "</td>";
                        } else {
                            s += "<td></td>";
                        }
                        s += "<td>" + bug.age + "</td>";
                        s += "</tr>";
                        tables["ubuntu-x-swat"] += s;
                    }
                });
            });

            $.each(tables, function(team, val) {
                id = team.replace(/ /g, '_');
                $("#" + id + " tbody").html(tables[team]);
                $("#" + id).trigger("update");
            });
            if (first_time) {
                first_time = false;
                sortList = [[3,1], [4,1]];
                $.each(tables, function(team, val) {
                    id = team.replace(/ /g, '_');
                    $("#" + id).trigger("sorton", [sortList]);
                });
            }
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

<%include file="header.mako"/>
<!-- vi:set ts=4 sw=4 expandtab syntax=mako: -->
