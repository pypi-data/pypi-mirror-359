#!/bin/bash
## Do not put any commands or blank lines before the #SBATCH lines
#SBATCH --nodes=8                   # Number of nodes - all cores per node are allocated to the job
#SBATCH --time=00:00:00             # Wall clock time (HH:MM:SS) - once the job exceeds this time, the job will be terminated (default is 5 minutes)
#SBATCH --account= XXXXXXX          # (optional, organization dependant)
#SBATCH --job-name=progress         # Name of job
#SBATCH --partition=batch           # partition/queue name: short or batch (optional, organization dependant)
                                    #            short: 4hrs wallclock limit
                                    #            batch: nodes reserved for > 4hrs (default)
#SBATCH --qos=normal                # Quality of Service: long, large, priority or normal (optional, organization dependant)
                                    #           normal: request up to 48hrs wallclock (default)
                                    #           long:   request up to 96hrs wallclock and no larger than 64nodes
                                    #           large:  greater than 50% of cluster (special request)
                                    #           priority: High priority jobs (special request)

nodes=$SLURM_JOB_NUM_NODES           # Number of nodes - the number of nodes you have requested (for a list of SLURM environment variables see "man sbatch")
cores=36                             # Number MPI processes to run on each node (a.k.a. PPN)
                                     # No. of cores per node will vary
# using openmpi-intel/1.10
export PATH=$PATH:$HOME//path/to/anaconda3/version/bin ## Add any required binaries to the PATH environment variable
source activate progress ## Activate the required anaconda environment (if any)
scontrol show job $SLURM_JOB_ID ### write job information to output file
# conda deactivate ## Deactivate the previously activated anaconda environment (if any)
mpiexec --bind-to core --npernode $cores --n $(($cores*$nodes)) python /path/to/mult_proc_example_simulation.py

# Note 1: This will start ($nodes * $cores) total MPI processes using $cores per node.  
#           If you want some other number of processes, add "-np N" after the mpiexec, where N is the total you want.
#           Example:  mpiexec -np 44  ......(for a 2 node job, this will load 36 processes on the first node and 8 processes on the second node)
#           If you want a specific number of process to run on each node, (thus increasing the effective memory per core), use the --npernode option.
#           Example: mpiexec -np 24 --npernode 12  ......(for a 2 node job, this will load 12 processes on each node)

# For openmpi 1.10: mpiexec --bind-to core --npernode 8 --n PUT_THE_TOTAL_NUMBER_OF_MPI_PROCESSES_HERE /path/to/executable [--args...]

# To submit your job, do:
# sbatch <script_name>
#
#The slurm output file will by default, be written into the directory you submitted your job from  (slurm-JOBID.out)
