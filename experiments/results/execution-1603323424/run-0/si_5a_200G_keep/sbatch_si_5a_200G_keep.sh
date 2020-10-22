#!/bin/bash
#SBATCH --account=vhs
#SBATCH --job-name=si_5a_200G_keep
#SBATCH --nodes=1
#SBATCH --mem=200000
#SBATCH --output=/home/vhs/paper-repartition/experiments/results/execution-1603323424/run-0/si_5a_200G_keep/slurm-%x-%j.out


rm -rf /disk0/vhs/repartition
mkdir /disk0/vhs/repartition
cd /disk0/vhs/repartition


echo "Clearing cache" && sync && echo 3 | sudo tee /proc/sys/vm/drop_caches
source /home/vhs/paper-repartition/.venv/bin/activate
export KEEP_LOG=/home/vhs/paper-repartition/experiments/results/execution-1603323424/run-0/si_5a_200G_keep/logs.csv


repartition --max-mem 200000000000 --create  "(3500, 3500, 3500)" "(350, 350, 350)" "(250, 250, 250)" keep

/usr/bin/time -o /home/vhs/paper-repartition/experiments/results/execution-1603323424/run-0/si_5a_200G_keep/runtime.txt -v repartition --max-mem 200000000000 --repartition "(3500, 3500, 3500)" "(350, 350, 350)" "(250, 250, 250)" keep
repartition --max-mem 200000000000 --delete "(3500, 3500, 3500)" "(350, 350, 350)" "(250, 250, 250)" keep


echo "Removing directories"
rm -rf /disk0/vhs/repartition