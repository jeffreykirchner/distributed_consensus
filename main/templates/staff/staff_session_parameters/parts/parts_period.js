/**show edit parameter set player
 */
 showEditParametersetPartPeriod:function(id){
    
    if(app.session.started) return;

    var parameter_set_parts = app.session.parameter_set.parameter_set_parts;

    index = -1;
    for(i=0;i<parameter_set_parts.length;i++)
    {
        if(parameter_set_parts[i].id == id)
        {
            index = i;
            break;
        }
    }
    
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetPartBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_parts[index]);
    
    app.parametersetPartBeforeEditIndex = index;
    app.current_parameter_set_part = app.session.parameter_set.parameter_set_parts[index];
    
    app.editParametersetPartPeriodModal.toggle();
},

/** hide edit parmeter set player
*/
hideEditParametersetPartsPeriod:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_parts[app.parametersetPartBeforeEditIndex], app.parametersetPartBeforeEdit);
       
        app.parametersetPartBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdatePart(){
    
    app.working = true;

    let parameter_set_parts = app.session.parameter_set.parameter_set_parts;

    index=-1;
    for(i=0;i<parameter_set_parts.length;i++)
    {
        if(parameter_set_parts[i].id == app.current_parameter_set_part.id)
        {
            index=i;
            break;
        }
    }

    formData = parameter_set_parts[index];

    app.sendMessage("update_parameterset_part", {"sessionID" : app.sessionID,
                                                 "paramterset_part_id" : app.current_parameter_set_part.id,
                                                 "formData" : formData});
},

/** handle result of updating parameter set player
*/
takeUpdateParametersetParts(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        app.editParametersetPartModal.hide();        
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},