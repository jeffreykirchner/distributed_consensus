{%if session.parameter_set.test_mode%}

/**
 * do random self test actions
 */
randomNumber(min, max){
    //return a random number between min and max
    min = Math.ceil(min);
    max = Math.floor(max+1);
    return Math.floor(Math.random() * (max - min) + min);
},

randomString(min_length, max_length){

    s = "";
    r = this.randomNumber(min_length, max_length);

    for(let i=0;i<r;i++)
    {
        v = this.randomNumber(48, 122);
        s += String.fromCharCode(v);
    }

    return s;
},

doTestMode(){
    {%if DEBUG%}
    console.log("Do Test Mode");
    {%endif%}

    if(this.end_game_modal_visible)
    {
        if(this.session_player.name == "")
        {
            document.getElementById("id_name").value =  this.randomString(5, 20);
            document.getElementById("id_student_id").value =  this.randomNumber(1000, 10000);

            this.sendName();
        }

        return;
    }

    if(this.session.started &&
       this.session.parameter_set.test_mode
       )
    {
        
        switch (this.session.current_experiment_phase)
        {
            case "Instructions":
                this.doTestModeInstructions();
                break;
            case "Run":
                this.doTestModeRun();
                break;
            
        }        
       
    }

    setTimeout(this.doTestMode, this.randomNumber(1000 , 1500));
},

/**
 * test during instruction phase
 */
 doTestModeInstructions()
 {
    if(this.session_player.instructions_finished) return;
    if(this.working) return;
    
   
    if(this.session_player.current_instruction == this.session_player.current_instruction_complete)
    {

        if(this.session_player.current_instruction == this.instruction_pages.length)
            document.getElementById("instructions_start_id").click();
        else
            document.getElementById("instructions_next_id").click();

    }else
    {
        //take action if needed to complete page
        switch (this.session_player.current_instruction)
        {
            case 1:
                break;
            case 2:
                
                break;
            case 3:
                
                break;
            case 4:
                
                break;
            case 5:
                break;
        }   
    }

    
 },

/**
 * test during run phase
 */
doTestModeRun()
{
    //do chat
    let go = true;
        
    if(app.session.finished) return;
    if(app.working) return;
        
    if(go)
        switch (this.randomNumber(1, 1)){
            case 1:
                this.doTestModeChoice();
                break;
            
            case 2:
                break;
            
            case 3:
                
                break;
        }
},

doTestModeChoice()
{
    session_player_part_period = app.get_current_part_period();

    if(app.current_choice.session_part.parameter_set_part.mode=='A' && 
       app.current_choice.session_part.show_results && 
       !app.session_player.session_player_parts[app.session.current_index.part_index].results_complete)
    {
        app.sendReadyToGoOn();
    }
    else if(session_player_part_period.current_outcome_id == -1)
    {//select one of the choices
        index = randomNumber(0, app.session.parameter_set.parameter_set_random_outcomes.length-1);
        parameter_set_random_outcome = app.session.parameter_set.parameter_set_random_outcomes[index];
        app.take_choice_grid_click(parameter_set_random_outcome.id, index);
    }
    else if(!session_player_part_period.choice)
    {//send choice
        app.sendchoice();
    }   
},

{%endif%}