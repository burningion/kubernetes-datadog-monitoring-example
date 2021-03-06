# Kubernetes Example Datadog Monitoring Project


This repo contains a basic example of how to set up and monitor a kubernetes application with Datadog.

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

With this, you're then be able to build Docker images locally, and pull them with the included yaml files. Note that if you restart your computer, or open another shell, you will need to re-enter the above command to link the locally built containers.

If you try rebuilding your container, and don't see changes, make sure you've run the above command, followed by rebuilding your containers. You can then delete the running pods to reinsert the newest container images into your cluster.

Here, we assume you're in the repo's top level directory to build the Postgres image:

```bash
$ docker build -t sample_postgres:latest ./postgres/
$ kubectl apply -f postgres_deploy.yaml
```

And you can check to see that everything went well:

```bash
$ kubectl get pods
NAME                        READY     STATUS    RESTARTS   AGE
datadog-agent-5hs6s         1/1       Running   0          2d
postgres-59f87896b6-hnjtp   1/1       Running   0          1m
```

Next, we can build and deploy the Flask application, and check to see its url:

```bash
$ docker build -t sample_flask:latest ./flask-app/
$ kubectl apply -f flask_deploy.yaml
$ kubectl get services
NAME         TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
flaskapp     NodePort    10.104.83.93    <none>        5005:31924/TCP   1d
kubernetes   ClusterIP   10.96.0.1       <none>        443/TCP          4d
postgres     ClusterIP   10.108.98.243   <none>        5432/TCP         2d
$ minikube service flaskapp --url
http://192.168.99.100:31924
```

Your url may be different than the one above. By clicking the URL, you should be able to access the Flask app from your host machine.

## Rebuilding the Container Images / Deploying Changes

In order to rebuild your containers, you just run the same `docker build` commands we did before. Kubernetes should pick up the changed images, but if you don't want to wait, it's easier to sometimes just delete the old pods. 

Here's a full example of how to build a new container, get the old pod names, and delete them so kubernetes pulls the latest versions:

```bash
$ docker build -t sample_flask:latest ./flask-app/
$ kubectl get pods
NAME                        READY     STATUS    RESTARTS   AGE
datadog-agent-fdkdg         1/1       Running   0          2h
flaskapp-8ddc88c8b-4pmdg    1/1       Running   0          15m
flaskapp-8ddc88c8b-wqhxq    1/1       Running   0          15m
postgres-59f87896b6-hnjtp   1/1       Running   0          2d
$ kubectl delete pod flaskapp-8ddc88c8b-4pmdg
pod "flaskapp-8ddc88c8b-4pmdg" deleted
$ kubectl delete pod flaskapp-8ddc88c8b-wqhxq
pod "flaskapp-8ddc88c8b-wqhxq" deleted
$ kubectl get pods
NAME                        READY     STATUS    RESTARTS   AGE
datadog-agent-fdkdg         1/1       Running   0          3h
flaskapp-8ddc88c8b-555jw    1/1       Running   0          38s
flaskapp-8ddc88c8b-h9rpr    1/1       Running   0          45s
postgres-59f87896b6-hnjtp   1/1       Running   0          2d
```

Note the pods are much younger than the old pods.
