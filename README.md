# Group-15-Project-VI

# RUNNING THE APP

- The app currently runs on port 5000 (subject to change)
- To run the app using the provided Dockerfile, first open a terminal inside the directory of the project on your local machine

## With terminal open, enter the following:##

- docker build -t <insert_name_of_choosing> .
- docker run -p 5000:5000 <insert_name_of_choosing>
- Proceed to the localhost at http://127.0.0.1:5000/

- docker run -d --name planner_app -p 5000:5000 planner_flask
- docker compose down
- docker compose up -d --build

- to demo OPTIONS, use curl -i -X OPTIONS http://localhost:5000/booking
- -X OPTIONS forces http request type, -i includes http response headers in output