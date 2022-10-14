/**show edit parameter set labels
 */
 showEditParametersetLabelsPeriod:function(id){
    
    if(app.session.started) return;

    var parameter_set_labels_period = null;

    index = -1;
    for(i=0;i< app.session.parameter_set.parameter_set_labels.length;i++)
    {
        for(j=0;j<app.session.parameter_set.parameter_set_labels[i].parameter_set_labels_period.length;j++)
        {
            if(app.session.parameter_set.parameter_set_labels[i].parameter_set_labels_period[j].id == id)
            {
                parameter_set_labels_period = app.session.parameter_set.parameter_set_labels[i].parameter_set_labels_period[j];
                app.parametersetLabelsBeforeEditIndex = {i:i, j:j}
                break;
            }
        }

        if(parameter_set_labels_period) break;
    }
    
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetLabelsPeriodBeforeEdit = Object.assign({},parameter_set_labels_period);
    
    app.current_parameter_set_labels_period = parameter_set_labels_period;
    
    app.editParametersetLabelsPeriodModal.toggle();
},

/** hide edit parmeter set player
*/
hideEditParametersetLabelsPeriod:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_labels[app.parametersetLabelsBeforeEditIndex.i]
                                               .parameter_set_labels_period[app.parametersetLabelsBeforeEditIndex.j],
                      app.parametersetLabelsPeriodBeforeEdit);
       
        app.parametersetLabelsPeriodBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdateLabelsPeriod(){
    
    app.working = true;

    var parameter_set_labels_period = app.session.parameter_set.parameter_set_labels[app.parametersetLabelsBeforeEditIndex.i]
                                                               .parameter_set_labels_period[app.parametersetLabelsBeforeEditIndex.j];

    formData = parameter_set_labels_period;

    app.sendMessage("update_parameterset_labels_period", {"sessionID" : app.sessionID,
                                                          "parameterset_labels_period_id" : app.current_parameter_set_labels_period.id,
                                                          "formData" : formData});
},

/** update parameterset type settings
*/
sendRandomizeLabels(){
    
    app.working = true;

    app.sendMessage("update_parameterset_randomize_labels", {"sessionID" : app.sessionID,
                                                         });
},

/** handle result of updating parameter set player
*/
takeUpdateParametersetLabelsPeriod(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        app.editParametersetLabelsPeriodModal.hide();        
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},