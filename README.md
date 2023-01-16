# FireGroup Testing
A simple API to update Launch Configuration in Auto Scaling Group with new AMI.
## How to use
### Install
We just need to build and run Dockerfile
```
docker build -t <image_name>:<image_tag> .
docker run -d -p 5000:5000 --name container_name -e ACCESS_KEY=<access_key> -e SECRET_KEY=<secret_key> -e REGION=<region> <image_name>:<image_tag>
```
after that, to using it we can access:
- http://localhost:5000 to show list of our asg.
- http://localhost:5000/updateasg?asg_name=<asg_name> to create new lc with new ami and update lc on asg.
## CI/CD
### With CI
We can using Github Action or Jenkins to create a pipeline include some steps below:
- Pull new code when we has new commit or merge into master branch
- Checking syntax our code and Dockerfile
- Run unit test if we have
- Build and push docker image to docker hub, ECR or our private docker registry
### With CD
We can use ArgoCD as tool for CD process, but need to prepare some stuff for that:
- First, we need to create a repo to save our manifests (helm or kustomize) of kubernetes.
- Second, with our simple api, we just need to create some simple resources like deployment, services, ingress.
- Create Application resource for ArgoCD to update and deploy our manifests whenever we update config on manifests repo