run:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

up:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

logs:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f $(SERVICE)

run-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.ics-hullm up

up-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.ics-hullm up -d

down-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.ics-hullm down

logs-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.ics-hullm logs



# Push all docker images to 'scm.cms.hu-berlin.de:4567/iqb-lab/ics'
include .env.ics-hullm
push-iqb-registry:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.ics-hullm build
	docker login scm.cms.hu-berlin.de:4567
	docker push $(REGISTRY_PATH)ics-hullm-backend:$(TAG)
	docker push $(REGISTRY_PATH)ics-hullm-worker:$(TAG)
	docker logout
