# Asynchronous Post-processing for Caravel Harness

The Caravel harness has been widely used to tape-out synchronous designs in the open-source SKY130 PDK. To use this flow for asynchronous circuit design using the open-source Act framework, we can treat Act-generated layout as an asynchronous macro. We develop an open-source toolflow that supports this approach. We include automatically genererated power rings and connection, pin extension, and custom fill insertion.

Use process_chip_magic.py to generate a .tcl script that can be sourced into Magic for post-processing.
