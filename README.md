# Kubernetes Example Datadog Monitoring Project


This repo is a **WORK IN PROGRESS**. It will contain a basic example of how to set up and monitor a kubernetes application with Datadog.

## Getting Started 

First, start up minikube:

```bash
$ minikube start
```

Next, add the Datadog API key as a secret in kubernetes:

```bash
$ kubectl create secret generic datadog-api --from-literal=token=<YOUR_DATADOG_API_KEY>
```

Finally, apply the kubernetes template so we have Datadog installed and running as a DaemonSet:

```bash
$ kubectl apply -f datadog-agent.yaml
```

Note this `yaml` file pulls our secret automatically, and enables APM and logs. Once we've run this command, we should be able to log into Datadog and see our minikube virtual machine as a host in Datadog.

If you don't see it show up, ensure you've copied and pasted the proper Datadog API key.

## Running the Application

If you're running this repo in minkube, you'll need to first give minikube access to the local Docker images. You can do this via a:

```bash
$ eval $(minikube docker-env)
```

With this, you're then be able to build Docker images locally, and pull them with the included yaml files. 

Here, we assume you're in the repo's top level directory to build the Postgres image:

```bash
$ docker build -t sample_postgres:latest ./postgres/
$ kubectl apply -f postgres_deploy.yaml
```

And you can check to see that everything went well:

```bash
$ $ kubectl get pods
NAME                        READY     STATUS    RESTARTS   AGE
datadog-agent-5hs6s         1/1       Running   0          2d
postgres-59f87896b6-hnjtp   1/1       Running   0          1m
```
