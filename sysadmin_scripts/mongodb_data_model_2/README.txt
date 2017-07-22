This project updates data model 1 version of Mongo DB for Spatial Transcriptomics back-end
to data model 2.

It makes use of 'pymongo' for connection scripting.

Each collection in the new DB has its own Python class file. Some objects are present already,
and are changed/extended, while some are introduced (as initially empty collections). This can be
deduced from class level variables in the Python classes.