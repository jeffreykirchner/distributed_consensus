/** take final result
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeFinalResults(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;        
        app.session.current_experiment_phase = result.current_experiment_phase;        
        app.session_player = result.session_player;
        app.session_player.earnings = result.earnings;
        //app.current_choice = result.current_choice;

        app.scroll_choice_into_view();
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

        app.scroll_choice_into_view();
    }
    else
    {

    }
},

/** take refresh screen
 * @param messageData {json} result of update, either sucess or fail with errors
*/
take_refresh_screens(messageData){
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
