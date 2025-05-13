run:
	docker compose up

run-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.ics_hullm up

down-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down


# Push all docker images to 'scm.cms.hu-berlin.de:4567/iqb-lab/ics'
include .env.ics-hullm
push-iqb-registry:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.ics-hullm build
	docker login scm.cms.hu-berlin.de:4567
	docker push $(REGISTRY_PATH)ics-hullm-backend:$(TAG)
	docker push $(REGISTRY_PATH)ics-hullm-worker:$(TAG)
	docker logout
