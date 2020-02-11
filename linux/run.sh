SCRIPT=$1
N=$2
for i in $(seq 1 $N); do python $SCRIPT; done
