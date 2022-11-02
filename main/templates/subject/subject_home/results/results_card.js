/** take final result
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeFinalResults(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;        
        app.session.current_experiment_phase = result.current_experiment_phase;        
        app.session_player.session_player_parts = result.session_player_parts;
        app.session_player.earnings = result.earnings;
        //app.current_choice = result.current_choice;
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
        //app.session = result.session;        
        app.session_player = result.session_player;
        //app.current_choice = result.current_choice;
    }
    else
    {

    }
},
