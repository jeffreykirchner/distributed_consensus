/** take update session_player list
 * @param messageData {json} result of update, either sucess or fail with errors
*/
take_update_session_players(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {     
        result = messageData.status.result;

        for(let i=0;i<result.session_players.length;i++)
        {
            let session_player = app.findSessionPlayer(result.session_players[i].id);
            session_player = result.session_players[i];
        }       
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** take update subject response
 * @param messageData {json} result of update, either sucess or fail with errors
*/
take_choice(messageData){
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {     
        result = messageData.status.result;
        let session_player = app.findSessionPlayer(result.player_id);
        session_player.session_player_parts = result.session_player_parts; 
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** take final result
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeFinalResults(messageData){
    if(messageData.value == "success")
    {     
        app.session.current_experiment_phase = messageData.current_experiment_phase;

        app.paymentPeriodsModal.hide();
        this.payment_periods_result = "";

        app.updatePhaseButtonText();

        session_players = messageData.session_players;

        for(let i=0;i<session_players.length;i++)
        {
            let session_player = app.findSessionPlayer(session_players[i].id);
            session_player.earnings = session_players[i].earnings;
        }
    }
    else
    {

    }
},

/**
 * return current part
 */
get_current_part(){    
    return app.session.session_parts[app.session.current_index.part_index];                         
},

/**
 * return part period
 */
 get_part_player(part_index, player_index){

    if(!app.session) return null;

    if(part_index == -1) return null;

    return app.session.session_players[player_index]
                      .session_player_parts[part_index];
},

/** take final result
 * @param messageData {json} result of update, either sucess or fail with errors
*/
take_update_ready_to_go_on(){
    if(messageData.status.value == "success")
    {     
        result = messageData.status.result;
        current_index = result.current_index;

        let session_player = app.findSessionPlayer(result.player_id);
        session_player.session_player_parts[current_index.part_index] = result.session_player_part;
        
    }
    else
    {

    }
},