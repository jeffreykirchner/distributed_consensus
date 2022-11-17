/**
 * send choice
 */
sendchoice(){

    current_part_period = app.get_current_part_period();

    if(!current_part_period) return;
    if(app.session.current_experiment_phase == 'Instructions') return;

    let t = new Date().getTime();
    let time_span = t - app.choice_start_time;

    app.working = true;
    app.sendMessage("choice",
                   {"data" : {random_outcome_id : current_part_period.current_outcome_id,
                              part_period_id :  current_part_period.id,
                              time_span : time_span,
                              current_index : app.session.current_index}});
                     
},

/** take result of submitting choice
*/
takeChoice(messageData){
    
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;
        current_index = result.current_index;

        app.session_player.session_player_parts = result.session_player_parts;

        // part_period = app.get_part_period(current_index.part_index, current_index.period_index);
        // part_period.choice = result.session_player_part_period.choice;
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

    if(messageData.status.value == "success")
    {
        app.session.current_index = result.current_index;
        app.session.current_experiment_phase = result.current_experiment_phase;
        app.current_choice = result.current_choice;
        app.session.time_remaining = app.session.parameter_set.period_length;
        app.scroll_choice_into_view();
        app.do_flip_animations();
        app.instructionDisplayScroll();

        app.choice_start_time = new Date().getTime();
    }
    else
    {
        
    }
},

async do_flip_animations(){

    if(app.session.current_experiment_phase != "Run") return;
    
    let mode = app.current_choice.session_part.parameter_set_part.mode;

    if(mode == "A")
    {

        if(app.current_choice.session_part.show_results)
        {
           
        }
        else
        {
            Vue.nextTick(() => {
                app.do_flip_animations_b("id_choice_a_image", "signal_image_animation");           
            })
        }
    }
    else if(mode == "B")
    {
        Vue.nextTick(() => {
            app.do_flip_animations_b("id_choice_b_image", "signal_image_animation");


            for(let i=0;i<app.current_choice.session_player_part_period_group.length;i++)
            {
                let element_id = 'group_labels_' + app.current_choice.session_player_part_period_group[i].id;
                app.do_flip_animations_b(element_id, "signal_image_animation");
            }
        })
        
    }
    else if(mode == "C")
    {
        Vue.nextTick(() => {

            app.do_flip_animations_b("id_choice_c_image", "signal_image_animation");

            for(let i=0;i<app.current_choice.session_player_part_period_group.length;i++)
            {
                let element_id = 'group_labels_' + app.current_choice.session_player_part_period_group[i].id;
                app.do_flip_animations_b(element_id, "signal_image_animation");
            }
        })
    }
},

do_flip_animations_b(element_id, animation_name){
    // retrieve the element
    element = document.getElementById(element_id);
        
    // -> removing the class
    element.classList.remove(animation_name);
    void element.offsetWidth;
    
    // -> and re-adding the class
    element.classList.add(animation_name);
},

scroll_choice_into_view()
{
    document.body.scrollTop = document.documentElement.scrollTop = 0;

    // if(app.session.current_experiment_phase == "Pay") return;
    
    // let mode = app.current_choice.session_part.parameter_set_part.mode;

    // if(mode == "A")
    // {
    //     if(app.current_choice.session_part.show_results)
    //     {
    //         document.getElementById("id_choice_a_results_card").scrollIntoView();
    //     }
    //     else
    //     {
    //         document.getElementById("id_choice_a_card").scrollIntoView();
    //     }
    // }
    // else if(mode == "B")
    // {
    //     document.getElementById("id_choice_b_card").scrollIntoView();
    // }
    // else if(mode == "C")
    // {
    //     document.getElementById("id_choice_c_card").scrollIntoView();
    // }
},

sendReadyToGoOn(){

    app.working = true;
    current_index = app.session.current_index;
    app.sendMessage("ready_to_go_on",
                   {"data" : {player_part_id : app.session_player.session_player_parts[current_index.part_index].id,
                              current_index : current_index
                              }});
},

/** take ready to go on
 * @param messageData {json} result of update, either sucess or fail with errors
*/
takeReadyToGoOn(messageData){
    if(messageData.status.value == "success")
    {
        result = messageData.status.result;

        current_index = result.current_index;

        player_part = app.session_player.session_player_parts[current_index.part_index];
        player_part.results_complete = result.session_player_part.results_complete;
        
    }
    else
    {

    }
},

/**
 * return visibility status of choice card.
 */
choice_card_visible(){

    if(!app.current_choice.hasOwnProperty('session_part')) return false;

    if(app.session.current_experiment_phase != 'Run' && 
       app.session.current_experiment_phase != 'Instructions') return false;

    session_player_part = app.session_player.session_player_parts[app.current_choice.session_part.parameter_set_part.part_number-1];
    
    if(app.session.current_experiment_phase == 'Instructions' && 
       app.current_choice.session_part.parameter_set_part.part_number == 1 &&
       session_player_part.current_instruction_complete == 0) return false;

    return true;
},


