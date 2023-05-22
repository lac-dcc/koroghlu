docker-x86:
	docker build -t koroghlu -f Dockerfile.x86 .

x86-run:
	docker run -ti koroghlu

docker-arm:
	docker build -t koroghlu -f Dockerfile.arm .

arm-run:
	docker run -ti koroghlu

docker-cuda:
	docker build -t koroghlu -f Dockerfile.cuda .

cuda-run:
	docker run -it --gpus all koroghlu
