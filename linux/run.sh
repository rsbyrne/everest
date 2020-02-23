SCRIPT=$1
N=$2
BASENAME=$(basename "$SCRIPT")
LOGSDIR="./logs"
mkdir -p $LOGSDIR
OUTFILE=$LOGSDIR"/"$BASENAME".out"
ERRORFILE=$LOGSDIR"/"$BASENAME".error"
touch $OUTFILE
touch $ERRORFILE
for i in $(seq 1 $N)
do python $SCRIPT 1> $OUTFILE 2> $ERRORFILE &
done
