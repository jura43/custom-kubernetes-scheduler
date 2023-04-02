import time
import random
import json
from kubernetes import client, config, watch

config.load_kube_config()
v1 = client.CoreV1Api()
schedulerName = "hascheduler"
print("Waiting for pods in queue...")

# Fetch available and ready nodes
def get_nodes():
    ready_nodes = []
    for n in v1.list_node(label_selector="node=worker").items:
        if n.spec.unschedulable == None:
            for status in n.status.conditions:
                if status.status == "True" and status.type == "Ready":
                    ready_nodes.append(n.metadata.name)


    return ready_nodes

# Function for determing best node for scheduling new pod
def select_node(ready_nodes):
 # Array of pods on a node
    nodes_with_pods = {}    # Dictionary of pods on a node
    n = len(ready_nodes) - 1 # Ready node counter

    while n > -1:
        pods_in_namespace = [] 
        node_selector = 'spec.nodeName=' + ready_nodes[n]
        pods=(v1.list_namespaced_pod("default", label_selector="scheduler=hascheduler", field_selector=node_selector, watch=False))
        for pod in pods.items:
            pods_in_namespace.append(pod.metadata.name)

        nodes_with_pods[ready_nodes[n]] = len(pods_in_namespace)
        n -= 1

    sorted_nodes = sorted(nodes_with_pods.items(), key=lambda item: item[1], reverse=False) # Arranging node by number of running pods
    nodes_suitable = sorted_nodes[0][0] # Selected node for scheduling next pod

    return nodes_suitable

# Binding of pod to the node
def scheduler(name, node, namespace="default"):

    body=client.V1Binding()
    target=client.V1ObjectReference()
    
    target.kind="Node"
    target.apiVersion="v1"
    target.name=node

    meta=client.V1ObjectMeta()
    meta.name=name

    body.target=target
    body.metadata=meta
    body.metadata.annotations={schedulerName:"scheduled"}

    return v1.create_namespaced_binding(namespace, body, _preload_content=False)

# Waiting for new pods
def main():
    w = watch.Watch()
    for event in w.stream(v1.list_namespaced_pod, "default"):
        if event['type'] == "ADDED" and event['object'].status.phase == "Pending" and event['object'].spec.scheduler_name == schedulerName:
            try:
                nodes=get_nodes()
                print(nodes)
                res = scheduler(event['object'].metadata.name, select_node(nodes))
                print("Node %s is chosen for pod %s" % (select_node(nodes), event['object'].metadata.name))
            except client.rest.ApiException as e:
                print (e)


if __name__ == '__main__':
    main()