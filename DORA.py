# DORA.py

# main code to run DORA.
run_on_iphone = False

# imports.
import random, copy, json
import numpy as np
import buildNetwork
import basicRunDORA
import pdb

# globals
vers_number = "0.2.3"  # DORA's version number.
path_name = "pythonDORA/currentVers"  # current path DORA's looking in.

# Parameters.
# create a big dictionary called parameters, with all parameters as fields.
# eta is for using for updating mapping connections.
# ignore_object_semantics is a parameter used when running in LISA mode. It allows DORA to downweight object semantics when multiple propositions are in the driver together. NOTE: I'm not sure if placing this item in the parameters dict is the best long-term solution. Likely, you'll want to integrate switching ignore_object_semantics automatically in the model based on context.
parameters = {
    "asDORA": True,
    "gamma": 0.3,
    "delta": 0.1,
    "eta": 0.9,
    "HebbBias": 0.5,
    "bias_retrieval_analogs": True,
    "use_relative_act": True,
    # run_order is an array indicating the order of operations for a learning phase
    # (cdr=clear driver and recipient, cr=clear recipient,
    # selectTokens=select token units from memory to place in the driver
    #   (the selection of tokens is by analog (i.e., a specific analog is chosen,
    #   and all tokens from that analog are placed in the driver)),
    # selectP=select a P at random from memory to place in the driver, r=retrieval, m=map,
    # p=predicate, f=form new relation, g=relational generalization, s=schema induction,
    # 'b'=between group entropy ops, 'w'=within group entropy ops,
    # 'wp'=within group entropy ops for preds only,
    #   (NOTE: b, w, and wp operations are newer to the theory and therefore listed after the old
    #   DORA operations; in reality according to the theory, they should occur after retrieval
    #   and before mapping)
    # 'co'=compression (NOTE: compression is an old part of the theory covered in Doumas, 2005,
    #   but newly implemented for general DORA),
    # c=clear results, cl=limited clear results (just inferences and newSet),
    # wdr= write the current state of the driver and recipient to output file,
    # wn=write current state of the network to output file).
    "run_order": ["cdr", "selectTokens", "r", "wp", "m", "p", "s", "f", "c"],
    "run_cyles": 5000,
    "write_on_iteration": 100,
    "firingOrderRule": "random",
    "strategic_mapping": False,
    "ignore_object_semantics": False,
    "ignore_memory_semantics": True,
    "mag_decimal_precision": 0,
    "exemplar_memory": False,
    "recent_analog_bias": True,
    "lateral_input_level": 1,
    "screen_width": 1200,
    "screen_height": 700,
    "doGUI": True,
    "testing": True,
    "GUI_update_rate": 1,
    "starting_iteration": 0,
    "tokenize": False,
    "ho_sem_act_flow": 0,
    "remove_uncompressed": False,
    "remove_compressed": False,
}

# do a run_on_iphone check and set doGUI to false if running on iphone.
if run_on_iphone:
    parameters["doGUI"] = False


