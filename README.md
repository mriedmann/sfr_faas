# Assignment: Serverless

## 1 Context

You are working for a newly created Bank called Bank98. During the creation
of a new banking platform this company decides to invest in a prototype to
evaluate the usage of Serverless/FaaS for further services. You are free to choose
which FaaS Provider you want to use: e.g. create a free personal account for
AWS, Azure, or Google Cloud; or set up your own on-premise FaaS platform
like Openfaas.

## 2 Tasks

### Task 1: Implement a Prototype:

The scope of the prototype is quite limited. The goal is to create three functions
which communicate with each other and can store data. Those three functions
are:

* Customers: Stores and persists customers with a name, address, and an
IBAN. Customers can be fetched and created. The usecase, that customers
can have multiple bank products, and therefore multiple IBANs can be
ignored for this prototype.

* Transactions: Stores transactions between specific IBANs. In addition
to an execution date, an amount, and a description, these transactions
should also contain a creditor and debtor IBAN.

* Monthly Report: This function takes an IBAN and returns a JSON that
includes the customer information, and the list of transactions for a specified month.

### Task 2: Evaluate Usage of FaaS-Frameworks

In a second step take a look at frameworks like the Serverless-Framework, or
ClaudiaJS to make an assumptions if those frameworks could be a useful choices
for the creation of applications based on FaaS. Provide a management summary
(one slide) that endorses your argumentation.

\newpage

## 3 Solution

To favor open-source and see how a more minimalistic approach to faas could look 
like, a basic installation of [Kubeless](https://kubeless.io/) on 
[Minikube](https://kubernetes.io/docs/setup/learning-environment/minikube/) 
was used for this assignment.

### Task 1

To fulfill the 3 given use-cases 3 different services (customers, transactions 
and reports) were implemented. All services are written in python3 and do only
depend on the very popular [requests]() library as well as couchdb as 
persistence layer.

Every service is deployed using 1 or more function, one function per possible
user action. Kubeless with python does not provide good support for REST-like
APIs so a different approach was used. All Services are reachable via one 
common Hostname (e.g. `faas.192.168.39.31.nip.io`) using the built-in 
http-trigger feature of Kubeless. Every function is deployed under a sub-path
to this common Hostname (e.g. `/customers/get`) and can therefor be easily 
reached.

To test the setup install Minikube and Kubeless and run `install.sh`. This
created all functions and triggers. Besides that you have to install couchdb
on the cluster and expose its port. Also, you have to modify the env-vars of
the functions to fit your environment (`DB_URL`,`CUSTOMERS_URL`,`TRANSACTIONS_URL`).

There is a very simple integration-test-suite under `tests.py`. For 
manual testing you could use a local python installation like this:
```bash
cd reports
python3 -c '\
  import handler; \
  print( \
    handler.get_report( \
      {"data":"{\"IBAN\":\"AT411100000237571500\"}"}, \
      {} \
    ) \
  )'
```
To test deployed services on K8S you can use curl:
```bash
curl \
http://faas.192.168.39.31.nip.io/customers/get-by \
--data '{"attr":"IBAN","value":"AT411100000237571500"}' 
```

\newpage

### Task 2

Among all FaaS Frameworks [Serverless](https://serverless.com/) was the most
promising one with Kubeless support. The following a basic draft for a 

#### Slide Draft

How would Serverless Framework help us with FaaS/Kubeless?

**Development**

* Version Management: Serverless gives us the possibility to handle different versions
of functions a simple and safe way.

* Structure: Serverless establishes a well-defined structure within project. This could
lead to more transparency and could reduce the review afford significantly. 

* Abstraction: Even if some specifics are bound to our FaaS-Platform Kubeless, the 
overall structure is very generic and can be very useful if we have to switch our
platform in the future.

**Deployment**

* Simple Deployments: Currently all functions and triggers have to be
managed manually. This is error-prone and time-consuming. With Serverless we
could define a complete deployment within a single yaml-file.

* Configuration and Secret Handling: Currently we have to deal with this on a 
project basis. This is inefficient and leads to problems during deployments.

* Commercial Support: There is a Pro subscription that can reduce management and monitoring
effort in production as well as provide CI/CD functionality. 