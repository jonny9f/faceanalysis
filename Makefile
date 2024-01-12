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

build_lambda: $(DOCKERFILE_PATH) $(BUILD_CONTEXT_DIR)
	docker build -f Dockerfile_lambda --tag 302605622298.dkr.ecr.eu-west-2.amazonaws.com/faceanalysis:latest $(BUILD_CONTEXT_DIR)

push_ecr: build_lambda
	aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 302605622298.dkr.ecr.eu-west-2.amazonaws.com
	docker push 302605622298.dkr.ecr.eu-west-2.amazonaws.com/faceanalysis:latest

test_lambda: build_lambda
	docker run  -v ~/.aws-lambda-rie:/aws-lambda -p 9000:8080 --entrypoint /aws-lambda/aws-lambda-rie \
    302605622298.dkr.ecr.eu-west-2.amazonaws.com/faceanalysis:latest \
        python -m awslambdaric serve.handler