# do I want to make these objects instead of functions?
# function to run the MainMenu.
class MainMenu(object):
    def __init__(self):
        self.vers_number = vers_number
        self.path_name = path_name
        self.network = None  # initialize the network to empty; filled with runDORA object later.
        # self.memory = basicRunDORA.dataTypes.memorySet()  # initialize an empty memorySet. *****NOTE: I don't think that you actuall need this field. It is subsumed for the purposes of running the model by the .network.memory object (i.e., you do all the work with the .network object, and the .network object has it's own version of the memory object).*****
        self.file = open("screens.py", "r")
        self.write_file = None  # file I should write data to.
        self.sym = None
        self.parameters = parameters
        self.parameterFile = None
        self.state = None

    def show_menu(self):
        # function to display menu contents and get user input on what state to enter.
        print("")
        print("***** DORA *****")
        print("Vers ", self.vers_number)
        print("Path = ", self.path_name)
        print("")
        print(" ----- MAIN MENU ----- ")
        print("")
        print("(L)oad sym file")
        print("sym file in memory is ", self.file)
        # print ('(P)ath: ', path_name)
        print("(C)lear loaded sym file")
        print("(S)ave current memory state")
        # print ('Load (O)ld memory state')
        print("output is written to ", self.write_file)
        print("(D)esignate file to WRITE to")
        print("Load (P)arameter file")
        print("(R)un")
        print("(Q)uit")
        # get user input.
        menu_state = input("DORA>")
        menu_state = (
            menu_state.upper()
        )  # python function to convert string to uppercase characters.
        # done.
        self.state = menu_state

    # noinspection PyPep8Naming
    def execute_mainmenu(self):
        global parameters  # porting from Python2 to Python3
        # function to execute state as input by user.
        if self.state.upper() == "L":
            # load a file into self.file.
            go_on = True
            while go_on:
                file_to_load = input("Enter name of sym file to load>")
                try:
                    self.file = open(file_to_load, "r")
                    break
                except IOError:
                    print(
                        "\nthere is no file called ",
                        file_to_load,
                        '. To try again, press Enter, or type "exit" to go back to MainMenu.',
                    )
                    new_state = input(">")
                    if new_state == "EXIT":
                        go_on = False
        elif self.state.upper() == "C":
            # clear the file from memory.
            self.file = None
        elif self.state.upper() == "S":
            # same the current state of memory.
            new_name = input("By what name will you save the current state?>")
            new_name += ".py"
            # use the .write_memory_to_symfile() funciton from basicRunDORA.
            basicRunDORA.write_memory_to_symfile(self.network.memory, new_name)
        elif self.state.upper() == "D":
            # designate the write file.
            print("Enter the name of the file to which you would like to write results")
            write_file = input("DORA>")
            self.write_file = open(write_file, "w")
        elif self.state.upper() == "P":
            # load a file into self.parameterFile.
            go_on = True
            while go_on:
                pfile_to_load = input("Enter name of parameter file to load>")
                try:
                    self.parameterFile = open(pfile_to_load, "r")
                    # now load the parameter file
                    parameter_string = ""
                    for line in self.parameterFile:
                        parameter_string += line
                    try:
                        parameters = ""  # porting from Python2 to Python3
                        d = {"parameters": parameters}  # porting from Python2 to Python3
                        exec(parameter_string, d)  # porting from Python2 to Python3
                        parameters = d["parameters"]  # porting from Python2 to Python3
                        go_on = False
                    except:
                        print(
                            "\nYour loaded paramter file is wonky. \nI am going to run anyway, but with preset parameters."
                        )
                        keep_running = input("Would you like to continue? (Y) or any key to exit>")
                        if keep_running.upper() != "Y":
                            do_run = False

                except IOError:
                    print(
                        "\n",
                        "there is no file called ",
                        pfile_to_load,
                        '. To try again, press Enter, or type "exit" to go back to MainMenu.',
                    )
                    new_state = input(">")
                    if new_state.upper() == "EXIT":
                        go_on = False
                #     try:
                #         exec (self.parameterFile)
                #         self.parameters = parameters
                #     except SyntaxError:
                #         print ('\nEntered parameter file is formatted incorrectly.')
                #     break
                # except IOError:
                #     print ('\n', 'there is no file called ', pfile_to_load, '. To try again, press Enter, or type "exit" to go back to MainMenu.')
                #     new_state = input('>')
                #     if new_state.upper() == 'EXIT':
                #         go_on = False
        elif self.state.upper() == "R":
            # make the network using build routines.
            # if the user has created a sym file using DORA's routines, use it to build the network, otherwise, use the loaded sym file.
            do_run = False
            if self.file:
                simType = ""
                di = {"simType": simType}  # porting from Python2 to Python3
                self.file.seek(0)  # to get to the beginning of the file.
                exec(self.file.readline(), di)  # porting from Python2 to Python3
                if di["simType"] == "sym_file":  # porting from Python2 to Python3
                    symstring = ""
                    for line in self.file:
                        symstring += line
                    do_run = True
                    symProps = []  # porting from Python2 to Python3
                    di = {"symProps": symProps}  # porting from Python2 to Python3
                    exec(symstring, di)  # porting from Python2 to Python3
                    self.sym = di["symProps"]  # porting from Python2 to Python3
                # now load the parameter file, if there is one.
                # if self.parameterFile:
                #     parameter_string = ''
                #     for line in self.parameterFile:
                #         parameter_string += line
                #     try:
                #         exec (parameter_string)
                #     except:
                #         print ('\nYour loaded paramter file is wonky. \nI am going to run anyway, but with preset parameters.')
                #         keep_running = input('Would you like to continue? (Y) or any key to exit>')
                #         if keep_running.upper() != 'Y':
                #             do_run = False
                elif di["simType"] == "json_sym":  # porting from Python2 to Python3
                    # you've loaded a json generated sym file, which means that it's in json format, and thus must be loaded via the json.load() routine.
                    # load the second line of the sym file via json.load().
                    symProps = json.loads(self.file.readline())
                    self.sym = symProps
                    do_run = True
                else:
                    print(
                        "\nThe sym file you have loaded is formatted incorrectly. \nPlease check your sym file and try again."
                    )
                    input("Enter any key to return to the MainMenu>")
            else:
                print("you need to load a sym file in the MainMenu.)")
                make_input = input("Enter any key to exit back to the MainMenu>")
                make_input = make_input.upper()
            if do_run:
                memory = buildNetwork.initializeMemorySet()
                # try to interpret the sym file. If it is not possible, then print (an error message.)
                try:
                    mysym = buildNetwork.interpretSymfile(self.sym)
                except:
                    print(
                        "\nYou have loaded an improperly formated sym file. \nPlease check your sym file and try again."
                    )
                    input("Enter any key to return to the MainMenu>")
                if self.network:
                    self.network.memory = buildNetwork.buildTheNetwork(
                        mysym[0], self.network.memory
                    )
                else:
                    memory = basicRunDORA.dataTypes.memorySet()
                    memory = buildNetwork.buildTheNetwork(mysym[0], memory)
                    # make the runDORA object.
                    self.network = basicRunDORA.runDORA(memory, parameters)
                # make sure the driver and recipient are all set up.
                self.network.memory = basicRunDORA.clearDriverSet(self.network.memory)
                self.network.memory = basicRunDORA.clearRecipientSet(self.network.memory)
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # make the runMenu.
                runMenu = RunMenu(self.network, self.parameters, self.write_file)
                # enter the run_menu.
                while runMenu.state.upper() != "E":
                    runMenu.showRunMenu()
                    runMenu.execute_runmenu()
                # record the rusults of the run.
                self.network = runMenu.network
        elif self.state.upper() == "Q":
            print("\nGoodbye.\n")
        else:  # user selection is not a valid menu option.
            print(
                "\nUmmm, ",
                self.state,
                " is not a valid choice. Let us try selecting again, shall we...\n",
            )


