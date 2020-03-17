setup:
	python3 -m venv ~/.DSBA-6190_Proj4

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	#python -m pytest -vv --cov=myrepolib tests/*.py
	#python -m pytest --nbval wine_predict/wine_quality_predict.ipynb

lint:
	pylint --disable=R,C,W1202,E1101 scripts/*.py
	 
all: 
	install lint test