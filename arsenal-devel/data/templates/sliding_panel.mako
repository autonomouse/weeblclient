<%namespace file="functions.mako" import="*"/>
        <!-- Top Panel -->
        <div id="toppanel">
            <!-- Sliding Panel -->
            <div id="panel">
                <form name="filter">
                <div class="content clearfix">

                    <table width="100%">
                        <tr valign="top">
			  % for prop in ["importance", "status", "series"]:
                            <td valign="top" width="30%">
                                <p class="l2-section-heading">${prop.capitalize()}</p>
				${interleave(prop, report[prop])}
                            </td>
                            <td width="20">&nbsp;</td>
			  % endfor
                        </tr>

                        <!--
                        <tr valign="top">

                            <td valign="top" width="30%" colspan="5">
                                <p class="l2-section-heading">Assignee</p>
                                <table width="100%">
                                    % for i, elem in enumerate(report["assignees"]):
                                        % if i % 5 == 0:
                                        <tr>
                                        % endif
                                            <td width="20%"> <input type="checkbox" name="assignees"  onclick="assignee_handler(this, 'series', true)" checked value="${report["assignees"]}"         /> ${report["assignees"][i]} </td>
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
                            <td valign="top">&nbsp;</td>
                            <td width="20">&nbsp;</td>
                            <td valign="top">&nbsp;</td>
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
