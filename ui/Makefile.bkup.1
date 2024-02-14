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
	@echo 'make start'
	@echo 'make stop'

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
	@echo 'make restart ENV=?'

	@echo 'make quick-start ENV=?'
	@echo 'make deploy ENV=?'
	@echo 'make clean ENV=?'



init:
	pipenv run \
		catalyst init application harmony-ui

populate:
	pipenv run \
		catalyst populate application



install:
	pipenv uninstall --all
	pipenv install

install-dev:
	pipenv uninstall --all
	pipenv install --dev

format:
	pipenv run black src/harmony_ui tests
	pipenv run flake8 src/harmony_ui tests

static-analysis:
	pipenv run \
		mypy \
			--ignore-missing-imports \
			--check-untyped-defs \
			src/harmony_ui \
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
		--role-arn arn:aws:iam::867910344731:role/ECSTaskHarmonyUiProduction \
		--role-session-name ecstaskharmonyuiproduction \
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
		> ~/.aws/ecstaskharmonyuiproduction-credentials
	docker exec harmony-ui mkdir -p /root/.aws
	docker cp \
		~/.aws/ecstaskharmonyuiproduction-credentials \
		harmony-ui:/root/.aws/credentials

attach:
	docker exec -it harmony-ui bash

local-dev:
	pipenv run \
		streamlit run \
			--browser.gatherUsageStats false \
			--browser.serverAddress localhost \
			--server.port 9717 \
			--server.baseUrlPath "/harmony-ui" \
			--theme.primaryColor="#97C5AB" \
			--theme.base light \
			src/harmony_ui/Welcome.py

start:
	docker exec \
		harmony-ui \
		streamlit run \
			--browser.gatherUsageStats false \
			--browser.serverAddress localhost \
			--server.port 9717 \
			--server.baseUrlPath "/harmony-ui" \
			--theme.primaryColor="#97C5AB" \
			--theme.base light \
			/root/src/harmony_ui/Welcome.py

stop:
	docker exec --detach harmony-ui bash -c 'kill `pgrep -f harmony-ui`'



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
		catalyst application register \
			--environment $(ENV)

create-iam:
	pipenv run \
		catalyst application create-iam \
			--environment $(ENV)

create:
	pipenv run \
		catalyst application create \
			--environment $(ENV)

update:
	pipenv run \
		catalyst application update \
			--environment $(ENV)

delete:
	pipenv run \
		catalyst application delete \
			--environment $(ENV)

delete-iam:
	pipenv run \
		catalyst application delete-iam \
			--environment $(ENV)

status:
	pipenv run \
		catalyst application status \
			--environment $(ENV)

restart:
	pipenv run \
		catalyst application restart \
			--environment $(ENV)



quick-start:
	make build
	make push
	make register ENV=$(ENV)
	make create-iam ENV=$(ENV)
	make create ENV=$(ENV)

deploy:
	make build
	make push
	make register ENV=$(ENV)
	make update ENV=$(ENV)
	make restart ENV=$(ENV)

clean:
	make delete ENV=$(ENV)
	make delete-iam ENV=$(ENV)



FORCE:

