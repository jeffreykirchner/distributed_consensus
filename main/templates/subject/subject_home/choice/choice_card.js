/**
 * send choice
 */
sendchoice(){

    app.working = true;
    app.sendMessage("choice",
                   {"formData" : {choice : null,}});
                     
},

/** take result of submitting choice
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

/**
 * handle choice grid click
 */
 take_choice_grid_click(outcome_id, outcome_index){

    if(this.working) return;

    app.current_outcome_index = outcome_index;
    app.current_outcome_id = outcome_id;
    
},