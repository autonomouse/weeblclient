
function hiderows(tbl, col) {
  var args = hiderows.arguments;
  for (var i in tbl.rows) {
    var row = tbl.rows[i];
    for (var j = hiderows.length; j <= args.length; j++) {
      if (row.cells[col].innerHTML == args[j]) {
        row.style.display = 'none';
        row.style.visibility = 'hidden';
        break;
      }
    }
  }
}

function showrows(tbl) {
      for (var i in tbl.rows) {
          var row = tbl.rows[i];
          row.style.display = '';
          row.style.visibility = 'visible';
      }
}

