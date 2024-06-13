# safeGuard
![progettotap](images/logo_resized.png)
safeGuard is a surveillance solution designed to detect movements within a specified area using cameras. Using image processing techniques, safeGuard not only identifies motion but also tracks and compiles statistics on objects present in the monitored scenes. This enables enhanced security monitoring, providing detailed insights and data-driven analysis for improved safety and situational awareness.

# How it works?



### Data Source 
  - [OrangePI](http://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/orange-pi-3-LTS.html) ---> The source data for our project is an Orange Pi device, utilized for motion detection and image capture.
 cryptocurrencies
  
  
### Tools
- **FluentBit**: A lightweight and extensible log processor and forwarder, used for collecting and forwarding log data from various sources.
- **Kafka**: A distributed messaging system employed to facilitate data streaming between different components of the project.
- **Zookeeper**: It helps in maintaining configuration information, naming, providing distributed synchronization, and group services.
- **Spark**: A Python library for distributed data processing, used to perform image detection and object counting.
- **Elasticsearch**: A distributed search and analytics engine, used for storing and indexing data about images.
 
 ### Dashboard
 The dashboard displays information related to all the detections present.
 
 ![dashboard]()



### How to start!!

Use `Docker-compose up -d` command  in the shell and have fun!
