""" Code for running the Smiley experiment.
"""
# import some libraries
from experiment import Experiment
import task
import post_task

# ---------------- SETUP --------------------
# Make an Experiment object to store the experiment info
experiment = Experiment()

# ---------------- MAIN PROGRjAM --------------------

# Run task
task.run(experiment)

# Run post-task
post_task.run(experiment)

# cleanup
experiment.close()