# function to run the RunMenu.
class RunMenu(object):
    def __init__(self, network: basicRunDORA.runDORA, parameters: dict, write_file):
        self.network = network
        self.parameters = parameters
        self.write_file = write_file
        self.state = "None"

    def showRunMenu(self):
        print("\n --- DORA RUN MENU --- ")
        print("(P)arameters")
        print("(V)iew network")
        print("(R)un DORA")
        print("(D)ebug mode (enter the debugger)")
        print("(E)xit back to MainMenu\n")
        # get user input.
        run_state = input("Run_DORA>")
        self.state = run_state

    def execute_runmenu(self):
        if self.state.upper() == "P":
            # print (parameters and allow user to modify them.)
            print("\n\n* * * PARAMETERS * * *")
            for parameter, value in parameters.items():
                print(parameter, ": ", value, "\n")
            print("You may modify parameters by entering a new parameter file in MainMenu.")
            input("Any key to continue...>")
        elif self.state.upper() == "V":
            # show the network.
            self.terminal_view(self.network.memory)
        elif self.state.upper() == "R":
            # Run in either DORA mode (DORA run on her own) or user mode (user controls DORA's flow of control).
            go_on = True
            while go_on:
                print("\nRun in (D)ORA controlled mode")
                print("Run in (U)ser controlled mode")
                run_type = input("Run_DORA>")
                if run_type.upper() == "D" or run_type.upper() == "U":
                    go_on = False
                else:
                    print(run_type, " is not an option. Try again...")
            if run_type.upper() == "D":
                # run via the ctrlStruct.
                ctrlStructure = ctrlStruct(self.network, self.parameters, self.write_file)
                for cycle in range(self.parameters["run_cyles"]):
                    ctrlStructure.runCycle(cycle)
                    # if you are on a run cycle mod write_on_iteration, then write to file.
                    if (cycle + 1) % self.parameters["write_on_iteration"] == 0:
                        write_file_name = "batch_run" + str(
                            cycle + 1 + self.parameters["starting_iteration"]
                        )
                        basicRunDORA.write_memory_to_symfile(
                            ctrlStructure.network.memory, write_file_name
                        )
                # and update network based on ctrlStructure.memory.
                self.network = ctrlStructure.network
            else:  # run in user controlled mode.
                # in user controlled mode, user can put stuff in driver/recipient, and pick an operation (retrieve, map, predicate, form new relation, generalization, schema induction).
                print("\n* * * User Controlled Run * * *")
                # allow user to run DORA.
                go_on_run = True
                while go_on_run:
                    print(
                        "\n(R)etrieve; (M)ap; (P)redicate; (F)orm new relation; (G)eneralize; (S)chematize, (B)etween set entropy operations, (W)ithin set entropy operations, (Co)mpression, (C)lear inferences/mappings, (U)pdate names"
                    )
                    print("(Ch)ange Driver/Recipient")
                    print(
                        "(Sw)ap DORA and LISA mode. Currently asDORA is", self.parameters["asDORA"]
                    )
                    print(
                        "(Ig)nore object semantics (a LISA property that only works in LISA mode). Currently ignore_object_semantics is",
                        self.parameters["ignore_object_semantics"],
                    )
                    print("(V)iew the network")
                    print("(E)xit to main Run_Menu")
                    run_command = input("Run_DORA>")
                    if run_command.upper() == "V":
                        self.terminal_view(self.network.memory)
                    elif run_command.upper() == "SW":
                        # swap DORA and LISA mode.
                        if self.parameters["asDORA"]:
                            my_mode = "DORA"
                        else:
                            my_mode = "LISA"
                        print("\nMy mode is currently " + my_mode)
                        print(
                            "To swap LISA/DORA modes, enter (Y)es, or enter any other key to exit"
                        )
                        swap = input("swap>")
                        if swap.upper() == "Y":
                            if self.parameters["asDORA"]:
                                self.parameters["asDORA"] = False
                                self.network.asDORA = False
                            else:
                                self.parameters["asDORA"] = True
                                self.network.asDORA = True
                    elif run_command.upper() == "IG":
                        # try to change the ignore_object_semantics parameter.
                        if self.parameters["ignore_object_semantics"]:
                            self.parameters["ignore_object_semantics"] = False
                            self.network.ingore_object_semantics = False
                        else:
                            # 'ignore_object_semantics' parameter is False, check if you're in LISA mode, if so, change ignore_object_semantics to True, else give an error message indicating that ignore_object_semantics can only be True in LISA mode.
                            if not self.parameters["asDORA"]:
                                self.parameters["ignore_object_semantics"] = True
                                self.network.ignore_object_semantics = True
                            else:
                                print(
                                    "\nasDORA is currently True (i.e., you are in DORA mode). You can only set ignore_object_semantics to True if you are in LISA mode. Please change to LISA mode if you want to make ignore_object_semantics True. \nOK, thanks!\n"
                                )
                    elif run_command.upper() == "U":
                        # update the names of items in memory.
                        self.network.memory = basicRunDORA.update_Names_nil(self.network.memory)
                        print("\nNames updated.")
                    elif run_command.upper() == "C":
                        # clear mappings, madeUnits, inferences, and newSet.
                        self.network.memory = basicRunDORA.reset_inferences(self.network.memory)
                        self.network.memory = basicRunDORA.reset_maker_made_units(
                            self.network.memory
                        )
                        self.network.memory = basicRunDORA.reset_mappings(self.network.memory)
                        self.network.memory = basicRunDORA.update_Names_nil(self.network.memory)
                        self.network.memory = basicRunDORA.indexMemory(self.network.memory)
                        self.network.memory = basicRunDORA.initialize_memorySet(self.network.memory)
                        (
                            self.network.memory.newSet.Ps,
                            self.network.memory.newSet.RBs,
                            self.network.memory.newSet.POs,
                        ) = ([], [], [])
                        print("\nInferences and mapping cleared.")
                    elif run_command.upper() == "CH":
                        # change driver and recipient.
                        go_on_cdr = True
                        while go_on_cdr:
                            print("\n(V)iew, driver and recipient")
                            print("view network (M)emory")
                            print("(L)ist all items of a particular token")
                            print("(S)wap driver and recipient")
                            print("change (D)river, change (R)ecipient")
                            print(
                                "(A)rbitrarily select an analog from memory and add it to the driver"
                            )
                            print("(CD) to clear driver")
                            print("(CR) to clear recipient")
                            print("(E)xit to Run_Menu")
                            ch_dr_state = input("Run_DORA>")
                            if ch_dr_state.upper() == "V":
                                # show the driver and the recipient.
                                basicRunDORA.DORA_GUI.term_network_display(
                                    self.network.memory, "driver"
                                )
                                basicRunDORA.DORA_GUI.term_network_display(
                                    self.network.memory, "recipient"
                                )
                            elif ch_dr_state.upper() == "M":
                                # show items in memory.
                                basicRunDORA.DORA_GUI.term_network_display(
                                    self.network.memory, "memory"
                                )
                            elif ch_dr_state.upper() == "L":
                                # allow user to list all items by token.
                                go_on_list_tokens = True
                                while go_on_list_tokens:
                                    print("")
                                    token = input("List by (G)roup, (P), (RB), or (PO), or (E)xit>")
                                    if token.upper() == "G":
                                        pass
                                    elif token.upper() == "P":
                                        basicRunDORA.DORA_GUI.display_token_names(
                                            self.network.memory, "P"
                                        )
                                    elif token.upper() == "RB":
                                        basicRunDORA.DORA_GUI.display_token_names(
                                            self.network.memory, "RB"
                                        )
                                    elif token.upper() == "PO":
                                        basicRunDORA.DORA_GUI.display_token_names(
                                            self.network.memory, "PO"
                                        )
                                    elif token.upper() == "E":
                                        go_on_list_tokens = False
                                    else:
                                        print("Sorry, ", token, " is not an option.")
                                        input("Enter any key to try again>")
                            elif ch_dr_state.upper() == "S":
                                # switch the analogs in the driver and the recipient.
                                self.network.memory = swap_driver_recipient(self.network.memory)
                            elif ch_dr_state.upper() == "A":
                                # select an analog from memory at random and add it to the driver.
                                # pick the analog at random.
                                random_analog = random.choice(self.network.memory.analogs)
                                analog_number = self.network.memory.analogs.index(random_analog)
                                # set the tokens in the selected analog to 'driver'.
                                self.network.memory = basicRunDORA.add_tokens_to_set(
                                    self.network.memory, analog_number, "analog", "driver"
                                )
                                self.network.memory = basicRunDORA.findDriverRecipient(
                                    self.network.memory
                                )
                            elif ch_dr_state.upper() == "CD":
                                # clear driver.
                                self.network.memory = basicRunDORA.clearDriverSet(
                                    self.network.memory
                                )
                                self.network.memory = basicRunDORA.findDriverRecipient(
                                    self.network.memory
                                )
                            elif ch_dr_state.upper() == "CR":
                                # clear recipient.
                                self.network.memory = basicRunDORA.clearRecipientSet(
                                    self.network.memory
                                )
                                self.network.memory = basicRunDORA.findDriverRecipient(
                                    self.network.memory
                                )
                            elif ch_dr_state.upper() == "D":
                                # change the driver.
                                go_on_driver = True
                                while go_on_driver:
                                    print("")
                                    top_unit = input(
                                        "Add a (G)roup, (P), (RB), (PO) to driver, or (E)xit>"
                                    )
                                    if top_unit.upper() == "G":
                                        # enter a group and all it's child tokens.
                                        # pass for now.
                                        pass
                                    elif top_unit.upper() == "P":
                                        # enter a P and all it's child tokens.
                                        go_on_P = True
                                        while go_on_P:
                                            # prompt user to enter the number of the P to enter, then put it in driver.
                                            P_number = input(
                                                "Enter the number of the P in memory (or (B)ack up a menu)>"
                                            )
                                            if P_number.upper() != "B":
                                                try:
                                                    P_number = int(P_number) - 1
                                                    self.network.memory = (
                                                        basicRunDORA.add_tokens_to_set(
                                                            self.network.memory,
                                                            P_number,
                                                            "P",
                                                            "driver",
                                                        )
                                                    )
                                                    self.network.memory = (
                                                        basicRunDORA.findDriverRecipient(
                                                            self.network.memory
                                                        )
                                                    )
                                                except:
                                                    print("\n", P_number, " is not a valid number.")
                                            else:
                                                go_on_P = False
                                    elif top_unit.upper() == "RB":
                                        # enter a RB and all it's child tokens.
                                        go_on_RB = True
                                        while go_on_RB:
                                            # prompt user to enter the number of the RB to enter, then put it in driver.
                                            RB_number = input(
                                                "Enter the number of the RB in memory (or (B)ack up a menu)>"
                                            )
                                            if RB_number.upper() != "B":
                                                try:
                                                    RB_number = int(RB_number) - 1
                                                    self.network.memory = (
                                                        basicRunDORA.add_tokens_to_set(
                                                            self.network.memory,
                                                            RB_number,
                                                            "RB",
                                                            "driver",
                                                        )
                                                    )
                                                    self.network.memory = (
                                                        basicRunDORA.findDriverRecipient(
                                                            self.network.memory
                                                        )
                                                    )
                                                except:
                                                    print(
                                                        "\n", RB_number, " is not a valid number."
                                                    )
                                            else:
                                                go_on_RB = False
                                    elif top_unit.upper() == "PO":
                                        # enter a PO.
                                        go_on_PO = True
                                        while go_on_PO:
                                            # prompt user to enter the number of the PO to enter, then put it in driver.
                                            PO_number = input(
                                                "Enter the number of the PO in memory (or (B)ack up a menu)>"
                                            )
                                            if PO_number.upper() != "B":
                                                try:
                                                    PO_number = int(PO_number) - 1
                                                    self.network.memory = (
                                                        basicRunDORA.add_tokens_to_set(
                                                            self.network.memory,
                                                            PO_number,
                                                            "PO",
                                                            "driver",
                                                        )
                                                    )
                                                    self.network.memory = (
                                                        basicRunDORA.findDriverRecipient(
                                                            self.network.memory
                                                        )
                                                    )
                                                except:
                                                    print(
                                                        "\n",
                                                        PO_number,
                                                        " that is not a valid number.",
                                                    )
                                            else:
                                                go_on_PO = False
                                    elif top_unit.upper() == "E":
                                        go_on_driver = False
                                    else:
                                        print("\n", top_unit, " is not an option. Try again.")
                            elif ch_dr_state.upper() == "R":
                                # change the recipient.
                                go_on_recipient = True
                                while go_on_recipient:
                                    print("")
                                    top_unit = input(
                                        "Add a (G)roup, (P), (RB), (PO) to recipient, or (E)xit>"
                                    )
                                    if top_unit.upper() == "G":
                                        # enter a group and all it's child tokens.
                                        # pass for now.
                                        pass
                                    elif top_unit.upper() == "P":
                                        # enter a P and all it's child tokens.
                                        go_on_P = True
                                        while go_on_P:
                                            # prompt user to enter the number of the P to enter, then put it in driver.
                                            P_number = input(
                                                "Enter the number of of the P in memory (or (B)ack up a menu)>"
                                            )
                                            if P_number.upper() != "B":
                                                try:
                                                    P_number = int(P_number) - 1
                                                    self.network.memory = (
                                                        basicRunDORA.add_tokens_to_set(
                                                            self.network.memory,
                                                            P_number,
                                                            "P",
                                                            "recipient",
                                                        )
                                                    )
                                                    self.network.memory = (
                                                        basicRunDORA.findDriverRecipient(
                                                            self.network.memory
                                                        )
                                                    )
                                                except:
                                                    print(
                                                        "\n",
                                                        P_number,
                                                        " that is not a valid number.",
                                                    )
                                            else:
                                                go_on_P = False
                                    elif top_unit.upper() == "RB":
                                        # enter a RB and all it's child tokens.
                                        go_on_RB = True
                                        while go_on_RB:
                                            # prompt user to enter the number of the RB to enter, then put it in driver.
                                            RB_number = input(
                                                "Enter the number of the RB in memory (or (B)ack up a menu)>"
                                            )
                                            if RB_number.upper() != "B":
                                                try:
                                                    RB_number = int(RB_number) - 1
                                                    self.network.memory = (
                                                        basicRunDORA.add_tokens_to_set(
                                                            self.network.memory,
                                                            RB_number,
                                                            "RB",
                                                            "recipient",
                                                        )
                                                    )
                                                    self.network.memory = (
                                                        basicRunDORA.findDriverRecipient(
                                                            self.network.memory
                                                        )
                                                    )
                                                except:
                                                    print(
                                                        "\n",
                                                        RB_number,
                                                        " that is not a valid number.",
                                                    )
                                            else:
                                                go_on_RB = False
                                    elif top_unit.upper() == "PO":
                                        # enter a PO.
                                        go_on_PO = True
                                        while go_on_PO:
                                            # prompt user to enter the number of the PO to enter, then put it in driver.
                                            PO_number = input(
                                                "Enter the number of the PO in memory (or (B)ack up a menu)>"
                                            )
                                            if PO_number.upper() != "B":
                                                try:
                                                    PO_number = int(PO_number) - 1
                                                    self.network.memory = (
                                                        basicRunDORA.add_tokens_to_set(
                                                            self.network.memory,
                                                            PO_number,
                                                            "PO",
                                                            "recipient",
                                                        )
                                                    )
                                                    self.network.memory = (
                                                        basicRunDORA.findDriverRecipient(
                                                            self.network.memory
                                                        )
                                                    )
                                                except:
                                                    print(
                                                        "\n",
                                                        PO_number,
                                                        " that is not a valid number.",
                                                    )
                                            else:
                                                go_on_PO = False
                                    elif top_unit.upper() == "E":
                                        go_on_recipient = False
                                    else:
                                        print("\n", top_unit, " is not an option. Try again.\n")
                            elif ch_dr_state.upper() == "E":
                                go_on_cdr = False
                            else:
                                print("\nSorry, ", ch_dr_state, " is not an option.")
                                input("Enter any key to try again>")
                    elif run_command.upper() == "R":
                        # do retrieval.
                        self.network.do_retrieval()
                        # self.network.do_retrieval_v2()
                    elif run_command.upper() == "M":
                        # do map.
                        self.network.do_map()
                    elif run_command.upper() == "B":
                        # do between set entropy operations.
                        self.network.do_entropy_ops_between()
                    elif run_command.upper() == "W":
                        # do within set entropy operations.
                        self.network.do_entropy_ops_within(pred_only=False)
                    elif run_command.upper() == "P":
                        # do predication.
                        # check if predication is ok.
                        pred_ok = basicRunDORA.predication_requirements(self.network.memory)
                        if pred_ok:
                            self.network.do_predication()
                        else:
                            print(
                                "\nThe requirements for predication are not met. \nThere are RBs in the recipient, OR some POs in recipient do not map to POs in driver above threshold(=.8). "
                            )
                            input("Press Enter to return to Run_Menu>")
                    elif run_command.upper() == "F":
                        # do form new relation.
                        # check if formation is ok.
                        form_ok = basicRunDORA.rel_form_requirements(self.network.memory)
                        if form_ok:
                            self.network.do_rel_form()
                        else:
                            print(
                                "\nThe requirements for forming a new relation are not met. \nThere is a P unit in the recipient, OR there are non-mapping RBs in the recipient."
                            )
                            input("Press Enter to return to Run_Menu>")
                    elif run_command.upper() == "G":
                        # do generalization.
                        # check if generalization is ok.
                        gen_ok = basicRunDORA.rel_gen_requirements(self.network.memory)
                        # do generalisation (or don't, if gen_ok is False)
                        if gen_ok:
                            self.network.do_rel_gen()
                        else:
                            print(
                                "\nThe requirements for generalisation are not met. \nThere are no items in the driver that map to a recipient item above threshold(=0.7)."
                            )
                            input("Press Enter to return to Run_Menu>")
                    elif run_command.upper() == "S":
                        # do schematization.
                        # check if schematization is ok.
                        schema_ok = basicRunDORA.schema_requirements(self.network.memory)
                        # do schematisation (or don't, if schema_ok is False)
                        if schema_ok:
                            self.network.do_schematization()
                        else:
                            print(
                                "\nThe requirements for schematisation are not met. \nThere are non-mapping items in driver or recipient."
                            )
                            input("Press Enter to return to Run_Menu>")
                    elif run_command.upper() == "CO":
                        # do compreession.
                        self.network.do_compression()
                    elif run_command.upper() == "E":
                        go_on_run = False
                    else:
                        print("\n", run_command, " is not a valid option.")
        elif self.state.upper() == "D":
            # enter the debugging mode.
            pdb.set_trace()
        elif self.state.upper() == "E":
            print("\nBack to the MainMenu we go!")
        else:
            # user selection is not a valid menu option.
            print(
                "\nUmmm, ",
                self.state,
                " is not a valid choice. Let us try selecting again, shall we...",
            )

    def terminal_view(self, memory):
        # function to view the state the the network.
        # decide if you want states of units, or a view of the network.
        go_on = True
        while go_on:
            print("")
            type_view = input(
                "View network (A)ctivations, (N)etwork state, (M)appings, or (B)ack to Run_Menu>"
            )
            if type_view.upper() == "B":
                go_on = False
            elif type_view.upper() == "A":
                # show activations of driver, recipient, and semantics.
                basicRunDORA.DORA_GUI.simple_term_state_display(memory)
                basicRunDORA.DORA_GUI.term_semantic_state_display(memory)
            elif type_view.upper() == "N":
                go_on_2 = True
                while go_on_2:
                    print("")
                    set_to_view = input("(D)river, (R)ecipient, (M)emory, or (B)ack to view menu>")
                    if set_to_view.upper() == "D":
                        # show driver.
                        basicRunDORA.DORA_GUI.term_network_display(memory, "driver")
                    elif set_to_view.upper() == "R":
                        # show recipient.
                        basicRunDORA.DORA_GUI.term_network_display(memory, "recipient")
                    elif set_to_view.upper() == "M":
                        # show memory.
                        basicRunDORA.DORA_GUI.term_network_display(memory, "memory")
                    elif set_to_view.upper() == "B":
                        go_on_2 = False
                    else:
                        print("\nUmmm, ", set_to_view, " is not a valid choice, try again...\n")
            elif type_view.upper() == "M":
                # show mapping state.
                basicRunDORA.DORA_GUI.term_map_display(memory)
            else:
                print("\nUmmm, ", type_view, " is not an option. Please try again...\n")


