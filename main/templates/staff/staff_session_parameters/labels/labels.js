/**show edit parameter set labels
 */
 showEditParametersetLabels:function(id){
    
    if(app.session.started) return;

    var parameter_set_labels = app.session.parameter_set.parameter_set_labels;

    index = -1;
    for(i=0;i<parameter_set_labels.length;i++)
    {
        if(parameter_set_labels[i].id == id)
        {
            index = i;
            break;
        }
    }
    
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetLabelsBeforeEdit = Object.assign({}, app.session.parameter_set.parameter_set_labels[index]);
    
    app.parametersetLabelsBeforeEditIndex = index;
    app.current_parameter_set_labels = app.session.parameter_set.parameter_set_labels[index];
    
    app.editParametersetLabelsModal.toggle();
},

/** hide edit parmeter set player
*/
hideEditParametersetLabels:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_labels[app.parametersetLabelsBeforeEditIndex], app.parametersetLabelsBeforeEdit);
       
        app.parametersetLabelsBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateLabels(){
    
    app.working = true;

    let parameter_set_labels = app.session.parameter_set.parameter_set_labels;

    index=-1;
    for(i=0;i<parameter_set_labels.length;i++)
    {
        if(parameter_set_labels[i].id == app.current_parameter_set_labels.id)
        {
            index=i;
            break;
        }
    }

    formData = parameter_set_labels[index];

    app.sendMessage("update_parameterset_labels", {"sessionID" : app.sessionID,
                                                   "paramterset_labels_id" : app.current_parameter_set_labels.id,
                                                   "formData" : formData});
},

/** handle result of updating parameter set player
*/
takeUpdateParametersetLabels(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        app.editParametersetLabelsModal.hide();        
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},