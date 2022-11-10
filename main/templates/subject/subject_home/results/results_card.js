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

/** return a list of pay session_player_part_periods for a given session_part
 * @param part_index session_part
*/
get_paid_list(part_index){
    let session_player_part_periods = app.session_player.session_player_parts[part_index].session_player_part_periods;

    v = [];

    for(let i=0; i<session_player_part_periods.length; i++)
    {
        if(session_player_part_periods[i].paid)
        {
            v.push(session_player_part_periods[i]);
        }
    }
   
    return v;
},
