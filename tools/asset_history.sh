asset_file="$1"
awk '{line+=1}/^    -/{end=line-1; if(start > 0){print start "," end}; count+=1;start=line;}END{print start "," line}' "$asset_file" | while read line; do
    size=`echo $line | awk -F, '{print $2-$1+1}'`
    end=`echo $line | awk -F, '{print $2}'`
    name=`head -n $end "$asset_file" | tail -n $size | python -c 'import yaml,sys; print yaml.load(sys.stdin)[0]["name"]'`
    date=`git blame -w -L $line "$asset_file" | sed 's/^[^(]*(\([^)]*\)).*/\1/' | python -c 'import sys,dateutil.parser; print max([dateutil.parser.parse("%s %s%s"%(j[0], j[1], j[2])) for j in [i.split()[-4:] for i in sys.stdin.readlines()]])'`
    (echo $name; echo $date) | python -c 'import sys,json,yaml; print yaml.dump([i.strip() for i in sys.stdin.readlines()]),'
done | python -c 'import sys,yaml; print yaml.dump({"assets":dict([[j[0], {"last_modified":j[1]}] for j in [yaml.load(i) for i in sys.stdin.readlines()]])}),'
