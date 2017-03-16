for i in *.mp4; do
#name=${i%.*}
name="${i/.mp4}"
link="${name##*-}"
thumb="$( printf "%s\n%s" ${name}* | grep -v mp4 )"
grep -s "$i" vids.log || printf "%s\t%s\t%s\t%s\n" "$( stat -c"%y" "$i" )" "https://www.google.com/search?q=${link}" "${thumb}" "${i}" >> vids.log
done
