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
