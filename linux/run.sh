SCRIPT=$1
N=$2
LOGSDIR="./logs"
mkdir -p $LOGSDIR
OUTFILE=$LOGSDIR"/"$SCRIPT".out"
ERRORFILE=$LOGSDIR"/"$SCRIPT".error"
touch $OUTFILE
touch $ERRORFILE
for i in $(seq 1 $N)
do python $SCRIPT 1> $OUTFILE 2> $ERRORFILE &
done
