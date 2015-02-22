#!/bin/bash

echo "Content-type: text/html"
echo ""
echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>youtube-dl or file upload</title>'
echo '</head>'
echo '<body>'

PATH=/usr/local/bin:$PATH
which youtube-dl 2>&1 >/dev/null

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
echo "<h1>YouTube-Download or File Upload</h1>"

echo '[<a href="/">Start over</a>]'
echo '[<a href="/youtube-dl/history">Dowload video history</a>]'

# Output
echo "<form method=GET action=\"${SCRIPT}\">"
echo "<label for='youtube'>YouTube Link: </label>"
echo "<input type='text' name='youtube' size=45 value=''>"
echo "<br><input type='submit' value='Process'>"
echo "</form>"

echo "<form method=POST action=\"${SCRIPT}\" enctype="multipart/form-data">"
echo "<label for='file'>Upload Video: </label>"
echo "<input type='file' name='file'>"
echo "<br><input type='submit' value='Process'>"
echo "</form>"


# Download
if test -n "$youtube"; then
  file="$(youtube-dl --get-filename --restrict-filenames "$youtube")"
  thumb="$(youtube-dl --get-thumbnail --restrict-filenames "$youtube")"

  if ! test -f "history/$file"; then
    youtube-dl --restrict-filenames -o "history/$file" "$youtube" 2>&1
    test $? = 0 && printf "%s\t%s\t%s\t%s\n" "$(date)" "$youtube" "$thumb" "$file" >> history/vids.log
  fi

  echo "<a>Size: $(du -sh "history/$file" 2>&1)</a> <a href='/?file=$PWD/history/$file'>edit</a><br>"
  echo "<img src='$thumb' width=45%>"
fi

# Upload
if test "$REQUEST_METHOD" = "POST"; then
  OIFS="$IFS"
  read boundary
  read disposition
  read ctype
  read junk

  a=${#boundary}
  b=${#disposition}
  c=${#ctype}
  a=$((a*2+b+c+d+10))

  SIZE=$((HTTP_CONTENT_LENGTH-a))

  dd ibs=1 obs=512 count=$SIZE of=vid$file
  sed -i '$d' vid$file
  sed -i '$d' vid$file
  sed -i '$d' vid$file
  sed -i '$d' vid$file

  echo "<a>Size: $(du -sh upload 2>&1)</a> <a href='/?file=$PWD/upload'>edit</a><br>"
  echo "<img src='data:image/png;charset=utf-8;base64,$(ffmpeg -ss 2 -i upload -t 1 -f image2pipe -vcodec ppm - | convert - png:- | base64)' width=45%>"
fi

echo '</body>'
echo '</html>'
