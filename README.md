<div align="center">
    <h1> Koroghlu </h1>
    <div style="font-style: italic">
        Koroghlu is a repository for preparing artifacts for conferences using Docker tools.
    </div>
</div>

<p align="center">
  <img alt="logo" src="./docs/cover.jpg" width="30%" height="auto"/>
</p>

<p align="center">
  <a href="https://github.com/lac-dcc/koroghlu/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-GPL%203.0%20only-green?style=for-the-badge" alt="License: GPL v3"></a>
  <a href="https://github.com/lac-dcc/koroghlu/commits/main">
    <img src="https://img.shields.io/github/last-commit/lac-dcc/koroghlu/main?style=for-the-badge"
         alt="Last update">
  </a>
</p>

## **Contents Table**

* [Introduction](#introduction)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Setup](#setup)
    * [Running](#running)
* [Structure](#structure)
* [Technical Report](#technical-report)

---
<a id="introduction"></a>

## **Introduction**


The pursuit of scientific knowledge strongly depends on the ability to reproduce and validate research results. It is a well-known fact that the scientific community faces challenges related to transparency, reliability, and the reproducibility of empirical published results. Consequently, the design and preparation of reproducible artifacts has a fundamental role in the development of science. Reproducible artifacts comprise comprehensive documentation, data, and code that enable replication and validation of research findings by others. In this work, we discuss a methodology to construct reproducible artifacts based on Docker.
Our presentation centers around the preparation of an artifact to be submitted to a scientific venues that encourages or requires this process.
This report's primary audience are scientists working with empirical computer science; however, we believe that the presented methodology can be extended to other technology-oriented empirical disciplines.

---
<a id="getting-started"></a>

## **Getting Started**

In this section are the steps to reproduce our experiments.

### **Prerequisites**

You need to install the following packages to run this project:

* [Docker](https://www.docker.com/get-started/) and [Docker Compose](https://docs.docker.com/compose/install/) to run our experiments

<a id="setup"></a>

###  **Setup**

The Docker Command Line Interface (CLI) is a suite of commands that
let users build containers through the prompt of an operating system's terminal.
The following steps build a docker image with everything necessary to reproduce the
experiment using the command line interface of Docker:

Install the docker tool following the official documentation [Available in this link](https://docs.docker.com/engine/install/).
As an example, on Linux or in the Windows WSL the following command should be enough:

```
$ sudo apt install docker.io
```

On OSX, the following command could be used instead:

```
$ brew install docker
```

Download the code necessary to run the experiment described in GitHub:

```
$ git clone https://github.com/lac-dcc/koroghlu
```

Move onto the koroghlu folder, which contains the build scripts:

```
$ cd koroghlu/
```

Build a docker image by running the command below within the koroghlu folder.
This command builds an image from a ``docker file", whose access path is specified with the \texttt{-f} tag (Estimated build time: 10 minutes on an Intel machine with 2.8GHz of clock):

```
$ docker build -t docker-artifact -f docker/Dockerfile.x86 .
```

The previous command builds a docker image with the ``tag'' docker-artifact (specified after the -t flag). The tag is a name (of our own choice) that we shall use to refer to this image in other commands.

Remark: The Docker daemon accesses a Unix socket owned by the root user. Thus, depending on privileges, users might have to run docker commands as sudo. To avoid prefacing the docker command with sudo, create a Unix group called docker. Users in this group will be able to run docker without root access. To follow this path, do:

```
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
```

At the end of this forth step, a docker image is created. This image follows the specifications given in the docker file Dockerfile.x86. This file is the core of the artifact.

<a id="running"></a>

### **Running**

Once a docker image is built with the tag name "docker-artifact", run the artifact that this image contains with the following command:

```
$ docker run -ti -v ${PWD}/results:/root/koroghlu/results docker-artifact
```

In the docker prompt, execute the command below to reproduce the experiments (Estimated running time: 5 minutes on an Intel machine with 2.8GHz of clock.

```
$ ./run.sh x86
```

Once the run.sh script terminates, we must have results ready to be analyzed in the results folder. We can exit the docker container and enter that folder to check out the results that we have reproduced:

```
$ root@f1258685f4fd:~/koroghlu# exit
$ cd results/
$ cat results.csv
  Turning,time(ms),std(ms),Space search(s),tile_i,tile_j,tile_k,order
  GridSearchTuner,1.0928,0.0589,103.33
  RandomTuner,0.6074,0.0000,95.20,64,1,16,jki
  GATuner,0.1129,0.0004,69.99,1,80,1,jki
  XGBTuner,0.3067,0.0002,84.30,16,48,64,jki
$ ls *.pdf
  x86_tuning.pdf
```

At the end of the third step above, we must have a PDF figure in the results folder: x86\_tuning.pdf.
This figure should be similar to figure below: it represents the ``scientific result" produced by our artifact.
Notice that the same artifact can be used to produce several different scientific results.
A good practice is to have a separate script (like our run.sh above) to reproduce each one of these results.

<p align="center">
  <img alt="logo" src="./docs/x86_tuning.png" width="50%" height="auto"/>
</p>

---
<a id="technical-report"></a>

## Technical Report

This framework is used in the following published papers:

TODO: in submission the paper.
