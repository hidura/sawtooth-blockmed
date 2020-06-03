## Add new ledger
### Steps
1. Create the protobuf.
2. Add the Payload type.
3. Go to payload.py on the processor/processor/workflow and add the is 
    method to verify the type of payload it is and the create/modify method.
4. Add the elif to the handler(processor/processor/workflow/) with the new code to store
    the information on the server.
5. Go to the state(processor/processor/workflow/) to add the get method that will retrive the information

6. Inside the get method is the _load method that will load the block, create it.
    6.1 Before anything add the ENTITY_CODE inside the helper on common/helper.
    6.2 Then add the make_class_address inside the helper on common/helper. 
    6.3 Then add add the list_address inside the helper