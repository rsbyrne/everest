SCRIPT=$1
N=$2
LOGSDIR="./logs"
OUTFILE=$LOGSDIR"/"$SCRIPT".out"
ERRORFILE=$LOGSDIR"/"$SCRIPT".error"
touch $OUTFILE
touch $ERRORFILE
for i in $(seq 1 $N)
do python $SCRIPT $OUTFILE 2> $ERRORFILE &
done
