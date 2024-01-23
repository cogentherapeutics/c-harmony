SHELL=/bin/bash
PYTHON=export PYTHONPATH=. && python3
# Options: blue green production edge development
ENV?="development"



instructions:
	@echo "Run the appropriate command for desired behavior."
	@echo 'make init'
	@echo 'make populate'

	@echo 'make install'
	@echo 'make install-dev'
	@echo 'make format'
	@echo 'make static-analysis'
	@echo 'make test'

	@echo 'make build'
	@echo 'make dev'
	@echo 'make creds'
	@echo 'make attach'
	@echo 'make local-dev'

	@echo 'make ecr'
	@echo 'make pull'
	@echo 'make push'

	@echo 'make register ENV=?'
	@echo 'make create-iam ENV=?'
	@echo 'make create ENV=?'
	@echo 'make update ENV=?'
	@echo 'make delete ENV=?'
	@echo 'make delete-iam ENV=?'
	@echo 'make status ENV=?'
	@echo 'make launch ENV=?'
	@echo 'make schedule ENV=?'
	@echo 'make unschedule ENV=?'

	@echo 'make quick-start ENV=?'
	@echo 'make deploy ENV=?'
	@echo 'make clean ENV=?'



init:
	pipenv run \
		catalyst init pipeline harmony

populate:
	pipenv run \
		catalyst populate pipeline



install:
	pipenv uninstall --all
	pipenv install

install-dev:
	pipenv uninstall --all
	pipenv install --dev

format:
	pipenv run black src/harmony tests
	pipenv run flake8 src/harmony tests

static-analysis:
	pipenv run \
		mypy \
			--ignore-missing-imports \
			--check-untyped-defs \
			src/harmony \
			tests

test: FORCE
	pipenv run coverage run -m pytest tests
	pipenv run coverage report



build: FORCE
	@cat pyproject.toml \
	| grep version \
	| cut -d' ' -f3 \
	| sed 's/"//g' > VERSION
	@version=$$(cat VERSION); \
	cat templates/compose.yaml.ac \
	| sed -e "s/<<<VERSION>>>/$$version/" \
		> build/compose.yaml
	aws ecr get-login-password \
		--region us-east-1 \
	| docker login \
		--username AWS \
		--password-stdin 867910344731.dkr.ecr.us-east-1.amazonaws.com; \
	docker compose --file build/compose.yaml build

dev:
	docker compose --file build/compose.yaml up

creds:
	aws sts assume-role \
		--role-arn arn:aws:iam::867910344731:role/ECSTaskHarmonyProduction \
		--role-session-name ecstaskharmonyproduction \
	| jq '{ \
		access_key_id: .Credentials.AccessKeyId, \
		secret_access_key: .Credentials.SecretAccessKey, \
		session_token: .Credentials.SessionToken \
	} \
	| "[default]", \
		"aws_access_key_id = " + .access_key_id, \
		"aws_secret_access_key = " + .secret_access_key, \
		"aws_session_token = " + .session_token' \
		--raw-output \
		> ~/.aws/ecstaskharmonyproduction-credentials
	docker exec harmony mkdir -p /root/.aws
	docker cp \
		~/.aws/ecstaskharmonyproduction-credentials \
		harmony:/root/.aws/credentials

attach:
	docker exec -it harmony bash

local-dev:
	pipenv run python src/harmony/instrumentation.py development



ecr:
	aws ecr get-login-password \
		--region us-east-1 \
	| docker login \
		--username AWS \
		--password-stdin 867910344731.dkr.ecr.us-east-1.amazonaws.com

pull:
	docker compose --file build/compose.yaml pull

push:
	docker compose --file build/compose.yaml push



register:
	pipenv run \
		catalyst pipeline register \
			--environment $(ENV)

create-iam:
	pipenv run \
		catalyst pipeline create-iam \
			--environment $(ENV)

create:
	pipenv run \
		catalyst pipeline create \
			--environment $(ENV)

update:
	pipenv run \
		catalyst pipeline update \
			--environment $(ENV)

delete:
	pipenv run \
		catalyst pipeline delete \
			--environment $(ENV)

delete-iam:
	pipenv run \
		catalyst pipeline delete-iam \
			--environment $(ENV)

status:
	pipenv run \
		catalyst pipeline status \
			--environment $(ENV)

launch:
	pipenv run \
		catalyst pipeline launch \
			--environment $(ENV)

schedule:
	pipenv run \
		catalyst pipeline schedule \
			--environment $(ENV)

unschedule:
	pipenv run \
		catalyst pipeline unschedule \
			--environment $(ENV)



quick-start:
	make build
	make push
	make register ENV=$(ENV)
	make create-iam ENV=$(ENV)
	make create ENV=$(ENV)
	make schedule ENV=$(ENV)

deploy:
	make build
	make push
	make register ENV=$(ENV)
	make update ENV=$(ENV)

clean:
	make unschedule ENV=$(ENV)
	make delete ENV=$(ENV)
	make delete-iam ENV=$(ENV)



FORCE:

