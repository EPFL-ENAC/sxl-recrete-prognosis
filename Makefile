generate-selfsigned-cert:
	$(eval UID := $(shell id -u))
	$(eval GID := $(shell id -g))
	cd cert && OWNER="${UID}.${GID}" docker compose up --remove-orphans

generate-selfsigned-cert-win:
	cd cert && \
	copy NUL certificate.crt && \
	copy NUL certificate.key && \
	docker compose up --remove-orphans

install:
	pip install -r requirements.txt

dev:
	streamlit run  app/app.py

run:
	docker compose down --remove-orphans
	docker compose build --pull
	docker compose up -d --remove-orphans