# object to perform flow of control for DORA controlled runs.
class ctrlStruct(object):
    def __init__(self, network: basicRunDORA.runDORA, parameters: dict, write_file):
        self.run_order = parameters["run_order"]
        self.parameters = parameters
        self.network = network
        self.write_file = write_file

    # main run function.
    def runCycle(self, cycle):
        # function to run a full run cycle in the run order given in parameters['run_order'].
        # runCycle options: [cdr, cr, selectTokens, r, m, p, f, g, s, co, c, wdr, wn]. See below for details.
        # get all the indeces for the tokens.
        self.network.memory = basicRunDORA.indexMemory(self.network.memory)
        for run_item in self.parameters["run_order"]:
            print(run_item)
            if run_item == "cdr":
                # clear driver and recipient.
                self.network.memory = basicRunDORA.clearDriverSet(self.network.memory)
                self.network.memory = basicRunDORA.clearRecipientSet(self.network.memory)
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
            elif run_item == "cr":
                # clear recipient.
                self.network.memory = basicRunDORA.clearRecipientSet(self.network.memory)
            elif run_item == "selectTokens":
                # randomly select tokens from memory to place into driver.
                # select between 1-3 analogs from memory, and put them in the driver.
                num_analogs = random.choice([1])
                # select randomly from all of memory or bias towards recently learned items.
                if (
                    self.network.recent_analog_bias
                ):  # there is a bias towards recently learned items.
                    for i in range(num_analogs):
                        # select an analog with a bias towards more recent analogs (exact probabilities specified in code below).
                        # select a random number.
                        rand_num = random.random()
                        if rand_num >= 0.7:
                            # select from Ps if available, or RBs if available and no Ps available.
                            if len(self.network.memory.Ps) > 0:
                                # randomly select a P and use that P's analog.
                                myP = random.choice(self.network.memory.Ps)
                                analog = myP.myanalog
                            elif len(self.network.memory.RBs) > 0:
                                # randomly select a RB and use that RB's analog.
                                myRB = random.choice(self.network.memory.RBs)
                                analog = myRB.myanalog
                            else:
                                # select anything from what's there.
                                analog = random.choice(self.network.memory.analogs)
                        # elif rand_num <= .8:
                        #    # select from RBs if available.
                        #    if len(self.network.memory.RBs) > 0:
                        #        # randomly select a RB and use that RB's analog.
                        #        myRB = random.choice(self.network.memory.RBs)
                        #        analog = myRB.myanalog
                        #    else:
                        #        # select anything from what's there.
                        #        analog = random.choice(self.network.memory.analogs)
                        else:
                            # select from memory without bias.
                            analog = random.choice(self.network.memory.analogs)
                        # use the list method .index() to get the location of analog in network.memory.analogs
                        analog_num = self.network.memory.analogs.index(analog)
                        self.network.memory = basicRunDORA.add_tokens_to_set(
                            self.network.memory, analog_num, "analog", "driver"
                        )
                        # if there are only objects, just grab 2.
                        if len(self.network.memory.driver.RBs) == 0:
                            POs = [PO for PO in self.network.memory.POs if PO.set == "driver"]
                            non_driver_POs = []
                            if len(POs) >= 3:
                                non_driver_POs = random.sample(POs, len(POs) - 2)
                            for myPO in non_driver_POs:
                                myPO.set = "memory"
                else:  # there is no bias towards recent items.
                    for i in range(num_analogs):
                        analog = random.choice(self.network.memory.analogs)
                        # use the built in python method .index() to get the location of analog in network.memory.analogs
                        analog_num = self.network.memory.analogs.index(analog)
                        self.network.memory = basicRunDORA.add_tokens_to_set(
                            self.network.memory, analog_num, "analog", "driver"
                        )

                # write what went into the driver into the run_log...

            # elif run_item == 'selectP':
            #    # randomly select Ps from memory to place into driver--but first make sure that there are Ps in memory.
            #    if len(self.network.memory.Ps) > 0:
            #        # select between 1 and 2 Ps. (NOTE: Right now we're defaulting to the same probability of selecting either 1 or 2 Ps. You might want to revisit this decision later.)
            #        num_Ps = random.choice([1,2])
            #        for i in range(num_Ps):
            #            myP = random.choice(self.network.memory.Ps)
            #            token_num = myP.my_index
            #            self.network.memory = basicRunDORA.add_tokens_to_set(self.network.memory, token_num, 'P', 'driver')
            #    else:
            #        print ('\nThere are no Ps in memory to select from.\n')
            # elif run_item == 'selectRB':
            #    # randomly select RBs from memory to place into the driver.
            #    # first check if there are RBs without Ps in memory--but first make sure that there are RBs in memory.
            #    RB_to_pick = False
            #    if len(self.network.memory.RBs) > 0:
            #        for myRB in self.network.memory.RBs:
            #            if len(myRB.myParentPs) == 0:
            #                RB_to_pick = True
            #                break
            #    if RB_to_pick:
            #        # select between 1 and 4 RBs. (NOTE: Right now we're defaulting to the same probability of selecting either 1, 2, 3, or 4 RBs. You might want to revisit this decision later.)
            #        num_RBs = random.choice([1,2,3,4])
            #        for i in range(num_RBs):
            #            go_on_sel_RB = True
            #            while go_on_sel_RB:
            #                myRB = random.choice(self.network.memory.RBs)
            #                if len(myRB.myParentPs) == 0:
            #                    go_on_sel_RB = False
            #            token_num = myRB.my_index
            #            self.network.memory = basicRunDORA.add_tokens_to_set(self.network.memory, token_num, 'RB', 'driver')
            #    else:
            #        print ('\nThere are no RBs without Ps to select from.\n')
            # elif run_item == 'selectPO':
            #    # randomly select a PO from memory to place into the driver.
            #    # first check if there are POs without RBs in memory.
            #    PO_to_pick = False
            #    for myPO in self.network.memory.POs:
            #        if len(myPO.myRBs) == 0:
            #            PO_to_pick = True
            #            break
            #    if PO_to_pick:
            #        go_on_sel_PO = True
            #        while go_on_sel_PO:
            #            myPO = random.choice(self.network.memory.POs)
            #            if len(myPO.myRBs) == 0:
            #                go_on_sel_PO = False
            #        token_num = myPO.my_index
            #        self.network.memory = basicRunDORA.add_tokens_to_set(self.network.memory, token_num, 'PO', 'driver')
            #    else:\nThere are no POs without RBs to select from.\n'
            elif run_item == "r":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # check if can do retrieval (there are POs in the driver).
                if len(self.network.memory.driver.POs) > 0:
                    # do retrieval.
                    # self.network.do_retrieval()
                    self.network.do_retrieval_v2()
                else:
                    print("Could not do retrieval on cycle ", cycle, "\n")

                # print (results of retrieval to run_log... )

            elif run_item == "w":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # perform within group entropy operations.
                self.network.do_entropy_ops_within(pred_only=False)
            elif run_item == "wp":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # perform within group entropy operations for preds only.
                self.network.do_entropy_ops_within(pred_only=True)

                # print (results of entropy ops to run_log... )

            elif run_item == "m":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # check if can do map (there are POs in driver and recipient).
                if (len(self.network.memory.driver.POs) > 0) and (
                    len(self.network.memory.recipient.POs) > 0
                ):
                    # do map.
                    self.network.do_map()
                else:
                    print("Could not do mapping on cycle ", cycle, "\n")

                # print (results of mapping to run_log... )

            elif run_item == "b":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # perform between group entropy operations.
                self.network.do_entropy_ops_between()
            elif run_item == "p":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # check if can do predication (function taken from basicRunDORA).
                pred_check = basicRunDORA.predication_requirements(self.network.memory)
                if pred_check:
                    # do predication.
                    self.network.do_predication()
                else:
                    print("Could not do predication on cycle ", cycle, "\n")

                # print (results of predication to run_log... )

            elif run_item == "s":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # check if can do schematization (there are POs in driver and recipient.
                if (len(self.network.memory.driver.POs) > 0) and (
                    len(self.network.memory.recipient.POs) > 0
                ):
                    # check if schematisation is OK, and if so, do schematization.
                    schema_ok = basicRunDORA.schema_requirements(self.network.memory)
                    if schema_ok:
                        self.network.do_schematization()
                else:
                    print("Could not do schematization on cycle ", cycle, "\n")

                # print (results of schematisation to run_log... )

            elif run_item == "f":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # check if can do form new relation (function taken from basicRunDORA).
                rel_form_check = basicRunDORA.rel_form_requirements(self.network.memory)
                if rel_form_check:
                    # do form new relation.
                    self.network.do_rel_form()
                else:
                    print("Could not do form-new-relation on cycle ", cycle, "\n")

                # print (results of form relation to run_log... )

            elif run_item == "g":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # check if can do generalization (function taken from basicRunDORA).
                yes_rel_gen = basicRunDORA.rel_gen_requirements(self.network.memory)
                if yes_rel_gen:
                    # do generalization.
                    self.network.do_rel_gen()
                else:
                    print("Could not do relational generalization on cycle ", cycle, "\n")
            elif run_item == "co":
                self.network.memory = basicRunDORA.findDriverRecipient(self.network.memory)
                # do compression.
                self.network.do_compression()
            elif run_item == "c":
                # clear all mapping and madeUnit fields and also clear driver, recipient, and newSet.
                self.network.memory = basicRunDORA.reset_inferences(self.network.memory)
                self.network.memory = basicRunDORA.reset_maker_made_units(self.network.memory)
                self.network.memory = basicRunDORA.reset_mappings(self.network.memory)
                # self.memory = basicRunDORA.update_Names_nil(self.memory)
                self.network.memory = basicRunDORA.indexMemory(self.network.memory)
                self.network.memory = basicRunDORA.initialize_memorySet(self.network.memory)
                (
                    self.network.memory.newSet.Ps,
                    self.network.memory.newSet.RBs,
                    self.network.memory.newSet.POs,
                ) = ([], [], [])
                print("(Driver and recipient units cleared on cycle ", str(cycle) + ")\n")
            elif run_item == "cl":
                # do a limited clear (madeUnits and inferences and newSet).
                self.network.memory = basicRunDORA.reset_inferences(self.network.memory)
                self.network.memory = basicRunDORA.reset_maker_made_units(self.network.memory)
                (
                    self.network.memory.newSet.Ps,
                    self.network.memory.newSet.RBs,
                    self.network.memory.newSet.POs,
                ) = ([], [], [])
                print("(Limited clear: newSet items cleared on cycle ", str(cycle) + ")\n")
            elif run_item == "wdr":
                # write the current state of the driver and recipient to the output file.
                write_dr(self.network.memory, self.write_file, cycle)
            elif run_item == "wn":
                # write the current state of the network to the output file.
                write_network(self.network.memory, self.write_file, cycle)


