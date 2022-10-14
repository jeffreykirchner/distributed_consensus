/**show edit parameter set player
 */
 showEditParametersetPartPeriod:function(id){
    
    if(app.session.started) return;

    var parameter_set_part_period = null;

    index = -1;
    for(i=0;i< app.session.parameter_set.parameter_set_parts.length;i++)
    {
        for(j=0;j<app.session.parameter_set.parameter_set_parts[i].parameter_set_part_periods.length;j++)
        {
            if(app.session.parameter_set.parameter_set_parts[i].parameter_set_part_periods[j].id == id)
            {
                parameter_set_part_period = app.session.parameter_set.parameter_set_parts[i].parameter_set_part_periods[j];
                app.parametersetPartPeriodBeforeEditIndex = {i:i, j:j}
                break;
            }
        }

        if(parameter_set_part_period) break;
    }
    
    app.clearMainFormErrors();
    app.cancelModal=true;
    app.parametersetPartsPeriodBeforeEdit = Object.assign({}, parameter_set_part_period);
    
    app.current_parameter_set_part_period = parameter_set_part_period;
    
    app.editParametersetPartPeriodModal.toggle();
},

/** hide edit parmeter set player
*/
hideEditParametersetPartsPeriod:function(){
    if(app.cancelModal)
    {
        Object.assign(app.session.parameter_set.parameter_set_parts[app.parametersetPartPeriodBeforeEditIndex.i]
                                 .parameter_set_part_periods[app.parametersetPartPeriodBeforeEditIndex.j],
                      app.parametersetPartsPeriodBeforeEdit);

                    app.parametersetPartsPeriodBeforeEdit=null;
    }
},

/** update parameterset type settings
*/
sendUpdatePartPeriod(){
    
    app.working = true;

    var parameter_set_part_period = app.session.parameter_set.parameter_set_parts[app.parametersetPartPeriodBeforeEditIndex.i]
                                                               .parameter_set_part_periods[app.parametersetPartPeriodBeforeEditIndex.j];

    formData = parameter_set_part_period;

    app.sendMessage("update_parameterset_part_period", {"sessionID" : app.sessionID,
                                                        "paramterset_part_period_id" : app.current_parameter_set_part_period.id,
                                                        "formData" : formData});
},

/** handle result of updating parameter set
*/
takeUpdateParametersetPartPeriod(messageData){
    //app.cancelModal=false;
    //app.clearMainFormErrors();

    app.cancelModal=false;
    app.clearMainFormErrors();

    if(messageData.status.value == "success")
    {
        app.takeGetSession(messageData);       
        app.editParametersetPartPeriodModal.hide();        
    } 
    else
    {
        app.cancelModal=true;                           
        app.displayErrors(messageData.status.errors);
    } 
},

/** update parameterset type settings
*/
sendRandomizePartPeriods(){
    
    app.working = true;
    app.sendMessage("update_parameterset_randomize_part_periods", {"sessionID" : app.sessionID,
                                                                  });
},
