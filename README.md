#### Archive codebase of 2017-18 A-level CS Project
Infrary was a project to simplify management of cloud infrastructure needed to run containers in production on 2017. 

It worked with [DigitalOcean](https://digitalocean.com/) and BYO docker hosts. Docker and [Rancher](https://www.rancher.com/) were used to manage containers once the host VM or server were set up.

The project also included a small ODM with connectors for [MongoDB](https://www.mongodb.com/) and [GCP Datastore](https://cloud.google.com/datastore/) as well as a custom JSON validation layer.

Most of the functionality is now part of the core Rancher project.

> [How To Set Up Multi-Node Deployments With Rancher 2.1, Kubernetes, and Docker Machine on Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-multi-node-deployments-with-rancher-2-1-kubernetes-and-docker-machine-on-ubuntu-18-04)
