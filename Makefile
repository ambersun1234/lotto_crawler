SHELL := /bin/bash

install:
	sudo apt install python3-pip -y
	sudo pip3 install virtualenv
	virtualenv env
	
package:
	pip3 install -r ./requirements.txt

