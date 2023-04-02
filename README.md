# Custom scheduler for Kubernetes

## About

This is simple custom kubernetes scheduler written in Python. This script was written as part of my final thesis with which I graduated on undergraduate study at the Algebra University College.

## How it works?
Once running it is waiting for new unscheduled pods. When there is a pod that doesn't have assign node to run on scheduler starts gathering list of ready and available nodes in Kubernetes cluster. After gathering list of nodes, it starts finding most suitable node for running new pod. Node that has lowest running pods is chosen to run newly unscheduled pod.

## Findings
This is maybe simple scheduler with limited use case, but through my research I found that this custom scheduler can schedule big number of pods in shorter amount of time compared to default Kubernetes scheduler. This can be useful in clusters with homogeneous nodes where pods need to be started in shortest possible amount of time.

## How to use?
To use to scheduler run it on control node in Kubernetes cluster which must have installed Python interpreter (used with 3.9) and Python Kubernetes library.

## Issues
Due to some bugs in library I never managed to run this script inside pod. Also, there might be some updates to the Kubernetes, Python or some other component which my break this script.
