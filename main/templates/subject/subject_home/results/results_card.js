/** take final result
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeFinalResults(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;        
        app.session = result.session;        
        app.session_player = result.session_player;
        app.current_choice = result.current_choice;
    }
    else
    {

    }
},

/** take final result
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeCurrentPartResult(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;        
        app.session = result.session;        
        app.session_player = result.session_player;
        app.current_choice = result.current_choice;
    }
    else
    {

    }
},