########################
###    FUNCTIONS.    ###
########################
# function to write the state of the driver and recipient to an output file.
def write_dr(memory, write_file, cycle):
    # write DORA_GUI.term_network_display for driver, recipient, and newSet, and the DORA_GUI.term_map_display to write_file.
    # first write the term_network_display.
    # for each item in the driver, write its name and show the unit in the recipient it most maps to and the mapping weight.
    map_heading = "*** MAPPING RESULTS FROM CYCLE " + str(cycle) + " ***"
    write_file.write("\n")
    memory = basicRunDORA.get_max_map_units(memory)
    for myP in memory.driver.Ps:
        if myP.max_map_unit:
            P_string = (
                "P: "
                + myP.name
                + " -- "
                + myP.max_map_unit.name
                + " -- mapping_weight="
                + str(myP.max_map)
            )
        else:
            P_string = "P: " + myP.name + " -- " + "NONE" + " -- mapping_weight=" + str(myP.max_map)
        write_file.write(P_string)
        write_file.write("\n")
    for myRB in memory.driver.RBs:
        if myRB.max_map_unit:
            RB_string = (
                "RB: "
                + myRB.name
                + " -- "
                + myRB.max_map_unit.name
                + " -- mapping_weight="
                + str(myRB.max_map)
            )
        else:
            RB_string = (
                "RB: " + myRB.name + " -- " + "NONE" + " -- mapping_weight=" + str(myRB.max_map)
            )
        write_file.write(RB_string)
        write_file.write("\n")
    for myPO in memory.driver.POs:
        if myPO.max_map_unit:
            PO_string = (
                "PO: "
                + myPO.name
                + " -- "
                + myPO.max_map_unit.name
                + " -- mapping_weignt="
                + str(myPO.max_map)
            )
        else:
            PO_string = (
                "PO: " + myPO.name + " -- " + "NONE" + " -- mapping_weignt=" + str(myPO.max_map)
            )
        write_file.write(PO_string)
        write_file.write("\n")
    # now write the term_map_display.
    write_file.write("\n")
    term_heading = "*** DRIVER/RECIPIENT STATE FROM CYCLE " + str(cycle) + " ***"
    write_file.write(term_heading)
    write_file.write("\n")
    write_file.write("DRIVER:\n")
    P_counter = 0
    for myP in memory.driver.Ps:
        P_counter += 1
        # print (my name, then info for each of my RBs.)
        write_file.write("\n")
        term_write_P(myP, P_counter, write_file)
    # draw each RB that has no Ps above it.
    RB_counter = 0
    for myRB in memory.driver.RBs:
        RB_counter += 1
        # if that RB has no Ps above it (i.e., myRB.myParentPs is empty), then draw it.
        term_write_RB(myRB, RB_counter, write_file)
    # for draw each PO that has no RBs.
    PO_counter = 0
    for myPO in memory.driver.POs:
        PO_counter += 1
        # if that PO has no RBs (i.e., myPO.myRBs is empty), then draw it.
        term_write_PO(myPO, PO_counter, write_file)
    write_file.write("\n")
    write_file.write("RECIPIENT:\n")
    P_counter = 0
    for myP in memory.recipient.Ps:
        P_counter += 1
        # print (my name, then info for each of my RBs.)
        write_file.write("\n")
        term_write_P(myP, P_counter, write_file)
    # draw each RB that has no Ps above it.
    RB_counter = 0
    for myRB in memory.recipient.RBs:
        RB_counter += 1
        # if that RB has no Ps above it (i.e., myRB.myParentPs is empty), then draw it.
        term_write_RB(myRB, RB_counter, write_file)
    # for draw each PO that has no RBs.
    PO_counter = 0
    for myPO in memory.recipient.POs:
        PO_counter += 1
        # if that PO has no RBs (i.e., myPO.myRBs is empty), then draw it.
        term_write_PO(myPO, PO_counter, write_file)


