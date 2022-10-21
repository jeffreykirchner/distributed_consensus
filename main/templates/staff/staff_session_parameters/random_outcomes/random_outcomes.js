/**show edit parameter set player
 */
 showEditRandomOutcome:function(id){
    
    if(app.session.started) return;

    var random_outcomes = app.session.parameter_set.parameter_set_random_outcomes;

    index = -1;
    for(i=0;i<random_outcomes.length;i++)
    {
        if(random_outcomes[i].id == id)
        {
            index = i;
            break;
        }
    }
    
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.randomOutcomeBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_random_outcomes[index]);
    
    app.parametersetRandomOutcomeEditIndex = index;
    app.current_random_outcome = app.session.parameter_set.parameter_set_random_outcomes[index];
    
    app.editRandomOutcomeModal.toggle();
},

/** hide edit parmeter set player
*/
hideEditRandomOutcome:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_random_outcomes[app.parametersetRandomOutcomeEditIndex], app.randomOutcomeBeforeEdit);
       
        app.randomOutcomeBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateRandomOutcome(){
    
    app.working = true;

    let random_outcomes = app.session.parameter_set.parameter_set_random_outcomes;

    index=-1;
    for(i=0;i<random_outcomes.length;i++)
    {
        if(random_outcomes[i].id == app.current_random_outcome.id)
        {
            index=i;
            break;
        }
    }

    formData = random_outcomes[index];

    // for(i=0;i<app.parameterset_player_form_ids.length;i++)
    // {
    //     v = app.parameterset_player_form_ids[i];
    //     formData[v] = parameter_set_players[index][v];
    // }

    app.sendMessage("update_parameterset_random_outcome", {"sessionID" : app.sessionID,
                                                           "random_outcome_id" : app.current_random_outcome.id,
                                                           "formData" : formData});
},

/** handle result of updating parameter set player
*/
takeUpdateRandomOutcome(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        //app.takeGetSession(messageData);     
        app.session=null;         
        window.location.reload();
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** copy specified period's groups forward to future groups
*/
sendRemoveRandomOutcome(){

    app.working = true;
    app.sendMessage("remove_parameterset_random_outcome", {"sessionID" : app.sessionID,
                                                           "random_outcome_id" : app.current_random_outcome.id,});
                                                   
},

/** handle result of copying groups forward
*/
takeRemoveRandomOutcome(messageData){
    app.cancelModal=false;
    //app.clearMainFormErrors();
    app.session=null;   
    window.location.reload();
},

/** copy specified period's groups forward to future groups
*/
sendAddRandomOutcome(player_id){
    app.working = true;
    app.sendMessage("add_parameterset_random_outcome", {"sessionID" : app.sessionID});
                                                   
},

/** handle result of copying groups forward
*/
takeAddRandomOutcome(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();
    //app.takeGetSession(messageData); 
    app.session=null;
    window.location.reload();
},
