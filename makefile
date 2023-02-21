init-db:
	#build docker container for a postgres

start-server:
	uvicorn app.main:app --reload
