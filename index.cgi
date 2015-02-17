#!/bin/bash

echo "Content-type: text/html"
echo ""
echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>Boyfriend youtube-dl</title>'
echo '</head>'
echo '<body>'

IFS="&"
for var in $QUERY_STRING; do
  declare "$var"
done

# URL Decode: Replace %NN with \xNN and pass the lot to printf -b, which will decode hex
test -n "$youtube" && printf -v youtube '%b' "${youtube//%/\\x}"
test -n "$file" && printf -v file '%b' "${file//%/\\x}"
test -n "$file" && printf -v file '%b' "${file//+/ }" # turn '+' to spaces
test -n "$scale" && printf -v scale '%b' "${scale//%/\\x}"

# Vars (after decode)
test -n "$file" -a -f "$file" && filename="$(basename $file)"
test -z "$scale" && scale=320


# Banner
echo "<h1>Boyfriend YouTube Download</h1>"

echo '[<a href="/">Start over</a>]'
echo '[<a href="/youtube-dl/history">Dowload video history</a>]'

# Output
echo "<form method=GET action=\"${SCRIPT}\">"
echo '<table nowrap>'

echo "<tr><td>Video URL</TD><TD><input type=text name=youtube size=45 value=''></td></tr>"
echo '</tr></table><br>'

echo '<input type="submit" value="Process">'
echo '</form>'


# Download
if test -n "$youtube"; then
  file="$(youtube-dl --get-filename --restrict-filenames "$youtube")"

  test -f "history/$file" || printf "%s\t%s\t%s\n" "$(date)" "$youtube" "$file" >> history/vids.log
  youtube-dl --restrict-filenames -o "history/$file" "$youtube"

  echo "<a>Size: $(du -sh "$PWD/history/$file" 2>&1)</a> <a href='/?file=$PWD/history/$file&start=0'>edit</a><br>"
  echo "<img src='$(youtube-dl --get-thumbnail --restrict-filenames "$youtube")' width=45%>"
fi

echo '</body>'
echo '</html>'
