Secretary
=========

Secretary consist of 3 main components: Secretary, used to coordinate the communication between Cuckoo and Hermes, the Hermes package, which abstracts the functions of the Hermes-API, accessible via HTTPS. The Cuckoo package abstracts the Cuckoo API-server and is based on HTTP communication.

Communication with Cuckoo is based on Cuckoo's API-Server (a simple HTTP-Server, developed with the Python web-framework Bottle) and works with HTTP. The message format is JSON. 

Communication with Hermes is based on the Hermes-API-controller (Hermes Web-API) and works with HTTPS. Parameters are submitted as form-data inside a HTTP-POST request. The HTTP-response of the server is in JSON format. The response is translated into corresponding DTO objects by the DtoFactory.

Once initialized, secretary checks if this secretary instance is already registered on Hermes. If this is not the case, the instance registers itself on Hermes. Next a thread will be started, that is used to submit the node state to Hermes. The main thread contains the polling loop. Jobs are polled from Hermes until a job is received. These are submitted to Cuckoo. Once Cuckoo has finished analysing the job, the results are submitted to Hermes.
