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

## Structure

 * Declarative presentation
  * See the big picture / scale to larger use cases
  * More opinion about which patterns are good/common
 * Imperative API for the engine
  * Porcelain
    * Do larger tasks with fewer words
    * Establish conventions and common patterns
    * Does not talk to engine directly / only talks to bedrock
    * Can be implemented in the same source base as bedrock
      * e.g., can use language visibility to enforce layering
  * Bedrock
    * Preserves system invariants
    * Exposed to clients with appropriate capabilities
    * Talks directly the engine / is magical
    * Minimize/reuse concepts as much as possible
    * Aim for simple / atomic operations on those concepts
 * Routing engine
  * Private to the platform
  * Keeps the model for what's happening
  * Eventually "does the work"
