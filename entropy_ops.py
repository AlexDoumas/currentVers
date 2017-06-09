# entropy same/diff/more/less.
# operations for DORA's same/different/more/less detection using simple entropy. Find instances of same/different and more/less using entropy.
# Basic idea (same/diff): For same/different, compare or over-lay the two representations. Create a DORAese sematnic signal (i.e., shared units have greater activation than unshared units). Calculate the error of the DORAese semantic pattern to a pattern with no entropy (i.e., all the active semantics have activation of 1.0). The extent of the error is a measure of difference, with low (or zero) error corresponding to 'same', and higher error corresponding to 'different'.
# Basic idea (more/less): For more/less the idea is very similar to same/diff. If you have two instances coded with magnitude, and the magnitude corresponds to a level of neural firing (more firing for more magnitude), identifying more and less is simply comparing or over-laying the two representations of magnitude, and computing an error signal. The higher the error signal the greater the difference, and the item that is over-activated by the error signal (i.e., the error signal shows too much activation) is the 'more' item, and the under-activated item (i.e., the error signal shows too little activation) is the 'less' item.

# imports.
import dataTypes
import operator
import pdb

# function to calculate over-all same/diff from entropy.
def ent_overall_same_diff(semantic_array):
    # check semantic array and calculate a similarity score as ratio of unshared to total features. 
    error_array = []
    act_array = []
    for semantic in semantic_array:
        # if activation is greater than 0.1, add activation to act_array and add 1.0 to error_array. 
        if semantic.act > 0.1:
            act_array.append(semantic.act)
            error_array.append(1.0)
    # calcuate the error by subtracting act_array from error_array.
    # NOTE: You can do this operation either with numpy (turning the lists into arrays) or with map and operator.
    #a_error_array = numpy.array(error_array)
    #a_act_array = numpy.array(act_array)
    #diff_array = a_error_array - a_act_array
    diff_array = list(map(operator.sub, error_array, act_array))
    sum_diff = sum(diff_array)
    sum_act = sum(act_array)
    similarity_ratio = float(sum_diff)/float(sum_act)
    # return the similarity_ratio.
    return similarity_ratio

# function to learn tunings to the similarity_ratio output above. Takes as input a list of similarity_ratios to learn tunings for, an argument, num_nodes, indicating the number of nodes the network should have, and an argument, tune_precision, indicating how precise the tunings should become.
def learn_similarity_tunings(similarity_ratios, num_nodes, tune_precision):
    # make a network of num_nodes.
    simNet = dataTypes.similarityNet()
    winning_nodes = []
    for i in range(num_nodes):
        simNet.nodes.append(dataTypes.basicSimNode())
    # run the similarity network.
    # set gamma and delta.
    gamma, delta = 0.3, 0.1
    for similarity_ratio in similarity_ratios:
        go_on = True
        while go_on:
            # update the inputs of all nodes.
            simNet.update_inputs(similarity_ratio)
            # for DEBUGGING.
            #for node in simNet.nodes:
            #    print str(node.input)
            # update the activations of all nodes.
            simNet.update_acts(gamma, delta)
            # tune the winning node.
            simNet.tune_network(similarity_ratio)
            # if the tuning on the winning node (i.e., the range of that node's threshold) is less than tune_precision, set go_on flag to False, and move to the next similarity_ratio to train.
            # find the winning_node.
            high_act = 0.0
            winning_node = None
            for node in simNet.nodes:
                if node.act > high_act:
                    high_act = node.act
                    winning_node = node
            # check the precision of the tuning for that node.
            if winning_node:
                # for DEBUGGING.
                print 'sim_ratio=',str(similarity_ratio)
                print 'high_act=',str(high_act)
                print 'winning_node=',str(simNet.nodes.index(winning_node))
                print ''
                if (winning_node.threshold[1]-winning_node.threshold[0]) <= tune_precision:
                    go_on = False
                    winning_nodes.append(winning_node)
    # return the similarityNetwork.
    return simNet, winning_nodes

# function that calculates specific same/diff semantics from entropy.
def ent_specific_semantics_same_diff(semantics):
    # take in a semantic array, check it, and return a list of all shared features (semantics with activations near 1; the same stuff), and a list of all unshared features (semantics with activations near .5; the different stuff).
    # initialise empty arrays for shared and unshared semantics.
    shared = []
    unshared = []
    # iterate semantics, and put any semantics with act >= 0.9 in shared, and any sematnics with act between 0.4 and 0.6 in unshared.
    for semantic in semantics:
        if semantic.act >= 0.9:
            shared.append(semantic)
        elif semantic.act >= 0.4 and semantic.act <= 0.6:
            unshared.append(semantic)
    # return the shared and unshared arrays.
    return shared, unshared

