/** take choice from subject
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeChoice(messageData){
    
},

/** take advance to next period
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeNextPeriod(messageData){
    result = messageData.status.result;
    
    if(messageData.status.value == "success")
    {        
        app.session.current_index = result.current_index;
        app.session.current_experiment_phase = result.current_experiment_phase;
    }
    else
    {

    }
},