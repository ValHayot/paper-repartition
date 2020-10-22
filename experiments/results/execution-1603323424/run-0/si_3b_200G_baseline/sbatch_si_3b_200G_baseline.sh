#!/bin/bash
#SBATCH --account=vhs
#SBATCH --job-name=si_3b_200G_baseline
#SBATCH --nodes=1
#SBATCH --mem=200000
#SBATCH --output=/home/vhs/paper-repartition/experiments/results/execution-1603323424/run-0/si_3b_200G_baseline/slurm-%x-%j.out


rm -rf /disk0/vhs/repartition
mkdir /disk0/vhs/repartition
cd /disk0/vhs/repartition


echo "Clearing cache" && sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
source /home/vhs/paper-repartition/.venv/bin/activate
export KEEP_LOG=/home/vhs/paper-repartition/experiments/results/execution-1603323424/run-0/si_3b_200G_baseline/logs.csv


repartition --max-mem 200000000000 --create  "(3500, 3500, 3500)" "(700, 700, 700)" "(350, 350, 350)" baseline

/usr/bin/time -o /home/vhs/paper-repartition/experiments/results/execution-1603323424/run-0/si_3b_200G_baseline/runtime.txt -v repartition --max-mem 200000000000 --repartition "(3500, 3500, 3500)" "(700, 700, 700)" "(350, 350, 350)" baseline
repartition --max-mem 200000000000 --delete "(3500, 3500, 3500)" "(700, 700, 700)" "(350, 350, 350)" baseline


echo "Removing directories"
rm -rf /disk0/vhs/repartition