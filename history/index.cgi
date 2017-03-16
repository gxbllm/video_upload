#!/bin/bash

# Requirements
PATH=/usr/local/bin:$PATH # Fix PATH on OS X
which youtube-dl 2>&1 >/dev/null

# URL Parse
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

# Delete
if test -n "$delete" && grep --silent "$delete" vids.log; then
  grep -v "$delete" vids.log >> vids.log.new
  rm -v "$delete"
  mv vids.log.new vids.log
fi




# HTTP
echo "Content-type: text/html"
echo ""

# HTML
echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>video history</title>'
echo '</head>'
echo '<body>'

# Banner
echo "<h1>Video History</h1>"

# Menu
echo "[<a href='../'>Go back</a>]"
test "$prev" != "0" && echo "[<a href='?page=$prev'>Prev page</a>]" || echo "<a>[Prev page]</a>"
test $(wc -l < vids.log) -gt $sofar && echo "[<a href='?page=$next'>Next page</a>]" || echo "<a>[Next page]</a>" # wc cant be trusted with an actual file argument because there is no way to stop printing its name


# Output
while read line; do
  date="$( echo "$line" | cut -f 1)"
  link="$( echo "$line" | cut -f 2)"
  thumb="$( echo "$line" | cut -f 3)"
  file="$( echo "$line" | cut -f 4)"

  echo "<h5>"
  echo "<a>Date: $date</a><br>"
  echo "<a>Link: </a><a href='$link'>$link</a><br>"

  echo "<a>Size: $(du -sh "$file" 2>&1)</a>"
  echo "<a href='../../?file=$PWD/$file'>edit</a>"
  echo "<a href='./?delete=$file'>delete</a><br>"
  if test -z "$thumb"; then
    echo "<img src='data:image/png;charset=utf-8;base64,$(ffmpeg -ss 2 -i "$FILE" -t 1 -f image2pipe -vcodec ppm - | convert - png:- | base64)' width=45%><br>"
  else
    echo "<img src='$thumb' width=45%><br>"
  fi
  echo "</h5>"
done < <(tail -n $sofar vids.log | head -n $num | tac 2>/dev/null || tail -n $sofar vids.log | head -n $num | tail -r) # Linux vs Mac

echo '</body>'
echo '</html>'