# basically, write DORA_GUI.term_network_display for memory to write_file.
def write_network(memory, write_file, cycle):
    # basically, write DORA_GUI.term_network_display for memory to write_file.
    net_heading = "*** NETWORK STATE FROM CYCLE " + str(cycle) + " ***"
    write_file.write("MEMORY:\n")
    P_counter = 0
    for myP in memory.Ps:
        P_counter += 1
        # print (my name, then info for each of my RBs.)
        term_write_P(myP, P_counter, write_file)
    # draw each RB that has no Ps above it.
    RB_counter = 0
    for myRB in memory.RBs:
        RB_counter += 1
        # if that RB has no Ps above it (i.e., myRB.myParentPs is empty), then draw it.
        term_write_RB(myRB, RB_counter, write_file)
    # for draw each PO that has no RBs.
    PO_counter = 0
    for myPO in memory.POs:
        PO_counter += 1
        # if that PO has no RBs (i.e., myPO.myRBs is empty), then draw it.
        term_write_PO(myPO, PO_counter, write_file)


# function to write P and all its tokens to a file.
def term_write_P(myP, counter, write_file):
    for myRB in myP.myRBs:
        RB_string = myRB.name + "-- Pred_name: " + myRB.myPred[0].name + " ("
        for link in myRB.myPred[0].mySemantics:
            RB_string = RB_string + link.mySemantic.name + ", "
        # now print (the name of the object or child P serving as the argument of the myRB.)
        if len(myRB.myObj) > 0:
            RB_string = RB_string + ") -- Obj_name:" + myRB.myObj[0].name + " ("
            for link in myRB.myObj[0].mySemantics:
                RB_string = RB_string + link.mySemantic.name + ", "
            RB_string += ")"
        elif len(myRB.myChildP) > 0:
            RB_string = RB_string + ") -- PROP_name:" + myRB.myChildP[0].name + " "
        write_file.write(RB_string)
        write_file.write("\n")


