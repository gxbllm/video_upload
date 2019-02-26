#!/usr/bin/bash

# Requirements
PATH=/usr/local/bin:$PATH # Fix PATH on OS X
which youtube-dl 2>&1 >/dev/null

# URL Parse
test -z "${QUERY_STRING}" && QUERY_STRING="$( echo $2 | cut -d? -f2 -s)"
test -z "${location}" && location="$( echo $2 | cut -d? -f1)"

cd ./${location}

oldIFS="$IFS"
IFS="&"
for var in $QUERY_STRING; do
  declare "$var"
done
IFS="$oldIFS"

# URL Decode: Replace %NN with \xNN and pass the lot to printf -b, which will decode hex
test -n "$video" && printf -v video '%b' "${video//%/\\x}"

VIDEO_QUALITY=160

# Functions
download_file() {
  file="$( youtube-dl --get-filename --restrict-filenames -o '%(title)s-%(id)s.%(ext)s' "$video" )"
  thumb="$( youtube-dl --get-thumbnail --restrict-filenames "$video" )"
  thumb="${file%.*}.${thumb##*.}"

  youtube-dl -f $VIDEO_QUALITY --write-thumbnail --no-playlist -o "history/$file" "$video"
  test $? = 0 && printf "%s\t%s\t%s\t%s\n" "$(date)" "$video" "$thumb" "$file" >> history/vids.log
}

upload_file() {
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
  file="upload_$(date +%F-%H-%M-%S).mp4"

  dd ibs=1 obs=512 count=$size of="history/$file"
  sed -i '$d' "$file"
  sed -i '$d' "$file"
  sed -i '$d' "$file"
  sed -i '$d' "$file"
}




# HTTP
echo "Content-type: text/html"
echo ""

# HTML
echo '<html>'
echo '<head>'
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
echo '<title>video upload</title>'
echo "<style>
pre {
    font-size: 5px;
}
</style>"
echo '</head>'
echo '<body>'
echo '<article>'

# Banner
echo "<h1>Video Upload</h1>"

# Menu
echo '[<a href="../">Go back</a>]'
echo '[<a href="history/">Video History</a>]'

# Input
echo "<form method=GET action=\"${SCRIPT}\">"
echo "<label for='video'>Video Link (<a href='https://rg3.github.io/youtube-dl/supportedsites.html' target='_blank'>sites</a>): </label>"
echo "<input type='text' name='video' size=45 value=''>"
echo "<br><input type='submit' value='Process'>"
echo "</form>"

echo "<form method=POST action=\"${SCRIPT}\" enctype="multipart/form-data">"
echo "<label for='file'>Upload File: </label>"
echo "<input type='file' name='file'>"
echo "<br><input type='submit' value='Process'>"
echo "</form>"


# Output
if test ! -f "history/$file"; then
  echo "<pre>"
  test -n "$video" && download_file
  test "$REQUEST_METHOD" = "POST" && upload_file
  echo "</pre>"
fi

if test -f "history/$file"; then
  # Info
  echo "<h5>"
  echo "<a>Size: $(du -sh "history/$file" 2>&1)</a>"
  echo "<a href='../?file=$PWD/history/$file'>edit</a><br>"
  echo "<img src='history/$thumb' width=45%><br>"
  #echo "<img src='data:image/png;charset=utf-8;base64,$(ffmpeg -ss 2 -i "$file" -t 1 -f image2pipe -vcodec ppm - | convert - png:- | base64)' width=45%><br>"
  echo "</h5>"
fi


echo '</article>'
echo '</body>'
echo '</html>'
