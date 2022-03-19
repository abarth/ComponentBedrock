# Readme

## Conceptual discussion

* The APIs in bedrock.py are for implementing Component Manager.
  * They are not exposed verbatim to component authors
  * They are useful to implement what _is_ exposed to component authors, both today and for future client needs

## Terms here vs in CF today (Mar 2022)

### Directories

* outgoing == "exposed directory"
* incoming == ? (meant to be capabilities provided by parent)
* incoming_namespace == "namespace"
* outgoing_namespace == "outgoing directory"