# function to write a RB and all its tokens to a file.
def term_write_RB(myRB, counter, write_file):
    if len(myRB.myParentPs) == 0:
        RB_string = (
            "RB " + str(counter) + "." + myRB.name + "-- Pred_name: " + myRB.myPred[0].name + " ("
        )
        for link in myRB.myPred[0].mySemantics:
            RB_string = RB_string + link.mySemantic.name + ", "
        # now print (the name of the object or child P serving as the argument of the myRB.)
        if len(myRB.myObj) > 0:
            RB_string = RB_string + ") -- Obj_name:" + myRB.myObj[0].name + " ("
            for link in myRB.myObj[0].mySemantics:
                RB_string = RB_string + link.mySemantic.name + ", "
            RB_string += ")"
        elif len(myRB.myChildP) > 0:
            RB_string = RB_string + ") -- PROP_name:" + myRB.myChildP[0].name + " "
        RB_string += ")"
        write_file.write(RB_string)
        write_file.write("\n")


# function to write a PO to a file.
def term_write_PO(myPO, counter, write_file):
    if len(myPO.myRBs) == 0:
        PO_string = "PO " + str(counter) + ". -- Obj_name: " + myPO.name + " ("
        for link in myPO.mySemantics:
            PO_string = PO_string + link.mySemantic.name + ", "
        PO_string += ")"
        write_file.write(PO_string)
        write_file.write("\n")


# function to swap the contents of driver and recipient.
def swap_driver_recipient(memory):
    # for every unit in the driver, set its state to 'recipient', and vise versa.
    for group in memory.driver.Groups:
        group.set = "recipient"
    for myP in memory.driver.Ps:
        myP.set = "recipient"
    for myRB in memory.driver.RBs:
        myRB.set = "recipient"
    for myPO in memory.driver.POs:
        myPO.set = "recipient"
    for group in memory.recipient.Groups:
        group.set = "driver"
    for myP in memory.recipient.Ps:
        myP.set = "driver"
    for myRB in memory.recipient.RBs:
        myRB.set = "driver"
    for myPO in memory.recipient.POs:
        myPO.set = "driver"
    # update the driver and recipient sets.
    memory = basicRunDORA.findDriverRecipient(memory)
    # return memory.
    return memory


##############################################################################
###########################        MAIN BODY        ##########################
##############################################################################
mainmenu = MainMenu()
while mainmenu.state != "Q":
    mainmenu.show_menu()
    mainmenu.execute_mainmenu()
