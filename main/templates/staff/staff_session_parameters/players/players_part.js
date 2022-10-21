/**show edit parameter set labels
 */
 showEditParametersetPlayerPart:function(id){
    
    if(app.session.started) return;

    var parameter_set_player_part = null;

    // "session.session_players.0.parameter_set_player.parameter_set_player_parts"

    index = -1;
    for(i=0;i< app.session.session_players.length;i++)
    {
        for(j=0;j<app.session.session_players[i].parameter_set_player.parameter_set_player_parts.length;j++)
        {
            if(app.session.session_players[i].parameter_set_player.parameter_set_player_parts[j].id == id)
            {
                parameter_set_player_part = app.session.session_players[i].parameter_set_player.parameter_set_player_parts[j];
                app.parametersetPlayerPartBeforeEditIndex = {i:i, j:j}
                break;
            }
        }

        if(parameter_set_player_part) break;
    }
    
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetPlayerPartBeforeEdit = Object.assign({}, parameter_set_player_part);
    
    app.current_parameter_set_player_part = parameter_set_player_part;
    
    app.editParametersetPlayerPartModal.toggle();
},

/** hide edit parmeter set player
*/
hideEditParametersetPlayerPart:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.session_players[app.parametersetPlayerPartBeforeEditIndex.i]
                                .parameter_set_player.parameter_set_player_parts[app.parametersetPlayerPartBeforeEditIndex.j],
                      app.parametersetPlayerPartBeforeEdit);
       
        app.parametersetPlayerPartBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateParametersetPlayerPart(){
    
    app.working = true;

    var parameter_set_player_part = app.session.session_players[app.parametersetPlayerPartBeforeEditIndex.i]
                                                 .parameter_set_player.parameter_set_player_parts[app.parametersetPlayerPartBeforeEditIndex.j];

    formData = parameter_set_player_part;

    app.sendMessage("update_parameterset_player_part", {"sessionID" : app.sessionID,
                                                        "paramterset_player_part_id" : app.current_parameter_set_player_part.id,
                                                        "indexes" : app.parametersetPlayerPartBeforeEditIndex,
                                                        "formData" : formData});
},

/** handle result of updating parameter set player
*/
takeUpdateParametersetPlayerPart(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        //app.takeGetSession(messageData);     
        result = messageData.status.result;  
        app.session.session_players[result.indexes.i].parameter_set_player.parameter_set_player_parts[result.indexes.j]=result.parameter_set_player_part;
        app.editParametersetPlayerPartModal.hide();        
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},