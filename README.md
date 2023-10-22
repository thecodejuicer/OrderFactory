# Event-Driven Architechtures with Kafka and ksqlDB Demo

This repository was created for a demonstration at the 2023 Heartland Developer's Conference.

## Scenario

The demonstration scenario portrays a parent food corporation with three subsidaries. The child companies operate their
tech stack independently, but the parent corporation still wants visibility into all of their operations in one place.

Kafka plays a central role in making it all work together.

## Disclaimer

Because this was created for a demonstration it does not, necessarily, follow best practices in all areas. For example,
it does not include authentication. It was designed to give an idea of how one might go about designing an event-driven
architecture.

Also, all the example records in this repository (in the resources folder) are strictly fictitious. They were crated by
a test data generation tool.

## Usage

You will need Docker and Python 3.11. Earlier versions of Python 3 may work, but have not been tested.
Use the IDE of your choice. Visual Studio Code with the ksql extension is helpful. I happened to use PyCharm Community
Edition.

### Creating the environment.

I highly recommend adding a virtual environment for the Python project. venv works just fine. I had some issues with
Conda, so I don't recommend it for this demo. If you know how to make it work, go for it.

1. Run `docker compose up -d` from the root folder. It may take a long time for the first run. The Confluent docker
   images are rather large.
2. Once all the container appear to be running, open the kafka-ui web app at http://localhost:8080. Make sure the
   Dashboard lists the cluster as "Online."
3. Open a terminal and active the virtual environment if you're using it.
4. Install Python dependencies: `pip install -r requirements.txt`
5. Run `python src/kafka_setup.py`. That will create all the Kafka, ksqlDB and Connect objects.
6. Run `python src/the_producer.py`. This will begin simulating customer orders. There is an issue where it doesn't
   always respond to CTRL+C to end the process. You may have to close the terminal instead when you want to close it.
7. In a separate terminal, from the "src" folder run `streamlit run streamlit_app.py`

Everything should be running at this point.

### Folder structure

`dockerfiles` - Custom Dockerfile scripts for the build.

- If you are behind a firewall that messes with SSL certificates, you may need to modify the connect.Dockerfile script.
  It will need the CA signing cert included during the build. An example for Netskope is included.

`docs` - Documentation.  
`kafka_connect` - Kafka Connect scripts for creating connectors.  
`ksql` - ksqlDB scripts for reference.  
`resources` - Support files for the project.  
`src` - Source code.

### Technologies Used

[Docker](https://www.docker.com/)  
[Confluent Docker Images](https://docs.confluent.io/platform/current/installation/docker/image-reference.html):
Community editions

- Kafka
- Schema Registry
- ksqlDB
- Connect

[Python 3](https://www.python.org/)  
[Streamlit](https://streamlit.io/)  
[UI for Apache Kafka](https://github.com/provectus/kafka-ui)  
[MongoDB](https://www.mongodb.com/)  
