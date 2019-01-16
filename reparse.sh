#! /bin/bash

export CMD1="python reparse.py"
export CMD2="python evaluator.py"

for INSTANCE in i2 i3 i4 i5 ; do
    ${CMD1} -students-file output/${INSTANCE}/output10.csv
    mv r_output.csv output/${INSTANCE}/r_output10.csv

    ${CMD1} -students-file output/${INSTANCE}/output30.csv
    mv r_output.csv output/${INSTANCE}/r_output30.csv

    ${CMD1} -students-file output/${INSTANCE}/output60.csv
    mv r_output.csv output/${INSTANCE}/r_output60.csv
done

for INSTANCE in i2 i3 i4 i5 ; do

    ${CMD2} -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file output/${INSTANCE}/output10.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > s1.txt
    ${CMD2} -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file output/${INSTANCE}/r_output10.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > s2.txt

    if cmp -s s1.txt s2.txt; then
        printf '"%s 10min - PASSED"\n' "$INSTANCE"
    else
        printf '"%s 10min - FAIL"\n' "$INSTANCE"
    fi

    ${CMD2} -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file output/${INSTANCE}/output30.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > s1.txt
    ${CMD2} -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file output/${INSTANCE}/r_output30.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > s2.txt

    if cmp -s s1.txt s2.txt; then
        printf '"%s 30min - PASSED"\n' "$INSTANCE"
    else
        printf '"%s 30min - FAIL"\n' "$INSTANCE"
    fi

    ${CMD2} -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file output/${INSTANCE}/output60.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > s1.txt
    ${CMD2} -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file output/${INSTANCE}/r_output60.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > s2.txt

    if cmp -s s1.txt s2.txt; then
        printf '"%s 60min - PASSED"\n' "$INSTANCE"
    else
        printf '"%s 60min - FAIL"\n' "$INSTANCE"
    fi
done

rm s1.txt
rm s3.txt