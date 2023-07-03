run:
	docker-compose down --remove-orphans
	docker-compose build --pull
	docker-compose up -d --remove-orphans
