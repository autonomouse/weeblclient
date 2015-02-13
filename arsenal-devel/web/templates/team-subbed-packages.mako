<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<%
    packages_by_team = {}
    teams = template_data.keys()
    for team in teams:
        packages_by_team[team] = template_data[team]

    team_report_order = []
    if 'unsubscribed' in packages_by_team:
        team_report_order.append('unsubscribed') # We want unknown first
    for t in sorted(teams):
        if t != 'unsubscribed':
            team_report_order.append(t)
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
        <div class="outermost">
            <div class="title">
		    ${report_title}
            </div>
            <div class="section">
                % for team in team_report_order:
                    <a href="#${team}">${team}</a>
                % endfor
            </div>
            <div class="section">
                % for team in team_report_order:
                    <% total = len(packages_by_team[team]) %>
                        <a name="${team}"></a>
                        <div class="section-heading">${team}&nbsp;&nbsp;(<span id="${team}-total">${total}</span>)</div>
                    <% id = team.replace(' ', '_') %>
                    <table id="${id}" class="tablesorter" border="0" cellpadding="0" cellspacing="1" width="100%%">
                        <thead>
                            <tr>
                                <!-- what else might be useful -->
                                <th width="100">Package</th>
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
       $(function() {
            % for team in team_report_order:
                <% id = team.replace(' ', '_') %>
                $("#${id}").tablesorter({
                    headers: {
                        0: {
                        }
                    },
                    widgets: ['zebra']
                });
            % endfor
        });
    </script>
    <script type="text/javascript">
        var jd = ${json_data_string};
        var first_time = true;

        var teams_id_list = [];
        var teams_name_list = [];
        % for team in team_report_order:
            <% id = team.replace(' ', '_') %>
            teams_id_list.push("${id}");
            teams_name_list.push("${team}");
        % endfor

        function update_tables() {
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

            $.each(jd, function(team, spackages) {
                $.each(spackages, function(index, spackage) {
                    s = "";
                    if (oddness[team]) {
                        s += "<tr class=\"odd\">";
                        oddness[team] = false;
                    } else {
                        s += "<tr class=\"even\">";
                        oddness[team] = true;
                    }
                    s += "<td><a href='https://launchpad.net/ubuntu/+source/" + spackage;
                    s += "'>" + spackage  + "</a></td>";
                    s += "</tr>";
                    tables[team] += s;
                    totals[team]++;
                });
            });

            $.each(tables, function(team, val) {
                id = team.replace(/ /g, '_');
                $("#" + id + " tbody").html(tables[team]);
                $("#" + id).trigger("update");
            });
            if (first_time) {
                first_time = false;
                sortList = [[0,0]];
                $.each(tables, function(team, val) {
                    id = team.replace(/ /g, '_');
                    $("#" + id).trigger("sorton", [sortList]);
                });
            }
        }

        $(document).ready(function(){
            update_tables();
        });
    </script>

</html>
<!-- vi:set ts=4 sw=4 expandtab syntax=mako: -->
