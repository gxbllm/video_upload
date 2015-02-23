#!/bin/bash

echo "Content-type: text/html"
echo ""
echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>video upload</title>'
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
echo "<h1>Video Upload</h1>"

echo '[<a href="/">Start over</a>]'
echo '[<a href="./history">Video History</a>]'

# Output
echo "<form method=GET action=\"${SCRIPT}\">"
echo "<label for='youtube'>YouTube Link: </label>"
echo "<input type='text' name='youtube' size=45 value=''>"
echo "<br><input type='submit' value='Process'>"
echo "</form>"

echo "<form method=POST action=\"${SCRIPT}\" enctype="multipart/form-data">"
echo "<label for='file'>Upload File: </label>"
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

  echo "<a>Size: $(du -sh "history/$file" 2>&1)</a>"
  echo "<a href='/?file=$PWD/history/$file'>edit</a>"
  echo "<br><img src='$thumb' width=45%><br>"
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

  size=$((HTTP_CONTENT_LENGTH-a))
  file="history/upload.mp4"

  dd ibs=1 obs=512 count=$size of="$file"
  sed -i '$d' "$file"
  sed -i '$d' "$file"
  sed -i '$d' "$file"
  sed -i '$d' "$file"

  echo "<a>Size: $(du -sh "$file" 2>&1)</a>
  echo "<a href='/?file=$PWD/$file'>edit</a>"
  echo "<br><img src='data:image/png;charset=utf-8;base64,$(ffmpeg -ss 2 -i "$file" -t 1 -f image2pipe -vcodec ppm - | convert - png:- | base64)' width=45%><br>"
fi

echo '</body>'
echo '</html>'
