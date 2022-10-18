sendchoice(){

    app.working = true;
    app.sendMessage("choice",
                   {"formData" : {choice : null,}});
                     
},

/** take result of submitting name
*/
takeChoice(messageData){

    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
              
    } 
    else
    {
        app.displayErrors(messageData.status.errors);
    }
},