# function that specifies to which PO each unshared semantic is most strongly connected.
def which_semantic_unshared(myPO1, myPO2, unshared):
    # take in the 2 POs, PO1 and PO2, and the list of unshared semantics. return two lists of unshared semantics, the first specifying the unshared semantics that are most strongly connected to PO1, and the second specifying the unshared semantics that are most strongly connected to PO2.
    # initialise empty arrays, one for the unshared semantics belonging to PO1 and the other for the unshared semantics belonging to PO2.
    unsharedPO1 = []
    unsharedPO2 = []
    # iterate through the unshared semantics and sort them into the arrays for PO1 and PO2.
    for semantic in unshared:
        for link in semantic.myPOs:
            if myPO1 is link.myPO:
                if link.weight >= 0.4 and semantic.act <= 0.6:
                    unsharedPO1.append(semantic)
            elif myPO2 is link.myPO:
                if link.weight >= 0.4 and semantic.act <= 0.6:
                    unsharedPO2.append(semantic)
    # return the arrays of sorted unshared semantics.
    return unsharedPO1, unsharedPO2

# function calculates more/less/same from two codes of extent based on entropy and competion.
def ent_magnitudeMoreLessSame(extent1, extent2):
    # take two representations of extent, and have them compete.
    # first build a simple entropyNet with the extents as lower-level nodes.
    entropyNet = dataTypes.entropyNet()
    for i in range(max(extent1,extent2)):
        new_sem = dataTypes.basicEntNode(False, True, [])
        entropyNet.inputs.append(new_sem)
    # and now make an object attached to each extent as a higher-level (output) node.
    # first make the nodes.
    extent_node1 = dataTypes.basicEntNode(True, False, [])
    extent_node2 = dataTypes.basicEntNode(True, False, [])
    entropyNet.outputs = [extent_node1, extent_node2]
    # connect each node to the correct extent semantics.
    for i in range(extent1):
        # create a link between the ith input unit and extent_node1.
        new_connection = dataTypes.basicLink(extent_node1, entropyNet.inputs[i], 1.0)
        entropyNet.connections.append(new_connection) 
        # add the connection to the higher and lower nodes it links.
        extent_node1.connections.append(new_connection)
        entropyNet.inputs[i].connections.append(new_connection)
    for i in range(extent2):
        # create a link between the ith input unit and extent_node2.
        new_connection = dataTypes.basicLink(extent_node2, entropyNet.inputs[i], 1.0)
        entropyNet.connections.append(new_connection)
        # add the connection to the higher and lower nodes it links.
        extent_node2.connections.append(new_connection)
        entropyNet.inputs[i].connections.append(new_connection)
    # set activations of all extent nodes to 1.0.
    for node in entropyNet.inputs:
        node.act = 1.0
    # until the network settles (i.e., only one output node is active for 3 iterations), keep running.
    unsettled = 0
    iterations = 0
    # set gamma and delta.
    gamma, delta = 0.3, 0.1
    delta_outputs_previous = 0.0
    settled = 0
    while settled < 3:
        # update the inputs to the output units.
        for node in entropyNet.outputs:
            node.clear_input()
            node.update_input(entropyNet)
        # update the activations of the output units.
        for node in entropyNet.outputs:
            node.update_act(gamma, delta)
        # FOR DEBUGGING: print inputs and outputs of all nodes.
        #pdb.set_trace()
        print 'iteration = ', iterations
        print 'INPUTS'
        for node in entropyNet.inputs:
            print node.input, ', ', node.act
        print 'OUTPUTS'
        for node in entropyNet.outputs:
            print node.input, ', ', node.act
        # check for settling. if the delta_outputs has not changed, add 1 to settled, otherwise, clear unsettled.
        delta_outputs = entropyNet.outputs[0].act-entropyNet.outputs[1].act
        print delta_outputs == delta_outputs_previous
        print settled
        print ''
        if delta_outputs == delta_outputs_previous:
            settled += 1
        else:
            settled = 0
        delta_outputs_previous = delta_outputs
        iterations += 1
    # the active output node is 'more', and the inactive output node is 'less', or the two extents are equal.
    if entropyNet.outputs[0].act > entropyNet.outputs[1].act:
        more = extent1
        less = extent2
        same_flag = False
    elif entropyNet.outputs[0].act < entropyNet.outputs[1].act:
        more = extent2
        less = extent1
        same_flag = False
    else: # the two extents are equal.
        more = 'NONE'
        less = 'NONE'
        same_flag = True
    # return more, less, a flag indicating whether the values are the same (called same_flag), and the number of iterations to settling.
    return more, less, same_flag, iterations




