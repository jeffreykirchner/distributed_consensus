/**
 * send choice
 */
sendchoice(){

    current_part_period = app.get_current_part_period();

    if(!current_part_period) return;

    app.working = true;
    app.sendMessage("choice",
                   {"data" : {random_outcome_id : current_part_period.current_outcome_id,
                              part_period_id :  current_part_period.id,
                              current_index : app.session.current_index}});
                     
},

/** take result of submitting choice
*/
takeChoice(messageData){
    
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;
        current_index = result.current_index;

        part_period = app.get_part_period(current_index.part_index, current_index.period_index);
        part_period.choice = result.session_player_part_period.choice;
    } 
    else
    {
        
    }
},

/**
 * handle choice grid click
 */
 take_choice_grid_click(outcome_id, outcome_index){

    if(this.working) return;   

    session_player_part_period = app.get_current_part_period()

    if(session_player_part_period)
    {
        session_player_part_period.current_outcome_id=outcome_id;
        session_player_part_period.current_outcome_index=outcome_index;
    }
},

/**
 * return current part period
 */
get_current_part_period(){
    
    return app.get_part_period(app.session.current_index.part_index, app.session.current_index.period_index);                         
},

/**
 * return part period
 */
get_part_period(part_index, period_index){

    if(!app.session) return null;

    if(part_index == -1 || period_index == -1) return null;

    return app.session_player.session_player_parts[part_index]
                             .session_player_part_periods[period_index];
},

/** take advance to next period
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeNextPeriod(messageData){
    result = messageData.status.result;
    app.session.current_index = result.current_index;
    app.current_choice = result.current_choice;
},