Your report should include the following information:

- The netids of the people in your group
- The number of your VM cluster
- The URL of your gitlab repository (e.g. https://gitlab.engr.illinois.edu/jsmith2/425-mp1
- Instructions for building and running your code. Note that the TAs will be running your code on your VMs but under their own accounts, so make sure the instructions do not depend on anything installed inside your home directory (or specify how to install it)
- The full commit hash of the revision that you want to be graded. You can see the revision on the command line with git rev-parse HEAD or in GitLab by selecting the "Copy SHA hash" button. Make sure to include the full 40-character hash, not the 8-character abbreviation GitLab displays.  

# cs425-spring19-mp1 Report

## Group

- mttsao2
- stoehr2 

## VM Cluster

We formed the group after we submmited the mp group form so we got our vms separately. The vms are 32 (mttsao2) & 58 (stoehr). We put the code on [vm#] currently.

## Gitlab Repository

## How to Run the Code

Please run: `Python mp1.py [name] [port] [# of users]`

e.g. `Python mp1.py Alice 4444 2`

## Commit Hash

[I'm the 40-charactorer hash]

## Design Document

### Reliability

#### Integrity

Every message received will be checked if already received by its sequence number. If the sequence number is seen, then drop the duplicate. If 

The 


#### Agreement

#### Validity

### Failure Detection

### Causal Ordering