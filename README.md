
### Message Box 

It is an example application that tries to provide synchronous access 
to an asynchronous web service that expects to send results to a http 
endpoint on a success callback.

Message Box instance is running a http server waiting for such callbacks, 
and any client can open a web socket connection to it and wait for a
callback with given id.  