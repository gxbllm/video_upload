
#!/bin/bash

echo "Content-type: text/html"
echo ""
echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>Boyfriend youtube-dl history</title>'
echo '</head>'
echo '<body>'

IFS="&"
for var in $QUERY_STRING; do
  declare "$var"
done

# URL Decode: Replace %NN with \xNN and pass the lot to printf -b, which will decode hex
test -n "$delete" && printf -v delete '%b' "${delete//%/\\x}"
test -n "$delete" && printf -v delete '%b' "${delete//+/ }"

# Vars
test -z "$page" -o "$page" = "0" && page=1
prev=$(( $page - 1 ))
next=$(( $page + 1 ))
test -z "$num" && num=10
sofar=$(( $num * $page ))


# Banner
echo "<h1>Boyfriend YouTube Download History</h1>"

echo '<a href="/">[Start over]</a>'
test "$prev" != "0" && echo "[<a href='?page=$prev'>Prev page</a>]" || echo "<a>[Prev page]</a>"
test $(wc -l < vids.log) -gt $sofar && echo "[<a href='?page=$next'>Next page</a>]" || echo "<a>[Next page]</a>" # wc cant be trusted with an actual file argument because there is no way to stop printing its name
echo "<br>"

# Delete
if test -n "$delete" && grep --silent "$delete" vids.log; then
  grep -v "$delete" vids.log >> vids.log.new
  rm -v "$delete" 2>&1
  rm "$delete" 2>&1
  mv vids.log.new vids.log
fi

# Output
while read line; do
  date="$( echo "$line" | cut -f 1)"
  link="$( echo "$line" | cut -f 2)"
  file="$( echo "$line" | cut -f 3)"

  echo "<br><a>"
  echo "Date: $date"
  echo "Link: <a href='$link'>$link</a>"
  echo "File: $file"
  echo "</a><br>"

  echo "<a>Size: $(du -sh "$PWD/$file" 2>&1)</a> <a href='/?file=$PWD/$file&start=0'>edit</a> <a href='?delete=$file'>delete</a>"
  echo "<br><img src='$(youtube-dl --get-thumbnail --restrict-filenames "$link")' width=45%><br>"
done < <(tail -n $sofar vids.log | head -n $num | tac 2>/dev/null || tail -n $sofar vids.log | head -n $num | tail -r) # Linux vs Mac

echo '</body>'
echo '</html>'
