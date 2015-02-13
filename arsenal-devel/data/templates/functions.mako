<%def name="interleave(name, l)">
  <table width="100%">
  <%
     items = []
     mid = len(l)/2 + (len(l) % 2)
     for i in range(0, mid):
       items.append(l[i])
       if mid+i < len(l):
         items.append(l[mid+i])
       else:
         items.append('')
     endfor
   %>
  % for i, value in enumerate(items):
    ${"<tr>" if (i+1) % 2 else ''}
    <td width="50%">
      % if value != '':
      <input
         type="checkbox" name="${name}"
         onclick="${name}_handler(this, '${name}', true)"
         checked value="${value}" />${value}
      % endif
    </td>
    ${"</tr>" if i % 2 else ''}
  % endfor
  </table>
</%def>
