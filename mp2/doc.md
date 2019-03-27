# cs425-spring19-mp2 Report

Please submit CP1 using Gradescope. Your submission should include the following information:

You should then have a description of the design of your MP2. Your description should explain:

- How your nodes keep connectivity; how they discover nodes beyond the originally introduced ones, and how they detect failed nodes. **You should justify why you think your design is robust to failures.**
- How transactions are propagated. Describe the algorithm you are using, any parameters and how you arrived at them.
- What information is logged and how you used this to generate the graphs. Please make sure that the logs you used in your experiments are checked into the git repository. If you wrote any scripts to analyze the logs please include them in the repo and describe how they work.

As a guideline, each of the three points above should be one or two paragraphs.

Finally, you should have the graphs of transaction propagation and bandwidth from the experiments described above.

## Group

- mttsao2
- stoehr2 

## VM Cluster: 58

## Gitlab Repository

https://gitlab.engr.illinois.edu/mttsao2/cs425-sp19/tree/master/mp2

## How to Run the Code

1. Run the service `python36 mp2_service.py [SERVICE_PORT] [TX_RATE]`

2. Run our code: `python36 main.py [NUM_NODES_ON_THIS_VM] [SERVICE_IP] [SERVICE_PORT]`

e.g. `python36 main.py 2 sp19-cs425-g58-01.cs.illinois.edu 1111`

## Commit Hash

[I'm the commit hash]

## Design Document

### Node connectivity

At the appearnace of an "Introduce" command from the service, the ip and port will be added to the list of live addresses, `liveAddresses`. 

When "Introduce" messages are received from other nodes, they are placed onto the `unknownAddresses` list.


Once Then the node adds these address to `pending address list` and wait for their responses. Once it got the reply, it adds the address to `live address list`.

Please refer to:

```
{node.py}
class Node(Thread):
    ...
    def handleMessage(self, message, addr):
        ...
    def run(self):
        ...
        ## NODE STUFF
        ...
```

### Transaction broadcast

Every round, each node picks up to three nodes from its `liveAddresses` list, and up to 2 nodes from the `unknownAddresses` list.

For each of these addresses (ip,port) pair,  

1. 5 latest transactions
2, 
2. 3 addresses from `liveAddresses` list
3. 2 addresses from `unknownAddresses` list

Every round a node randomly chooses 3 nodes from the `live address list` and sends recent 5 transactions to them. 

Please refer to:

```
{node.py}
class Node(Thread):
    ...
    def run(self):
        ...
        ## Figure out which addresses to send to
        ...
        ######## WRITE TO OTHER NODES
        ...
```

### Failure handling

If half of nodes fail, every round, in average, a node successfully sends recent transactions to 1.5 nodes. At round clog(n), the infected node number y ~ (n+1) - 1/n^(cb-2). Where n+1 is the total population of nodes. The situation with all nodes alive (b=3) and half nodes alive (b=1.5) is as follows:

| c   | b    | round  |formula of y      | ~y            |
| --- |:----:|:------:|:----------------:|--------------:|
| 1   | 3    | log(n) |(n+1)-1/n^(3-2)   | (n+1)-1/n     |
| 1   | 1.5  | log(n) |(n+1)-1/n^(1.5-2) | (n+1)-n^0.5   |
| 2   | 3    | 2log(n)|(n+1)-1/n^(6-2)   | (n+1)-1/n^4   |
| 2   | 1.5  | 2log(n)|(n+1)-1/n^(3-2)   | (n+1)-1/n     |
| 3   | 3    | 3log(n)|(n+1)-1/n^(9-2)   | (n+1)-1/n^7   |
| 3   | 1.5  | 3log(n)|(n+1)-1/n^(4.5-2) | (n+1)-1/n^2.5 |

The propagation time is roughly doubled when half nodes die in comparison to all nodes alive.

### Node termination

Please refer to:

```
{node.py}
class Node(Thread):
    def handleServiceMessage(self, message):    
```

## Analysis

### Transaction propagation completed

### Propagation Speed

- Propagation 50:

![Plot 1](img/plot01_hist_propagation_delay_half.png "Plot 1")

- Propagation completed:

![Plot 2](img/plot02_hist_propagation_delay_all.png "Plot 2")

- Transaction Propagation:

Nodes: 20

![Plot 3](img/plot03_line_tx_reached_20.png "Plot 3")

Nodes: 100

![Plot 4](img/plot04_line_tx_reached_100.png "Plot 4")

### Bandwidth

Nodes: 20

![Plot 5](img/plot05_line_bandwidth_20.png "Plot 5")

Nodes: 100

![Plot 6](img/plot06_line_bandwidth_100.png "Plot 6")
