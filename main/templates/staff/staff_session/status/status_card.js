/** take advance to next period
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeNextPeriod(messageData){
    result = messageData.status.result;
    
    if(messageData.status.value == "success")
    {   
        session_part = result.session_part;     
        app.session.current_index = result.current_index;
        app.session.current_experiment_phase = result.current_experiment_phase;
        app.session.session_parts[result.session_part.parameter_set_part.part_number-1] = result.session_part;

        app.updatePhaseButtonText();        

        for(let i=0;i<result.session_players.length;i++)
        {
            let session_player = app.findSessionPlayer(result.session_players[i].id);
            session_player.earnings = result.session_players[i].earnings;
        }
    }
    else
    {

    }
},