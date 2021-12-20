Microservices architecture that receives and processes weather forecast events.

Services include:

* Receiver - Edge service that receives events in JSON format.

* Kafka - Message broker to faciliate communication between the receiver and other services.

* Storage - Stores events in a MySQL database.
  
* Processing - Periodically processes recently received events to calculate statistics.
  
* Audit - Retrieves event from message queue with a specified index.
  
* Dashboard - User interface that dynamically displays events statistics as the database and message queue change.
