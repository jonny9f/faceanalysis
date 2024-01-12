DOCKER_TAG ?= jonny9f/faceanalysis:latest

# Path to the Dockerfile and the build context directory
DOCKERFILE_PATH = Dockerfile
BUILD_CONTEXT_DIR = .

build: $(DOCKERFILE_PATH) $(BUILD_CONTEXT_DIR)
	docker build --tag $(DOCKER_TAG) $(BUILD_CONTEXT_DIR)

push: build
	docker push $(DOCKER_TAG)

run: build
	docker run --rm -p 5000:5000 $(DOCKER_TAG) 

push_ecr: build
	aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/f2z2d6w2
	docker tag $(DOCKER_TAG) public.ecr.aws/f2z2d6w2/faceanalysis:latest
	docker push public.ecr.aws/f2z2d6w2/faceanalysis:latest

