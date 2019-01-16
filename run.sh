#! /bin/bash

export CMD="python program.py"

for INSTANCE in i2 i3 i4 i5 ; do
    mkdir -p output/${INSTANCE}
    ${CMD} -timeout 600 -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file data/${INSTANCE}/student.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > out.txt
    mv out.csv output/${INSTANCE}/output10.csv
    mv out.txt output/${INSTANCE}/out10.txt
    ${CMD} -timeout 1800 -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file data/${INSTANCE}/student.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > out.txt
    mv out.csv output/${INSTANCE}/output30.csv
    mv out.txt output/${INSTANCE}/out30.txt
    ${CMD} -timeout 3600 -award-activity "1,2,4" -award-student 1 -minmax-penalty 1 -students-file data/${INSTANCE}/student.csv -requests-file data/${INSTANCE}/requests.csv -overlaps-file data/${INSTANCE}/overlaps.csv -limits-file data/${INSTANCE}/limits.csv > out.txt
    mv out.csv output/${INSTANCE}/output60.csv
    mv out.txt output/${INSTANCE}/out60.txt
done